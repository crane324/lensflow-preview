"""
微信聊天记录导入器

支持两种模式：
1. 自动模式：微信桌面版运行中 → PyWxDump 直接从内存提取密钥 → 解密数据库
2. 手动模式：用户通过微信自带导出/第三方工具导出 → 解析文件

使用方式：
    importer = WeChatImporter()

    # 自动模式（需要微信运行）
    chats = importer.auto_import(target_wxid="wxid_xxx")

    # 手动模式
    chats = importer.import_from_file("exported_chat.txt")
"""
import os
import json
import logging
import sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# WeChat 数据目录
WECHAT_DATA_DIRS = [
    os.path.expandvars(r"%USERPROFILE%\Documents\WeChat Files"),
    os.path.expandvars(r"%USERPROFILE%\Documents\WeChat Files"),
    os.path.expandvars(r"%APPDATA%\Tencent\WeChat"),
]


@dataclass
class WeChatContact:
    """微信联系人"""
    wxid: str = ""
    nickname: str = ""
    remark: str = ""  # 备注名
    avatar_path: str = ""


@dataclass
class WeChatChat:
    """一个聊天会话"""
    contact: WeChatContact = field(default_factory=WeChatContact)
    messages: List[Dict] = field(default_factory=list)
    message_count: int = 0
    source: str = ""  # auto / file


