"""
人格分析相关的 LLM Prompt 模板

核心设计理念：
- 采用 Few-shot Prompting：给出分析示例让模型理解输出模式
- Chain-of-Thought：引导模型先分析再打分
- 心理学依据：参考大五人格（Big Five）和社交风格理论
"""
from ..config import PERSONA_DIMENSIONS, BIG_FIVE_DIMENSIONS


# ============================================================
# 1. 聊天记录 → 完整人格分析 Prompt
# ============================================================

PERSONA_ANALYSIS_SYSTEM_PROMPT = """你是一位资深的心理学家和沟通分析专家，擅长通过聊天记录分析人的性格特质和沟通风格。

你的任务：
分析给定的聊天记录，提取该用户的：
1. **大五人格评分**（开放性、尽责性、外向性、宜人性、情绪稳定性，每项1-10分）
2. **对话风格**（幽默风/正经/文艺/接地气等）
3. **话题偏好**（最感兴趣的话题，兴趣程度1-10）
4. **情绪画像**（情绪基线、触发点、表达强度）
5. **社交策略**（主动/被动、自我暴露程度、冲突处理方式）
6. **价值观倾向**（事业/家庭/自由/稳定/成长/贡献）

分析原则：
- 基于实际聊天内容，不要凭空猜测
- 如果聊天记录不足以支撑某个维度的判断，请标记 confidence 较低
- 注意识别用户在不同对话场景下的表现差异
- 给出具体的文本证据来支撑你的判断

输出格式：严格输出 JSON，结构如下：
{
  "big_five": {
    "openness": 6.5,
    "conscientiousness": 5.0,
    "extraversion": 7.0,
    "agreeableness": 6.0,
    "neuroticism": 4.5
  },
  "conversation_style": {
    "primary_style": "幽默风趣",
    "secondary_styles": ["接地气", "理性逻辑"],
    "sentence_length": "中等",
    "emoji_usage": "频繁",
    "question_frequency": "适中",
    "humor_type": "梗文化",
    "description": "该用户喜欢用网络热梗和表情包活跃气氛..."
  },
  "topic_preferences": {
    "top_interests": ["游戏动漫", "科技数码", "电影音乐"],
    "interest_levels": {"游戏动漫": 9, "科技数码": 8, "电影音乐": 7},
    "expertise_areas": ["游戏动漫"],
    "avoided_topics": ["情感关系"]
  },
  "emotion_profile": {
    "baseline": "乐观积极",
    "positive_triggers": ["被认可", "幽默互动"],
    "negative_triggers": ["被误解", "冷场"],
    "expressiveness": 7.5,
    "optimism_level": 7.0
  },
  "social_strategy": {
    "initiation": "主动",
    "response_style": "详实",
    "conflict_handling": "委婉回避",
    "self_disclosure": "适中",
    "description": "该用户是典型的主动型社交者..."
  },
  "values": {
    "primary_values": ["自由探索", "成长学习"],
    "life_priority": "自由",
    "relationship_view": "希望找一个能一起成长的伴侣",
    "description": "该用户重视个人成长和自由度..."
  },
  "summary": "一句话总结该用户的人格画像",
  "confidence": 0.85,
  "evidence": {
    "conversation_style": "见第12行用户使用「笑死」等口语化表达...",
    "big_five_extraversion": "聊天中主动发言占比约70%..."
  }
}
"""


def build_chat_analysis_prompt(chat_text: str, max_length: int = 8000) -> str:
    """构建聊天记录分析的 user prompt"""
    # 截断过长文本
    if len(chat_text) > max_length:
        truncated_text = chat_text[:max_length]
        note = f"\n\n（注意：聊天记录过长，已截取前 {max_length} 字符进行分析，分析置信度可能受影响）"
    else:
        truncated_text = chat_text
        note = ""

    return f"""请分析以下聊天记录，提取该用户的人格特质。

=== 聊天记录开始 ===
{truncated_text}
=== 聊天记录结束 ===
{note}

请严格按 JSON 格式输出分析结果。"""


