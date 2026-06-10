"""
聊天记录解析工具

支持的格式：
- 纯文本（TXT）
- 微信导出的 JSON
- CSV 格式

功能：
1. 自动识别格式
2. 提取纯文本对话内容
3. 按说话人切分对话（可选）
4. 统计基础对话元数据
"""
import re
import json
import csv
import io
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """单条消息"""
    sender: str = ""
    content: str = ""
    timestamp: Optional[str] = None

@dataclass
class ChatLog:
    """解析后的聊天记录"""
    messages: List[ChatMessage] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    total_messages: int = 0
    format: str = "txt"


def parse_chat(text: str, format: str = "auto") -> ChatLog:
    """
    解析聊天记录

    Args:
        text: 原始聊天记录文本
        format: 格式 (auto/txt/wechat_json/csv)

    Returns:
        ChatLog 对象
    """
    if format == "auto":
        format = detect_format(text)

    if format == "wechat_json":
        return parse_wechat_json(text)
    elif format == "csv":
        return parse_csv(text)
    else:
        return parse_plain_text(text)


def detect_format(text: str) -> str:
    """自动检测聊天记录格式"""
    text = text.strip()

    # 尝试 JSON
    if text.startswith("{"):
        try:
            data = json.loads(text)
            if isinstance(data, (dict, list)):
                return "wechat_json"
        except json.JSONDecodeError:
            pass

    # 尝试 CSV
    if "," in text[:200] and "\n" in text[:200]:
        lines = text.strip().split("\n")
        if len(lines) >= 2:
            first_line = lines[0].lower()
            if any(kw in first_line for kw in ["sender", "message", "time", "说话人", "内容"]):
                return "csv"

    # 默认纯文本
    return "txt"


def parse_plain_text(text: str) -> ChatLog:
    """
    解析纯文本聊天记录

    支持的常见格式：
    - "用户名: 消息内容"
    - "用户名：消息内容"
    - "【用户名】消息内容"
    - 时间戳 + 用户名 + 内容

    也支持纯对话文本（无明确说话人），作为一个整体处理
    """
    messages = []
    participants_set = set()

    # 尝试匹配 "说话人: 内容" 或 "说话人：内容" 格式
    pattern = re.compile(
        r'(?:^|\n)'
        r'(?:\[?\d{2,4}[-/:]\d{2}[-/:]\d{2}\]?\s*)?'  # 可选时间戳
        r'(?:【?([^\n:：\]]{1,20})[】\]])?[：:]\s*'    # 说话人
        r'(.+?)(?=\n(?:\[?\d{2,4}|【?\w{1,20}[】\]][：:]|$))',  # 内容（到下一个消息头为止）
        re.DOTALL
    )

    matches = pattern.findall(text)

    if matches:
        for speaker, content in matches:
            speaker = speaker.strip() if speaker else "未知"
            content = content.strip()
            if content:
                messages.append(ChatMessage(sender=speaker, content=content))
                participants_set.add(speaker)
    else:
        # 无法解析说话人，将整个文本作为一个人的对话
        # 先尝试简单按行切分
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        if lines:
            # 尝试 "说话人: 内容" 的简单匹配
            simple_pattern = re.compile(r'^(.{1,20})[：:]\s*(.+)$')
            has_speakers = False
            for line in lines:
                m = simple_pattern.match(line)
                if m:
                    speaker, content = m.groups()
                    messages.append(ChatMessage(sender=speaker.strip(), content=content.strip()))
                    participants_set.add(speaker.strip())
                    has_speakers = True

            if not has_speakers:
                # 完全无法识别说话人，整段作为一个对话
                messages = [ChatMessage(sender="用户", content=text.strip())]
                participants_set.add("用户")

    chat_log = ChatLog(
        messages=messages,
        participants=list(participants_set),
        total_messages=len(messages),
        format="txt"
    )
    return chat_log


