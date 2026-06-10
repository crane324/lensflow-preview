"""
Social - 虚拟AI相亲系统
FastAPI 主入口

数字人生成模块 API：
- POST /api/persona/analyze-chat      上传聊天记录 → 人格分析
- POST /api/persona/upload-file       上传聊天文件（支持 txt/json/csv/html）
- GET  /api/wechat/status             检测微信运行状态
- POST /api/wechat/auto-import        一键导入微信聊天记录
- POST /api/persona/analyze-photo     上传照片分析人格
- GET  /api/persona/questionnaire     获取问卷（分阶段）
- POST /api/persona/submit-answers    提交问卷回答
- POST /api/persona/analyze-preferences  分析匹配偏好
- POST /api/persona/generate          生成完整数字人档案
- GET  /api/persona/{id}             查看数字人档案
"""
import logging
import uuid
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import APP_CONFIG
from .models import (
    PersonaProfile, PersonaResponse, UserProfile,
    ChatAnalysisRequest, ProfileUpdateRequest, QuestionnaireResponse,
)
from .services.llm_service import get_llm_service, reset_llm_service
from .services.persona_analyzer import PersonaAnalyzer
from .services.profile_builder import ProfileBuilder
from .services.preference_engine import PreferenceEngine
from .prompts.persona_analysis import build_persona_prompt

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ========== FastAPI 应用 ==========