class WeChatImporter:
    """微信聊天记录导入器"""

    def __init__(self):
        self.wx_data_dir = None
        self.user_wxid = None

    # ==================== 自动检测 ====================

    def detect_wechat_data(self) -> Optional[str]:
        """自动检测微信数据目录"""
        for base_dir in WECHAT_DATA_DIRS:
            if not os.path.exists(base_dir):
                continue
            # 查找用户目录（wxid_xxx 格式）
            for entry in os.listdir(base_dir):
                full_path = os.path.join(base_dir, entry)
                if os.path.isdir(full_path) and entry.startswith("wxid_"):
                    msg_dir = os.path.join(full_path, "Msg")
                    if os.path.exists(msg_dir):
                        self.wx_data_dir = full_path
                        self.user_wxid = entry
                        logger.info(f"检测到微信数据: {full_path}")
                        return full_path
        return None

    def list_contacts_from_db(self) -> List[WeChatContact]:
        """从 MicroMsg.db 读取联系人列表（需要先解密）"""
        if not self.wx_data_dir:
            self.detect_wechat_data()
        if not self.wx_data_dir:
            return []

        contacts = []
        micro_msg_path = os.path.join(self.wx_data_dir, "Msg", "MicroMsg.db")

        # 尝试直接读取（如果已解密）
        if os.path.exists(micro_msg_path):
            try:
                conn = sqlite3.connect(micro_msg_path)
                cursor = conn.cursor()
                # 尝试读取联系人表
                cursor.execute("SELECT UserName, NickName, Remark FROM Contact LIMIT 50")
                for row in cursor.fetchall():
                    contacts.append(WeChatContact(
                        wxid=row[0] or "",
                        nickname=row[1] or "",
                        remark=row[2] or "",
                    ))
                conn.close()
            except Exception as e:
                logger.debug(f"MicroMsg.db 读取失败（可能已加密）: {e}")

        return contacts

    # ==================== PyWxDump 自动模式 ====================

    def auto_import(self, target_wxid: str = None, max_messages: int = 2000) -> Optional[WeChatChat]:
        """
        自动模式：通过 PyWxDump 从运行中的微信提取聊天记录

        要求：微信桌面版必须正在运行

        Args:
            target_wxid: 目标联系人的 wxid，为 None 时返回自己的消息
            max_messages: 最大消息数
        """
        try:
            from pywxdump import get_wx_info, get_core_db
        except ImportError:
            logger.error("PyWxDump 未安装，请运行: pip install pywxdump")
            return None

        # Step 1: 获取微信信息
        logger.info("正在获取微信信息...")
        wx_info_list = get_wx_info()

        if not wx_info_list:
            logger.warning("未检测到微信运行，无法使用自动模式")
            logger.warning("请先打开微信桌面版，然后重试")
            return None

        wx_info = wx_info_list[0]
        logger.info(f"检测到微信: {wx_info.get('nickname', '未知')}")

        # Step 2: 获取并解密数据库
        logger.info("正在解密聊天数据库...")
        db_info = get_core_db(wx_info)

        if not db_info:
            logger.error("解密数据库失败")
            return None

        # Step 3: 读取聊天记录
        chat_db_path = db_info.get("chat_db_path") or db_info.get("ChatMsg_db_path")
        if not chat_db_path or not os.path.exists(chat_db_path):
            logger.error("找不到解密后的聊天数据库")
            return None

        messages = self._read_chat_db(chat_db_path, target_wxid, max_messages)

        chat = WeChatChat(
            contact=WeChatContact(
                wxid=target_wxid or self.user_wxid or "",
                nickname=wx_info.get('nickname', ''),
            ),
            messages=messages,
            message_count=len(messages),
            source="auto",
        )

        return chat

    def _read_chat_db(
        self, db_path: str, target_wxid: str = None, max_msgs: int = 2000
    ) -> List[Dict]:
        """读取解密后的聊天数据库"""
        messages = []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"数据库表: {tables}")

            # 尝试常见的聊天表名
            chat_tables = [t for t in tables if 'chat' in t.lower() or 'msg' in t.lower()]
            if not chat_tables:
                chat_tables = tables  # 回退到所有表

            for table in chat_tables:
                try:
                    # 根据 target_wxid 过滤
                    if target_wxid:
                        cursor.execute(
                            f"SELECT * FROM [{table}] WHERE talker LIKE ? LIMIT ?",
                            (f"%{target_wxid}%", max_msgs)
                        )
                    else:
                        cursor.execute(
                            f"SELECT * FROM [{table}] LIMIT ?",
                            (max_msgs,)
                        )

                    columns = [desc[0] for desc in cursor.description] if cursor.description else []

                    for row in cursor.fetchall():
                        msg_dict = dict(row)

                        # 提取关键字段
                        msg = {
                            "sender": "",
                            "content": "",
                            "timestamp": "",
                            "type": "text",
                        }

                        # 尝试匹配常见字段名
                        for key in msg_dict:
                            key_lower = key.lower()
                            if key_lower in ("talker", "sender", "fromuser", "speaker"):
                                msg["sender"] = str(msg_dict[key])
                            elif key_lower in ("content", "message", "msg", "text"):
                                msg["content"] = str(msg_dict[key])
                            elif key_lower in ("createtime", "time", "timestamp", "createtime"):
                                msg["timestamp"] = str(msg_dict[key])
                            elif key_lower in ("type", "msgtype"):
                                msg["type"] = str(msg_dict[key])

                        if msg["content"]:
                            messages.append(msg)

                except Exception as e:
                    logger.debug(f"读取表 {table} 失败: {e}")

            conn.close()
        except Exception as e:
            logger.error(f"读取数据库失败: {e}")

        # 按时间排序
        messages.sort(key=lambda m: m.get("timestamp", ""))

        # 限制数量
        return messages[:max_msgs]

    # ==================== 手动文件导入 ====================

    def import_from_file(self, file_path: str, encoding: str = "utf-8") -> WeChatChat:
        """
        从导出的文件导入聊天记录

        支持的格式：
        - 微信自带的 .txt 导出
        - 第三方工具导出的 .txt / .json / .html / .csv
        - 纯文本对话
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".json":
            return self._import_json(file_path, encoding)
        elif ext == ".html" or ext == ".htm":
            return self._import_html(file_path, encoding)
        elif ext == ".csv":
            return self._import_csv(file_path, encoding)
        else:
            return self._import_txt(file_path, encoding)  # 默认文本

    def _import_txt(self, file_path: str, encoding: str = "utf-8") -> WeChatChat:
        """导入文本格式"""
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            text = f.read()

        # 使用现有的 chat_parser
        from ..utils.chat_parser import parse_chat, chat_to_analysis_text

        chat_log = parse_chat(text, format="auto")
        analysis_text, speaker = chat_to_analysis_text(chat_log)

        messages = [
            {"sender": m.sender, "content": m.content, "timestamp": m.timestamp or ""}
            for m in chat_log.messages
        ]

        return WeChatChat(
            contact=WeChatContact(nickname=speaker or "用户"),
            messages=messages,
            message_count=len(messages),
            source="file",
        )

    def _import_json(self, file_path: str, encoding: str = "utf-8") -> WeChatChat:
        """导入 JSON 格式（微信/QQ 导出）"""
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            text = f.read()

        from ..utils.chat_parser import parse_chat, chat_to_analysis_text

        chat_log = parse_chat(text, format="wechat_json")
        analysis_text, speaker = chat_to_analysis_text(chat_log)

        messages = [
            {"sender": m.sender, "content": m.content, "timestamp": m.timestamp or ""}
            for m in chat_log.messages
        ]

        return WeChatChat(
            contact=WeChatContact(nickname=speaker or "用户"),
            messages=messages,
            message_count=len(messages),
            source="file",
        )

    def _import_html(self, file_path: str, encoding: str = "utf-8") -> WeChatChat:
        """导入 HTML 格式（微信备份工具导出）"""
        from html.parser import HTMLParser

        class WeChatHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.messages = []
                self.current_sender = ""
                self.current_content = ""
                self.in_message = False
                self.in_content = False

            def handle_data(self, data):
                data = data.strip()
                if not data:
                    return
                # 简单的启发式解析
                self.current_content += data + "\n"

        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            html = f.read()

        # 简单清洗：去除 HTML 标签
        import re
        clean = re.sub(r'<[^>]+>', '\n', html)
        clean = re.sub(r'\n{3,}', '\n\n', clean)

        from ..utils.chat_parser import parse_chat
        chat_log = parse_chat(clean, format="txt")

        messages = [
            {"sender": m.sender, "content": m.content, "timestamp": m.timestamp or ""}
            for m in chat_log.messages
        ]

        return WeChatChat(
            contact=WeChatContact(nickname="用户"),
            messages=messages,
            message_count=len(messages),
            source="file",
        )

    def _import_csv(self, file_path: str, encoding: str = "utf-8") -> WeChatChat:
        """导入 CSV 格式"""
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            text = f.read()

        from ..utils.chat_parser import parse_chat
        chat_log = parse_chat(text, format="csv")

        messages = [
            {"sender": m.sender, "content": m.content, "timestamp": m.timestamp or ""}
            for m in chat_log.messages
        ]

        return WeChatChat(
            contact=WeChatContact(nickname="用户"),
            messages=messages,
            message_count=len(messages),
            source="file",
        )

    # ==================== 导出为分析文本 ====================

    def to_analysis_text(self, chat: WeChatChat) -> str:
        """将聊天记录转换为 AI 分析用的文本格式"""
        lines = []
        for msg in chat.messages:
            sender = msg.get("sender", "未知")
            content = msg.get("content", "")
            time_str = msg.get("timestamp", "")

            prefix = f"[{time_str}] " if time_str else ""
            lines.append(f"{prefix}{sender}: {content}")

        return "\n".join(lines)