def parse_wechat_json(text: str) -> ChatLog:
    """
    解析微信导出的 JSON 聊天记录

    微信导出的常见格式：
    {
      "messages": [
        {"sender": "张三", "content": "你好", "time": "2024-01-01 12:00"}
      ]
    }
    """
    messages = []
    participants_set = set()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 尝试修复（微信导出可能有多行 JSON）
        return parse_plain_text(text)

    # 支持多种 JSON 结构
    msg_list = []
    if isinstance(data, list):
        msg_list = data
    elif isinstance(data, dict):
        # 尝试常见字段名
        msg_list = (
            data.get("messages") or
            data.get("message") or
            data.get("msgs") or
            data.get("chatLog") or
            data.get("content") or
            []
        )
        if isinstance(msg_list, str):
            # content 字段可能是纯文本
            return parse_plain_text(msg_list)

    for item in msg_list:
        if isinstance(item, dict):
            sender = (
                item.get("sender") or
                item.get("speaker") or
                item.get("name") or
                item.get("user") or
                item.get("talker") or
                ""
            )
            content = (
                item.get("content") or
                item.get("message") or
                item.get("msg") or
                item.get("text") or
                ""
            )
            timestamp = item.get("time") or item.get("timestamp") or item.get("createTime")
            if content:
                messages.append(ChatMessage(sender=str(sender), content=str(content), timestamp=str(timestamp) if timestamp else None))
                participants_set.add(str(sender))

    chat_log = ChatLog(
        messages=messages,
        participants=list(participants_set),
        total_messages=len(messages),
        format="wechat_json"
    )
    return chat_log


def parse_csv(text: str) -> ChatLog:
    """解析 CSV 格式聊天记录"""
    messages = []
    participants_set = set()

    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        sender = (
            row.get("sender") or row.get("speaker") or
            row.get("说话人") or row.get("name") or ""
        )
        content = (
            row.get("content") or row.get("message") or
            row.get("msg") or row.get("内容") or row.get("text") or ""
        )
        timestamp = row.get("time") or row.get("timestamp") or row.get("时间")

        if content:
            messages.append(ChatMessage(sender=sender, content=content, timestamp=timestamp))
            participants_set.add(sender)

    if not messages:
        # CSV 解析失败，回退到纯文本
        return parse_plain_text(text)

    chat_log = ChatLog(
        messages=messages,
        participants=list(participants_set),
        total_messages=len(messages),
        format="csv"
    )
    return chat_log


def chat_to_analysis_text(chat_log: ChatLog, target_speaker: str = None) -> Tuple[str, Optional[str]]:
    """
    将解析后的聊天记录转换为分析用的文本格式

    Args:
        chat_log: 解析后的聊天记录
        target_speaker: 目标分析对象（说话人）。为 None 时自动选择消息最多的说话人。

    Returns:
        (分析文本, 目标说话人名称)
    """
    if not chat_log.messages:
        return "", None

    # 自动选择说话人
    if target_speaker is None and len(chat_log.participants) > 1:
        # 选择消息数最多的
        from collections import Counter
        speaker_counts = Counter(m.sender for m in chat_log.messages)
        target_speaker = speaker_counts.most_common(1)[0][0]

    # 格式化输出
    lines = []
    for msg in chat_log.messages:
        if target_speaker is None or msg.sender == target_speaker:
            # 标记目标发言
            lines.append(f"[{msg.sender}]: {msg.content}")
        else:
            # 对方发言（提供上下文）
            if target_speaker is not None:
                lines.append(f"[对方-{msg.sender}]: {msg.content}")

    return "\n".join(lines), target_speaker


def extract_metadata(chat_log: ChatLog) -> Dict:
    """提取聊天记录的元数据"""
    if not chat_log.messages:
        return {}

    from collections import Counter
    speaker_counts = Counter(m.sender for m in chat_log.messages)
    total_chars = sum(len(m.content) for m in chat_log.messages)
    avg_msg_length = total_chars / len(chat_log.messages) if chat_log.messages else 0

    return {
        "total_messages": chat_log.total_messages,
        "participants": chat_log.participants,
        "participant_count": len(chat_log.participants),
        "speaker_distribution": dict(speaker_counts.most_common()),
        "total_characters": total_chars,
        "average_message_length": round(avg_msg_length, 1),
        "format": chat_log.format,
    }