app = FastAPI(
    title=APP_CONFIG["title"],
    version=APP_CONFIG["version"],
    description=APP_CONFIG["description"],
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 服务实例（懒加载） ==========

_persona_store: dict[str, PersonaProfile] = {}  # 简易内存存储


def get_analyzer() -> PersonaAnalyzer:
    return PersonaAnalyzer()


def get_profile_builder() -> ProfileBuilder:
    return ProfileBuilder()


def get_preference_engine() -> PreferenceEngine:
    return PreferenceEngine()


# ========== API 路由 ==========

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": APP_CONFIG["version"]}


# ========== 微信相关 ==========

@app.get("/api/wechat/status")
async def wechat_status():
    """
    检测微信状态

    返回：
    - wechat_running: 微信桌面版是否在运行
    - data_detected: 是否检测到微信数据目录
    - can_auto_import: 是否可以自动导入
    """
    result = {
        "wechat_running": False,
        "data_detected": False,
        "can_auto_import": False,
        "message": "",
        "help": "",
    }

    # 检查微信数据目录
    from .utils.wechat_importer import WeChatImporter
    importer = WeChatImporter()
    data_dir = importer.detect_wechat_data()

    if data_dir:
        result["data_detected"] = True
        result["message"] = f"检测到微信数据: {data_dir}"

    # 检查微信是否运行
    try:
        from pywxdump import get_wx_info
        wx_info = get_wx_info()
        if wx_info:
            result["wechat_running"] = True
            result["can_auto_import"] = True
            result["message"] = f"微信正在运行，已检测到 {len(wx_info)} 个账号"
        else:
            result["message"] = "微信未运行，请先打开微信桌面版"
            result["help"] = "打开电脑微信（不是小程序），然后刷新此页面再试"
    except Exception as e:
        result["message"] = "无法检测微信状态，请确保微信桌面版已打开"
        result["help"] = "如果微信已打开，请尝试重启微信后重试"

    return result


@app.post("/api/wechat/auto-import")
async def wechat_auto_import(max_messages: int = Form(default=3000)):
    """
    一键导入微信聊天记录

    前提：微信桌面版必须正在运行
    """
    from .utils.wechat_importer import WeChatImporter

    importer = WeChatImporter()

    # 尝试自动导入
    chat = importer.auto_import(max_messages=max_messages)

    if chat is None:
        raise HTTPException(
            status_code=400,
            detail="自动导入失败。请确保：\n1. 微信桌面版正在运行\n2. 微信已登录\n3. 不是通过商店版/小程序打开的微信"
        )

    if chat.message_count == 0:
        raise HTTPException(
            status_code=400,
            detail="未读取到聊天记录。数据库可能为空或解密后无有效消息"
        )

    # 转换为分析文本
    analysis_text = importer.to_analysis_text(chat)

    # 进行分析
    analyzer = get_analyzer()
    personality, metadata = analyzer.analyze(analysis_text, chat_format="txt")

    persona_id = str(uuid.uuid4())[:8]
    persona = PersonaProfile(id=persona_id, personality=personality)
    _persona_store[persona_id] = persona

    logger.info(f"微信导入+分析完成: {chat.message_count}条消息, 置信度={personality.confidence:.0%}")

    return PersonaResponse(
        success=True,
        persona=persona,
        message=f"✅ 成功导入 {chat.message_count} 条微信消息，人格分析置信度 {personality.confidence:.0%}",
        next_step="填写基础信息问卷，补充你的个人资料",
    )


# ---------- Step 1: 聊天记录分析 ----------

@app.post("/api/persona/analyze-chat", response_model=PersonaResponse)
async def analyze_chat(request: ChatAnalysisRequest):
    """
    上传聊天记录文本，进行人格分析
    """
    if not request.chat_text.strip():
        raise HTTPException(status_code=400, detail="聊天记录不能为空")

    try:
        analyzer = get_analyzer()
        personality, metadata = analyzer.analyze(
            chat_text=request.chat_text,
            chat_format=request.chat_format,
        )

        persona_id = str(uuid.uuid4())[:8]
        persona = PersonaProfile(id=persona_id, personality=personality)
        _persona_store[persona_id] = persona

        logger.info(
            f"聊天分析完成: id={persona_id}, "
            f"消息数={metadata.get('total_messages', 0)}, "
            f"置信度={personality.confidence}"
        )

        return PersonaResponse(
            success=True,
            persona=persona,
            message=f"人格分析完成！分析了 {metadata.get('total_messages', 0)} 条消息，置信度 {personality.confidence:.0%}",
            next_step="填写基础信息问卷，补充你的个人资料",
        )

    except Exception as e:
        logger.error(f"聊天分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.post("/api/persona/upload-file", response_model=PersonaResponse)
async def upload_chat_file(file: UploadFile = File(...)):
    """
    上传聊天记录文件（支持 txt, json, csv, html）

    自动检测格式并解析
    """
    # 检查文件类型
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    allowed = {".txt", ".json", ".csv", ".html", ".htm", ".log"}

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}。支持的格式: {', '.join(allowed)}"
        )

    # 读取文件
    content = await file.read()

    # 尝试解码
    text = None
    for encoding in ["utf-8", "gbk", "gb2312", "gb18030", "latin-1"]:
        try:
            text = content.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if text is None:
        raise HTTPException(status_code=400, detail="无法解码文件，请确认文件编码为 UTF-8 或 GBK")

    # 使用 WeChatImporter 解析文件
    from .utils.wechat_importer import WeChatImporter
    importer = WeChatImporter()

    # 保存临时文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=ext, delete=False, encoding="utf-8") as f:
        f.write(text)
        tmp_path = f.name

    try:
        chat = importer.import_from_file(tmp_path)
        analysis_text = importer.to_analysis_text(chat)

        # 分析
        analyzer = get_analyzer()
        personality, metadata = analyzer.analyze(analysis_text, chat_format="txt")

        persona_id = str(uuid.uuid4())[:8]
        persona = PersonaProfile(id=persona_id, personality=personality)
        _persona_store[persona_id] = persona

        logger.info(f"文件导入完成: {filename}, {chat.message_count}条消息")

        return PersonaResponse(
            success=True,
            persona=persona,
            message=f"✅ 成功导入 {filename}，共 {chat.message_count} 条消息。分析置信度 {personality.confidence:.0%}",
            next_step="填写基础信息问卷，补充你的个人资料",
        )
    finally:
        os.unlink(tmp_path)


