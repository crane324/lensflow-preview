"""
Profile Builder — 用户画像构建服务

功能：
1. 生成个性化的动态问卷
2. 根据用户回答逐步完善画像
3. 支持分阶段的信息收集

流程：
阶段1: 基础信息（年龄、性别、职业、城市等）
阶段2: 兴趣探索（爱好、生活方式、价值观）
阶段3: 深度挖掘（感情观、期待、深层需求）
"""
import logging
from typing import Dict, Any, List, Optional
import uuid

from ..models import UserProfile, Gender, Education, RelationshipGoal
from ..prompts.persona_analysis import (
    QUESTIONNAIRE_SYSTEM_PROMPT,
    build_questionnaire_prompt,
)
from .llm_service import get_llm_service

logger = logging.getLogger(__name__)


# ========== 预定义的基础问卷（阶段1） ==========

BASIC_QUESTIONS = [
    {
        "id": "nickname",
        "type": "open",
        "question": "请给我一个昵称或者称呼吧～",
        "hint": "你想让大家怎么称呼你？",
        "dimension": "identity",
    },
    {
        "id": "gender",
        "type": "choice",
        "question": "你的性别是？",
        "hint": "",
        "dimension": "identity",
        "options": ["男", "女", "其他"]
    },
    {
        "id": "age",
        "type": "open",
        "question": "你的年龄是？",
        "hint": "输入数字即可，比如 25",
        "dimension": "identity",
    },
    {
        "id": "occupation",
        "type": "open",
        "question": "你的职业是什么？",
        "hint": "比如：产品经理、软件工程师、自由职业...",
        "dimension": "identity",
    },
    {
        "id": "education",
        "type": "choice",
        "question": "你的学历是？",
        "hint": "",
        "dimension": "identity",
        "options": ["高中及以下", "大专", "本科", "硕士", "博士"]
    },
    {
        "id": "city",
        "type": "open",
        "question": "你目前在哪个城市？",
        "hint": "",
        "dimension": "identity",
    },
    {
        "id": "hobbies",
        "type": "open",
        "question": "你平时有什么兴趣爱好？",
        "hint": "可以多写几个，用逗号分隔就好~",
        "dimension": "lifestyle",
    },
    {
        "id": "relationship_goal",
        "type": "choice",
        "question": "你这次来是想找什么样的关系？",
        "hint": "",
        "dimension": "goal",
        "options": ["随缘交友", "认真恋爱", "以结婚为目的"]
    },
    {
        "id": "self_description",
        "type": "open",
        "question": "最后，用一两句话介绍一下你自己吧！",
        "hint": "让大家认识一下真实的你~",
        "dimension": "identity",
    },
]