# ============================================================
# 2. 分段分析合并 Prompt（用于超长聊天记录）
# ============================================================

SEGMENT_MERGE_SYSTEM_PROMPT = """你是一位心理学家，需要将多段分析结果合并为一个统一的人格画像。

合并原则：
- 对同一维度的多个评分取加权平均
- 如果各段分析结果存在矛盾，说明该用户在不同场景下有不同表现
- 综合 confidence 时取各段平均值
- 最终输出格式与单段分析完全一致"""


def build_segment_merge_prompt(segments: list[dict]) -> str:
    """构建分段合并提示"""
    segments_json = []
    for i, seg in enumerate(segments):
        segments_json.append(f"第{i+1}段分析结果:\n{seg}")

    segments_text = "\n\n---\n\n".join(segments_json)

    return f"""请将以下 {len(segments)} 段聊天记录分析结果合并为一个统一的人格画像。

{segments_text}

请输出合并后的完整 JSON 分析结果。"""


# ============================================================
# 3. 数字人对话 System Prompt 生成
# ============================================================

PERSONA_SYSTEM_PROMPT_TEMPLATE = """你是一个名为「{name}」的 AI 数字人，你正在虚拟世界中与一位潜在的约会对象聊天。

## 你的人设
- 性别：{gender}
- 年龄：{age}岁
- 职业：{occupation}

## 你的性格
- 大五人格：开放性{openness}/10，尽责性{conscientiousness}/10，外向性{extraversion}/10，宜人性{agreeableness}/10，情绪稳定性{emotional_stability}/10
- 对话风格：{conversation_style}
- 情绪特点：{emotional_traits}
- 社交方式：{social_traits}

## 你的兴趣
{interests}

## 你的价值观
{values}

## 行为准则
- 用你真实的风格说话，{sentence_style}
- {emoji_rule}
- 每次回复保持在2-5句话，不要过长
- 自然地表达自己的观点和情感
- 可以适当提问，但不要像采访一样连续追问
- 如果遇到不舒服的话题，可以礼貌地表示不想继续

## 当前场景
{scene_description}

现在，开始你们的对话吧。记住：你就是{name}本人，用你的风格自然地聊天。"""


def build_persona_prompt(persona: dict) -> str:
    """根据人格画像生成数字人 System Prompt"""
    bf = persona.get("big_five", {})
    cs = persona.get("conversation_style", {})
    ep = persona.get("emotion_profile", {})
    ss = persona.get("social_strategy", {})
    tp = persona.get("topic_preferences", {})
    v = persona.get("values", {})
    up = persona.get("user_profile", {})

    primary_style = cs.get("primary_style", "自然")
    sentence_style = {
        "短": "回复简洁有力，不喜欢长篇大论",
        "中等": "回复长度适中，根据话题自然调整",
        "长": "喜欢详细表达，回复会较长"
    }.get(cs.get("sentence_length", "中等"), "回复长度适中")

    emoji_usage = cs.get("emoji_usage", "适中")
    emoji_rule = {
        "频繁": "多使用表情符号来增强表达",
        "适中": "适当使用表情符号",
        "很少": "几乎不使用表情符号"
    }.get(emoji_usage, "适当使用表情符号")

    top_interests = tp.get("top_interests", [])
    interests_text = "\n".join([f"- {t}" for t in top_interests[:5]]) if top_interests else "- 广泛兴趣"

    primary_values = v.get("primary_values", [])
    values_text = "、".join(primary_values[:4]) if primary_values else "热爱生活"

    return PERSONA_SYSTEM_PROMPT_TEMPLATE.format(
        name=up.get("nickname", "用户"),
        gender=up.get("gender", "未知"),
        age=up.get("age", "25"),
        occupation=up.get("occupation", "职场人士"),
        openness=bf.get("openness", 5.0),
        conscientiousness=bf.get("conscientiousness", 5.0),
        extraversion=bf.get("extraversion", 5.0),
        agreeableness=bf.get("agreeableness", 5.0),
        emotional_stability=10.0 - bf.get("neuroticism", 5.0),
        conversation_style=f"{primary_style}，{cs.get('description', '')}",
        emotional_traits=f"{ep.get('baseline', '平和')}型，情绪表达强度{ep.get('expressiveness', 5)}/10",
        social_traits=f"{ss.get('initiation', '自然')}发起对话，自我暴露{ss.get('self_disclosure', '适中')}",
        interests=interests_text,
        values=values_text,
        sentence_style=sentence_style,
        emoji_rule=emoji_rule,
        scene_description="{scene_description}",  # 保留为模板变量
    )