@app.post("/api/persona/analyze-photo", response_model=PersonaResponse)
async def analyze_photo(file: UploadFile = File(...)):
    """
    上传照片分析人格

    利用多模态 AI 分析：
    - 自拍风格（表情、角度、滤镜使用）
    - 照片内容偏好（风景/美食/人物/宠物）
    - 视觉人格线索
    """
    # 检查文件类型
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    allowed = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的图片格式: {ext}。支持的格式: {', '.join(allowed)}"
        )

    # 读取图片并转为 base64
    import base64
    content = await file.read()

    # 限制大小（5MB）
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")

    base64_image = base64.b64encode(content).decode("utf-8")
    mime_type = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif",
        ".webp": "image/webp", ".bmp": "image/bmp",
    }.get(ext, "image/jpeg")

    # 调用多模态 LLM 分析
    llm = get_llm_service()

    system_prompt = """你是一位资深的心理学家和视觉分析师。
请根据用户上传的照片，从心理学角度分析其人格特质和风格偏好。

分析维度：
1. 视觉风格：照片的色调、构图、滤镜使用
2. 内容偏好：照片中的场景类型（自拍/风景/美食/宠物/社交等）
3. 情绪表达：表情、姿态所传达的情绪
4. 人格线索：从视觉元素推断的可能性格特质
5. 生活方式：照片反映的生活状态和兴趣

输出 JSON：
{
  "visual_style": {"tone": "暖色调/冷色调/自然", "composition": "描述", "filter_usage": "频繁/适中/很少"},
  "content_type": "自拍/风景/美食/社交/其他",
  "emotional_expression": "开心/平静/酷/忧郁/其他",
  "personality_clues": ["线索1", "线索2"],
  "lifestyle_hints": "描述",
  "confidence": 0.7
}"""

    try:
        # 注意：deepseek-chat 支持图片，使用 OpenAI 兼容格式
        result_text = llm.client.chat.completions.create(
            model=llm.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请分析这张照片中反映的人格特质和风格偏好。"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        raw_output = result_text.choices[0].message.content
        import json
        # 清理
        raw_output = raw_output.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]

        photo_analysis = json.loads(raw_output.strip())

        return PersonaResponse(
            success=True,
            persona=None,
            message=f"照片分析完成！风格：{photo_analysis.get('visual_style', {}).get('tone', '未知')}，"
                    f"内容：{photo_analysis.get('content_type', '未知')}",
            next_step="照片分析可作为辅助参考，建议同时上传聊天记录获得更准确的人格画像",
        )

    except Exception as e:
        logger.error(f"照片分析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"照片分析失败: {str(e)}")


# ---------- Step 2: 问卷系统 ----------

@app.get("/api/persona/questionnaire")
async def get_questionnaire(
    persona_id: Optional[str] = None,
    stage: int = 1,
):
    """获取问卷（分阶段）"""
    builder = get_profile_builder()

    existing_info = {}
    if persona_id and persona_id in _persona_store:
        persona = _persona_store[persona_id]
        existing_info = builder.get_collected_info_summary(
            persona.user_profile,
            persona.personality.model_dump() if persona.personality.confidence > 0 else None,
        )

    questionnaire = builder.get_stage_questions(stage=stage, existing_info=existing_info)
    return questionnaire


@app.post("/api/persona/submit-answers", response_model=PersonaResponse)
async def submit_answers(response: QuestionnaireResponse):
    """提交问卷回答"""
    answers = response.answers
    stage = int(answers.get("_stage", "1"))
    persona_id = answers.get("_persona_id", "")

    builder = get_profile_builder()
    user_profile = builder.build_profile_from_answers(answers)

    if persona_id and persona_id in _persona_store:
        persona = _persona_store[persona_id]
    else:
        persona_id = str(uuid.uuid4())[:8]
        persona = PersonaProfile(id=persona_id)

    existing = persona.user_profile
    for field in ["nickname", "gender", "age", "occupation", "education", "city", "hobbies", "self_description", "relationship_goal"]:
        new_val = getattr(user_profile, field, None)
        if new_val and new_val != getattr(existing, field, None):
            setattr(existing, field, new_val)

    persona.user_profile = existing
    _persona_store[persona_id] = persona

    if stage == 1:
        next_step = "接下来是几个个性化的问题，让我更好地了解你"
        next_stage = 2
    elif stage == 2:
        next_step = "最后几个深度问题，帮你精准匹配"
        next_stage = 3
    else:
        next_step = "问卷完成！现在可以分析你的匹配偏好了"
        next_stage = None

    return PersonaResponse(
        success=True,
        persona=persona,
        message=f"第{stage}阶段回答已保存！",
        next_step=f"{next_step}|stage={next_stage}" if next_stage else next_step,
    )


# ---------- Step 3: 偏好分析 ----------

@app.post("/api/persona/analyze-preferences", response_model=PersonaResponse)
async def analyze_preferences(request: ProfileUpdateRequest):
    """分析匹配偏好"""
    persona_id = getattr(request.user_profile, 'nickname', '')

    persona = None
    for pid, p in _persona_store.items():
        if p.user_profile.nickname == request.user_profile.nickname:
            persona = p
            persona_id = pid
            break

    if not persona:
        persona_id = str(uuid.uuid4())[:8]
        persona = PersonaProfile(id=persona_id)

    if request.user_profile:
        persona.user_profile = request.user_profile

    engine = get_preference_engine()
    explicit = request.match_preference.model_dump() if request.match_preference else None

    match_pref = engine.analyze_preferences(
        user_profile=persona.user_profile,
        personality=persona.personality,
        explicit_preferences=explicit,
    )

    persona.match_preference = match_pref
    _persona_store[persona_id] = persona

    return PersonaResponse(
        success=True,
        persona=persona,
        message="匹配偏好分析完成！",
        next_step="现在可以生成你的完整数字人档案了",
    )


# ---------- Step 4: 生成数字人 ----------

@app.post("/api/persona/generate", response_model=PersonaResponse)
async def generate_persona(data: dict = None):
    """生成完整的数字人档案"""
    persona_id = data.get("persona_id", "") if data else ""

    if not persona_id or persona_id not in _persona_store:
        raise HTTPException(status_code=404, detail="未找到该数字人档案，请先完成前面的步骤")

    persona = _persona_store[persona_id]
    persona_dict = persona.model_dump()

    prompt_input = {
        "big_five": persona_dict["personality"]["big_five"],
        "conversation_style": persona_dict["personality"]["conversation_style"],
        "emotion_profile": persona_dict["personality"]["emotion_profile"],
        "social_strategy": persona_dict["personality"]["social_strategy"],
        "topic_preferences": persona_dict["personality"]["topic_preferences"],
        "values": persona_dict["personality"]["values"],
        "user_profile": persona_dict["user_profile"],
    }

    persona.persona_prompt = build_persona_prompt(prompt_input)
    _persona_store[persona_id] = persona

    return PersonaResponse(
        success=True,
        persona=persona,
        message="🎉 数字人生成完成！",
        next_step="你的数字人已经准备好在虚拟世界中开始约会了！",
    )


# ---------- 查询接口 ----------

@app.get("/api/persona/{persona_id}", response_model=PersonaResponse)
async def get_persona(persona_id: str):
    """获取指定数字人档案"""
    persona = _persona_store.get(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="数字人档案不存在")

    return PersonaResponse(success=True, persona=persona, message="")


@app.get("/api/personas")
async def list_personas():
    """列出所有数字人"""
    return {
        "count": len(_persona_store),
        "personas": [
            {"id": pid, "nickname": p.user_profile.nickname, "created_at": p.created_at.isoformat()}
            for pid, p in _persona_store.items()
        ]
    }


# ========== 静态文件 ==========

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"前端静态文件已挂载: {frontend_path}")


# ========== 启动入口 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