class ProfileBuilder:
    """用户画像构建器"""

    def __init__(self):
        self.llm = get_llm_service()

    def get_stage_questions(self, stage: int = 1, existing_info: dict = None) -> dict:
        """
        获取某个阶段的问题列表

        Args:
            stage: 阶段编号
                1 - 基础信息
                2 - AI 个性化追问
                3 - 深度探索
            existing_info: 已有信息

        Returns:
            {"stage": 1, "questions": [...], "greeting": "..."}
        """
        if stage == 1:
            return {
                "stage": 1,
                "stage_name": "基础信息",
                "greeting": "你好！让我先简单了解一下你吧 👋",
                "questions": BASIC_QUESTIONS,
            }

        elif stage == 2:
            return self._generate_dynamic_questions(existing_info or {})

        elif stage == 3:
            return self._generate_deep_questions(existing_info or {})

        else:
            return {"stage": stage, "questions": [], "greeting": ""}

    def _generate_dynamic_questions(self, existing_info: dict) -> dict:
        """根据已有信息生成个性化追问（阶段2）"""
        user_prompt = build_questionnaire_prompt(existing_info)

        try:
            result = self.llm.chat_with_json_output(
                system_prompt=QUESTIONNAIRE_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.7,  # 稍高温度让问题更有创意
            )
            result["stage"] = 2
            result["stage_name"] = "个性化探索"
            return result
        except Exception as e:
            logger.error(f"生成动态问题失败: {e}")
            return {
                "stage": 2,
                "stage_name": "个性化探索",
                "greeting": "接下来，让我再多了解你一些吧～",
                "questions": [
                    {
                        "id": "weekend",
                        "type": "open",
                        "question": "你周末通常怎么度过？",
                        "hint": "比如：宅家看剧、约朋友出去玩、运动...",
                        "dimension": "lifestyle",
                    },
                    {
                        "id": "ideal_date",
                        "type": "open",
                        "question": "你心中一次理想的约会是怎样的？",
                        "hint": "地点、活动、氛围...都可以说说",
                        "dimension": "romance",
                    },
                ],
            }

    def _generate_deep_questions(self, existing_info: dict) -> dict:
        """深度探索问题（阶段3）"""
        return {
            "stage": 3,
            "stage_name": "深度探索",
            "greeting": "最后几个深入一点的问题，帮你更精准地匹配～",
            "questions": [
                {
                    "id": "communication_need",
                    "type": "choice",
                    "question": "在一段关系中，你更喜欢怎样的沟通方式？",
                    "options": ["每天高频联系", "保持适度联系", "给彼此足够空间", "看情况而定"],
                    "dimension": "communication",
                },
                {
                    "id": "conflict_style",
                    "type": "choice",
                    "question": "和伴侣产生矛盾时，你通常会？",
                    "options": ["第一时间沟通解决", "先冷静一下再说", "等对方主动", "看事情的严重程度"],
                    "dimension": "conflict",
                },
                {
                    "id": "life_value",
                    "type": "choice",
                    "question": "以下哪个最符合你对「幸福生活」的定义？",
                    "options": [
                        "事业有成，受人尊敬",
                        "家庭和睦，儿女绕膝",
                        "自由自在，探索世界",
                        "平淡安稳，岁月静好",
                    ],
                    "dimension": "values",
                },
                {
                    "id": "partner_core",
                    "type": "open",
                    "question": "你觉得一段关系中，对方最重要的品质是什么？",
                    "hint": "比如：真诚、上进、幽默、温柔...",
                    "dimension": "preference",
                },
                {
                    "id": "extra_wish",
                    "type": "open",
                    "question": "你还有什么想让我了解的？或者对未来的 TA 有什么想说的？",
                    "hint": "随意发挥～",
                    "dimension": "other",
                },
            ],
        }

    def build_profile_from_answers(self, answers: Dict[str, str]) -> UserProfile:
        """
        从用户回答构建 UserProfile 对象

        Args:
            answers: {"question_id": "answer", ...}
        """
        profile = UserProfile()

        # 直接映射
        profile.nickname = answers.get("nickname", "")

        gender_map = {"男": Gender.MALE, "女": Gender.FEMALE, "其他": Gender.OTHER}
        profile.gender = gender_map.get(answers.get("gender", ""), None)

        try:
            profile.age = int(answers.get("age", 0)) or None
        except (ValueError, TypeError):
            profile.age = None

        profile.occupation = answers.get("occupation", "")

        edu_map = {
            "高中及以下": Education.HIGH_SCHOOL,
            "大专": Education.ASSOCIATE,
            "本科": Education.BACHELOR,
            "硕士": Education.MASTER,
            "博士": Education.PHD,
        }
        profile.education = edu_map.get(answers.get("education", ""), None)

        profile.city = answers.get("city", "")

        hobbies_str = answers.get("hobbies", "")
        profile.hobbies = [h.strip() for h in hobbies_str.replace("，", ",").split(",") if h.strip()]

        relationship_map = {
            "随缘交友": RelationshipGoal.CASUAL,
            "认真恋爱": RelationshipGoal.SERIOUS,
            "以结婚为目的": RelationshipGoal.MARRIAGE,
        }
        profile.relationship_goal = relationship_map.get(answers.get("relationship_goal", ""), None)

        profile.self_description = answers.get("self_description", "")

        return profile

    def get_collected_info_summary(self, profile: UserProfile, personality: dict = None) -> dict:
        """
        汇总已收集的信息，用于生成下一阶段的问题
        这是衔接 Profile Builder → AI 动态问卷的关键
        """
        info = {
            "nickname": profile.nickname,
            "gender": profile.gender.value if profile.gender else None,
            "age": profile.age,
            "occupation": profile.occupation,
            "hobbies": profile.hobbies,
            "self_description": profile.self_description,
        }

        if personality:
            cs = personality.get("conversation_style", {})
            tp = personality.get("topic_preferences", {})
            ss = personality.get("social_strategy", {})
            v = personality.get("values", {})

            info.update({
                "conversation_style": cs.get("primary_style", ""),
                "emotional_baseline": personality.get("emotion_profile", {}).get("baseline", ""),
                "social_strategy": f"{ss.get('initiation', '')}型",
                "top_interests": tp.get("top_interests", []),
                "primary_values": v.get("primary_values", []),
            })

        return info
