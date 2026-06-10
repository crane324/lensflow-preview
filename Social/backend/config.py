"""
Social - 虚拟世界相亲匹配系统
全局配置文件
"""
import os
from typing import Literal

# ========== LLM 配置 ==========
# 支持 OpenAI 兼容接口（OpenAI / DeepSeek / 通义千问 等）
LLM_CONFIG = {
    "provider": os.getenv("LLM_PROVIDER", "openai"),  # openai / deepseek / qwen
    "api_key": os.getenv("OPENAI_API_KEY", "sk-your-api-key-here"),
    "api_base": os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1"),
    "model": os.getenv("LLM_MODEL", "deepseek-chat"),
    "temperature": 0.7,
    "max_tokens": 4096,
}

# DeepSeek 预设
DEEPSEEK_CONFIG = {
    "api_base": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
}

# 通义千问预设
QWEN_CONFIG = {
    "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-plus",
}

def get_llm_config(provider: str = None) -> dict:
    """获取指定供应商的 LLM 配置"""
    config = LLM_CONFIG.copy()

    if provider == "deepseek":
        config.update(DEEPSEEK_CONFIG)
    elif provider == "qwen":
        config.update(QWEN_CONFIG)

    return config


# ========== 人格分析维度 ==========
PERSONA_DIMENSIONS = {
    "conversation_style": {
        "name": "对话风格",
        "options": ["幽默风趣", "正经严肃", "文艺清新", "接地气", "理性逻辑", "感性温暖"]
    },
    "topic_preferences": {
        "name": "话题偏好",
        "categories": ["电影音乐", "美食旅行", "科技数码", "情感关系", "职场发展", "运动健身", "读书学习", "游戏动漫", "社会时事", "生活日常"]
    },
    "emotional_baseline": {
        "name": "情绪基线",
        "options": ["乐观积极", "悲观谨慎", "理性冷静", "敏感细腻", "豁达平和"]
    },
    "social_strategy": {
        "name": "社交策略",
        "options": ["主动外向", "被动慢热", "话痨分享型", "倾听观察型", "平衡适应型"]
    },
    "values": {
        "name": "价值观倾向",
        "options": ["事业成就型", "家庭归属型", "自由探索型", "稳定安全型", "成长学习型", "社会贡献型"]
    }
}

# ========== Big Five 人格维度（参考心理学标准）==========
BIG_FIVE_DIMENSIONS = {
    "openness": {"name": "开放性", "low": "传统保守", "high": "开放好奇"},
    "conscientiousness": {"name": "尽责性", "low": "随性灵活", "high": "自律严谨"},
    "extraversion": {"name": "外向性", "low": "内向安静", "high": "外向活跃"},
    "agreeableness": {"name": "宜人性", "low": "独立强势", "high": "合作友善"},
    "neuroticism": {"name": "情绪稳定性", "low": "情绪稳定", "high": "情绪敏感"}
}

# ========== 应用配置 ==========
APP_CONFIG = {
    "title": "Social - 虚拟AI相亲系统",
    "version": "0.1.0",
    "description": "让数字人先替你在虚拟世界谈一场恋爱",
    "max_chat_upload_size": 10 * 1024 * 1024,  # 10MB
    "supported_chat_formats": ["txt", "json", "csv"],
}