# ============================================================
# 4. 动态问卷生成 Prompt
# ============================================================

QUESTIONNAIRE_SYSTEM_PROMPT = """你是一位专业的婚恋顾问和心理学家。你需要根据用户已有的信息，
生成个性化的跟进问题，以更深入地了解用户的人格、偏好和期待。

规则：
1. 生成 5-8 个问题
2. 问题应能补充当前未知的信息维度
3. 问题风格轻松自然，像朋友聊天一样
4. 避免重复询问已有信息
5. 混合开放性和选择题
6. 输出 JSON 格式

输出格式：
{
  "questions": [
    {
      "id": "q1",
      "type": "open",  // open 或 choice
      "question": "你周末通常会怎么度过？",
      "hint": "可以描述一个典型的周末",
      "dimension": "lifestyle",  // 探索维度
      "options": []  // choice 类型时填写
    },
    ...
  ],
  "greeting": "开场问候语",
  "stage": "当前阶段标识"
}

探索维度可包括：lifestyle（生活方式）, values（价值观）, emotional（情感模式）,
social（社交偏好）, romance（感情观）, growth（成长诉求）"""


def build_questionnaire_prompt(existing_info: dict) -> str:
    """根据已有信息生成个性化问卷"""
    info_text = f"""
已收集的信息：
- 昵称：{existing_info.get('nickname', '未知')}
- 性别：{existing_info.get('gender', '未知')}
- 年龄：{existing_info.get('age', '未知')}
- 职业：{existing_info.get('occupation', '未知')}
- 兴趣爱好：{', '.join(existing_info.get('hobbies', [])) or '未知'}
- 自我介绍：{existing_info.get('self_description', '未提供')}

已有人格分析：
- 对话风格：{existing_info.get('conversation_style', '未知')}
- 情绪基线：{existing_info.get('emotional_baseline', '未知')}
- 社交策略：{existing_info.get('social_strategy', '未知')}
- 主要话题：{', '.join(existing_info.get('top_interests', [])) or '未知'}
- 价值观：{', '.join(existing_info.get('primary_values', [])) or '未知'}

请根据以上已有信息，生成 5-8 个个性化问题来深入了解该用户，重点关注尚未明确的维度。
"""

    return info_text


# ============================================================
# 5. 偏好分析 Prompt
# ============================================================

PREFERENCE_ANALYSIS_SYSTEM_PROMPT = """你是一位专业的婚恋匹配顾问。你需要综合分析用户提供的信息，
推断和总结用户的理想型偏好。

分析维度：
1. 从用户自身特质推断互补或相似偏好
2. 从用户明确表达的喜好中提取
3. 从用户的价值观推断兼容类型

输出 JSON 格式：
{
  "preferred_personality": ["幽默", "稳重"],
  "preferred_style": ["主动", "善于倾听"],
  "dealbreakers": ["冷暴力", "不尊重人"],
  "important_values": ["真诚", "有上进心"],
  "compatibility_analysis": "基于你的性格特质，你适合...类型的伴侣",
  "suggested_scenarios": ["校园空间", "职场空间"],
  "ideal_date_description": "你的理想型是..."
}
"""
