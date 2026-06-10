"""
数字人数据模型

定义完整的数字人 Profile 结构，包含：
- 基础信息 (Profile)
- 人格特质 (Personality)
- 对话风格 (ConversationStyle)
- 偏好与期待 (Preferences)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


# ========== 枚举类型 ==========

class Gender(str, Enum):
    MALE = "男"
    FEMALE = "女"
    OTHER = "其他"


class Education(str, Enum):
    HIGH_SCHOOL = "高中及以下"
    ASSOCIATE = "大专"
    BACHELOR = "本科"
    MASTER = "硕士"
    PHD = "博士"


class RelationshipGoal(str, Enum):
    CASUAL = "随缘交友"
    SERIOUS = "认真恋爱"
    MARRIAGE = "以结婚为目的"


# ========== 人格特质子模型 ==========

class BigFiveScores(BaseModel):
    """大五人格评分 (1-10)"""
    openness: float = Field(default=5.0, ge=1.0, le=10.0, description="开放性")
    conscientiousness: float = Field(default=5.0, ge=1.0, le=10.0, description="尽责性")
    extraversion: float = Field(default=5.0, ge=1.0, le=10.0, description="外向性")
    agreeableness: float = Field(default=5.0, ge=1.0, le=10.0, description="宜人性")
    neuroticism: float = Field(default=5.0, ge=1.0, le=10.0, description="情绪稳定性")


class ConversationStyle(BaseModel):
    """对话风格"""
    primary_style: str = Field(default="", description="主要风格：幽默/正经/文艺/接地气/理性/感性")
    secondary_styles: List[str] = Field(default_factory=list, description="次要风格")
    sentence_length: str = Field(default="中等", description="句子长度偏好：短/中等/长")
    emoji_usage: str = Field(default="适中", description="表情使用频率：很少/适中/频繁")
    question_frequency: str = Field(default="适中", description="提问频率：很少/适中/频繁")
    humor_type: str = Field(default="", description="幽默类型：冷笑话/自嘲/梗文化/俏皮话/不喜欢幽默")
    description: str = Field(default="", description="对话风格的文字描述")


class EmotionProfile(BaseModel):
    """情绪画像"""
    baseline: str = Field(default="理性冷静", description="情绪基线")
    positive_triggers: List[str] = Field(default_factory=list, description="正面情绪触发点")
    negative_triggers: List[str] = Field(default_factory=list, description="负面情绪触发点")
    expressiveness: float = Field(default=5.0, ge=1.0, le=10.0, description="情绪表达强度")
    optimism_level: float = Field(default=5.0, ge=1.0, le=10.0, description="乐观程度")


class SocialStrategy(BaseModel):
    """社交策略"""
    initiation: str = Field(default="被动", description="主动发起对话：主动/被动/平衡")
    response_style: str = Field(default="", description="回应方式：详实/简洁/反问/延续/终结")
    conflict_handling: str = Field(default="", description="冲突处理：直接面对/委婉回避/理性分析/情绪表达")
    self_disclosure: str = Field(default="适中", description="自我暴露程度：保守/适中/开放")
    description: str = Field(default="", description="社交策略的文字描述")


class TopicPreferences(BaseModel):
    """话题偏好"""
    top_interests: List[str] = Field(default_factory=list, description="最感兴趣的话题 (Top 5)")
    interest_levels: Dict[str, float] = Field(default_factory=dict, description="各话题兴趣度 1-10")
    expertise_areas: List[str] = Field(default_factory=list, description="擅长/专业领域")
    avoided_topics: List[str] = Field(default_factory=list, description="回避的话题")


class Values(BaseModel):
    """价值观"""
    primary_values: List[str] = Field(default_factory=list, description="核心价值观")
    life_priority: str = Field(default="", description="生活优先级：事业/家庭/自由/稳定/成长/贡献")
    relationship_view: str = Field(default="", description="感情观描述")
    description: str = Field(default="", description="价值观文字描述")


# ========== 汇总模型 ==========

class PersonalityProfile(BaseModel):
    """完整人格画像（AI 分析结果）"""
    big_five: BigFiveScores = Field(default_factory=BigFiveScores)
    conversation_style: ConversationStyle = Field(default_factory=ConversationStyle)
    emotion_profile: EmotionProfile = Field(default_factory=EmotionProfile)
    social_strategy: SocialStrategy = Field(default_factory=SocialStrategy)
    topic_preferences: TopicPreferences = Field(default_factory=TopicPreferences)
    values: Values = Field(default_factory=Values)
    summary: str = Field(default="", description="人格画像一句话总结")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="分析置信度（基于数据量）")


class UserProfile(BaseModel):
    """用户基础画像（用户主动填写）"""
    nickname: str = Field(default="", description="昵称")
    gender: Optional[Gender] = Field(default=None, description="性别")
    age: Optional[int] = Field(default=None, ge=18, le=80, description="年龄")
    occupation: Optional[str] = Field(default=None, description="职业")
    education: Optional[Education] = Field(default=None, description="学历")
    city: Optional[str] = Field(default=None, description="所在城市")
    hobbies: List[str] = Field(default_factory=list, description="兴趣爱好")
    self_description: str = Field(default="", description="自我介绍")
    relationship_goal: Optional[RelationshipGoal] = Field(default=None, description="交友目的")


class MatchPreference(BaseModel):
    """匹配偏好（理想型）"""
    preferred_gender: Optional[Gender] = Field(default=None, description="偏好性别")
    age_range: tuple[int, int] = Field(default=(20, 40), description="年龄范围")
    preferred_personality: List[str] = Field(default_factory=list, description="偏好的性格特质")
    preferred_style: List[str] = Field(default_factory=list, description="偏好的沟通风格")
    dealbreakers: List[str] = Field(default_factory=list, description="绝对不要的特质")
    important_values: List[str] = Field(default_factory=list, description="看重的价值观")
    description: str = Field(default="", description="理想型的文字描述")


class PersonaProfile(BaseModel):
    """完整的数字人档案（汇总输出）"""
    # 元数据
    id: str = Field(default="", description="唯一标识")
    created_at: datetime = Field(default_factory=datetime.now)

    # 三个来源
    user_profile: UserProfile = Field(default_factory=UserProfile, description="用户基础信息")
    personality: PersonalityProfile = Field(default_factory=PersonalityProfile, description="AI 人格分析")
    match_preference: MatchPreference = Field(default_factory=MatchPreference, description="匹配偏好")

    # 用于数字人对话的 System Prompt
    persona_prompt: str = Field(default="", description="数字人对话 System Prompt")


# ========== API 请求/响应模型 ==========

class ChatAnalysisRequest(BaseModel):
    """聊天记录分析请求"""
    chat_text: str = Field(..., description="聊天记录文本")
    chat_format: str = Field(default="txt", description="格式：txt/json/wechat")


class ProfileUpdateRequest(BaseModel):
    """用户画像更新请求"""
    user_profile: UserProfile
    match_preference: Optional[MatchPreference] = None


class QuestionnaireResponse(BaseModel):
    """问卷回答"""
    answers: Dict[str, str] = Field(default_factory=dict, description="问题ID->回答")


class PersonaResponse(BaseModel):
    """数字人生成响应"""
    success: bool
    persona: Optional[PersonaProfile] = None
    message: str = ""
    next_step: str = ""  # 引导下一步操作
