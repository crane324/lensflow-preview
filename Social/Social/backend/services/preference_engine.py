"""
Preference Engine — 匹配偏好分析服务

功能：
1. 根据用户人格和自述，分析理想型偏好
2. 推断匹配兼容性类型
3. 推荐最适合的虚拟场景
"""
import logging
from typing import Dict, Any, List

from ..models import MatchPreference, Gender, PersonalityProfile, UserProfile
from ..prompts.persona_analysis import (
    PREFERENCE_ANALYSIS_SYSTEM_PROMPT,
)
from .llm_service import get_llm_service

logger = logging.getLogger(__name__)


class PreferenceEngine:
    """匹配偏好引擎"""

    def __init__(self):
        self.llm = get_llm_service()

    def analyze_preferences(
        self,
        user_profile: UserProfile,
        personality: PersonalityProfile,
        explicit_preferences: Dict[str, Any] = None,
    ) -> MatchPreference:
        """
        综合分析用户偏好

        Args:
            user_profile: 用户自述画像
            personality: AI 分析的人格画像
            explicit_preferences: 用户明确表达的偏好（如问卷第3阶段的回答）
        """
        # Step 1: 基于规则的推断
        rule_based = self._rule_based_inference(user_profile, personality)

        # Step 2: LLM 深度分析
        llm_based = self._llm_preference_analysis(user_profile, personality, explicit_preferences)

        # Step 3: 合并
        merged = self._merge_preferences(rule_based, llm_based, explicit_preferences)
        return merged

    def _rule_based_inference(
        self,
        user_profile: UserProfile,
        personality: PersonalityProfile,
    ) -> Dict[str, Any]:
        """基于规则的偏好推断"""
        preferred_personality = []
        preferred_style = []

        # 大五人格规则
        bf = personality.big_five

        # 高外向性的人 → 通常适合高外向或中等外向的伴侣
        if bf.extraversion >= 7.0:
            preferred_personality.append("外向活跃")
        elif bf.extraversion <= 3.0:
            preferred_personality.append("温和安静")
            preferred_personality.append("善于倾听")

        # 高开放性 → 喜欢同样开放的伴侣
        if bf.openness >= 7.0:
            preferred_personality.append("有趣有创意")
        elif bf.openness <= 3.0:
            preferred_personality.append("踏实稳重")

        # 高尽责性 → 看重对方的责任感
        if bf.conscientiousness >= 7.0:
            preferred_personality.append("自律上进")
        elif bf.conscientiousness <= 3.0:
            preferred_personality.append("随和包容")

        # 情绪稳定性
        if bf.neuroticism >= 7.0:
            preferred_personality.append("情绪稳定")
            preferred_personality.append("有安全感")

        # 社交策略推断
        ss = personality.social_strategy
        if ss.initiation == "主动":
            preferred_style.append("积极回应")  # 主动者需要响应者
        elif ss.initiation == "被动":
            preferred_style.append("主动引导")  # 被动者需要引导者

        # 价值观推断
        v = personality.values
        value_map = {
            "事业成就型": ["有上进心", "独立"],
            "家庭归属型": ["顾家", "温柔"],
            "自由探索型": ["有趣", "开放包容"],
            "稳定安全型": ["靠谱", "踏实"],
            "成长学习型": ["有思想", "热爱生活"],
            "社会贡献型": ["有同理心", "有格局"],
        }
        for val in v.primary_values:
            if val in value_map:
                preferred_personality.extend(value_map[val])

        # 去重
        preferred_personality = list(dict.fromkeys(preferred_personality))
        preferred_style = list(dict.fromkeys(preferred_style))

        # 场景推荐
        cs = personality.conversation_style
        tp = personality.topic_preferences

        scenario_scores = {"校园空间": 50, "职场空间": 50, "沙滩空间": 50, "深海空间": 50}

        if cs.primary_style in ["文艺清新", "感性温暖"]:
            scenario_scores["校园空间"] += 20
        if cs.primary_style in ["正经严肃", "理性逻辑"]:
            scenario_scores["职场空间"] += 20
        if cs.primary_style in ["幽默风趣", "接地气"]:
            scenario_scores["沙滩空间"] += 20
        if cs.primary_style in ["文艺清新"] or bf.openness >= 7.0:
            scenario_scores["深海空间"] += 20

        # 话题兴趣影响场景
        if any(t in str(tp.top_interests) for t in ["旅行", "户外", "运动"]):
            scenario_scores["沙滩空间"] += 15
        if any(t in str(tp.top_interests) for t in ["科技", "读书", "职场"]):
            scenario_scores["职场空间"] += 15
        if any(t in str(tp.top_interests) for t in ["电影", "音乐", "艺术"]):
            scenario_scores["校园空间"] += 15
        if any(t in str(tp.top_interests) for t in ["游戏", "动漫", "科幻"]):
            scenario_scores["深海空间"] += 15

        sorted_scenarios = sorted(scenario_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "preferred_personality": preferred_personality[:6],
            "preferred_style": preferred_style[:4],
            "suggested_scenarios": [s[0] for s in sorted_scenarios[:2]],
        }

    def _llm_preference_analysis(
        self,
        user_profile: UserProfile,
        personality: PersonalityProfile,
        explicit_preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """LLM 深度偏好分析"""
        # 构建用户信息摘要
        user_info = f"""
用户基本信息：
- 昵称：{user_profile.nickname}
- 性别：{user_profile.gender.value if user_profile.gender else '未知'}
- 年龄：{user_profile.age or '未知'}
- 职业：{user_profile.occupation or '未知'}
- 兴趣爱好：{', '.join(user_profile.hobbies)}
- 自我介绍：{user_profile.self_description or '未提供'}
- 交友目的：{user_profile.relationship_goal.value if user_profile.relationship_goal else '未知'}

AI 人格分析：
- 大五人格：开放性{personality.big_five.openness}/10, 尽责性{personality.big_five.conscientiousness}/10, 外向性{personality.big_five.extraversion}/10, 宜人性{personality.big_five.agreeableness}/10, 情绪稳定性{10 - personality.big_five.neuroticism}/10
- 对话风格：{personality.conversation_style.primary_style}
- 情绪基线：{personality.emotion_profile.baseline}
- 社交策略：{personality.social_strategy.initiation}型
- 话题偏好：{', '.join(personality.topic_preferences.top_interests[:5])}
- 价值观：{', '.join(personality.values.primary_values[:4])}
- 人格总结：{personality.summary}
"""

        if explicit_preferences:
            user_info += f"\n用户明确表达的偏好：\n{explicit_preferences}"

        try:
            result = self.llm.chat_with_json_output(
                system_prompt=PREFERENCE_ANALYSIS_SYSTEM_PROMPT,
                user_prompt=user_info,
                temperature=0.4,
            )
            return result
        except Exception as e:
            logger.error(f"LLM 偏好分析失败: {e}")
            return {}

    def _merge_preferences(
        self,
        rule_based: Dict[str, Any],
        llm_based: Dict[str, Any],
        explicit: Dict[str, Any] = None,
    ) -> MatchPreference:
        """合并规则推断和 LLM 分析的结果"""
        # 合并特质（LLM 优先，规则补充）
        preferred_personality = llm_based.get("preferred_personality", [])
        for trait in rule_based.get("preferred_personality", []):
            if trait not in preferred_personality:
                preferred_personality.append(trait)

        preferred_style = llm_based.get("preferred_style", [])
        for style in rule_based.get("preferred_style", []):
            if style not in preferred_style:
                preferred_style.append(style)

        dealbreakers = llm_based.get("dealbreakers", ["不尊重人", "冷暴力", "欺骗"])

        important_values = llm_based.get("important_values", [])

        # 场景推荐
        scenarios = llm_based.get("suggested_scenarios", [])
        if not scenarios:
            scenarios = rule_based.get("suggested_scenarios", ["校园空间", "沙滩空间"])

        description = llm_based.get("ideal_date_description", "")

        # 从 explicit 中提取
        preferred_gender = None
        if explicit:
            gender_str = explicit.get("preferred_gender", "")
            if gender_str == "男":
                preferred_gender = Gender.MALE
            elif gender_str == "女":
                preferred_gender = Gender.FEMALE

        return MatchPreference(
            preferred_gender=preferred_gender,
            age_range=(20, 40),
            preferred_personality=preferred_personality[:8],
            preferred_style=preferred_style[:5],
            dealbreakers=dealbreakers[:5],
            important_values=important_values[:6],
            description=description,
        )

    def quick_preference_from_answers(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        快速从第3阶段问卷答案中提取偏好线索
        不需要完整的 PersonaProfile
        """
        preferences = {}

        # 沟通需求 → 沟通风格偏好
        comm = answers.get("communication_need", "")
        if "高频" in comm:
            preferences["preferred_style"] = ["主动联系", "喜欢分享"]
        elif "适度" in comm:
            preferences["preferred_style"] = ["有分寸感", "尊重边界"]
        elif "空间" in comm:
            preferences["preferred_style"] = ["独立", "不黏人"]

        # 冲突处理 → 兼容性推断
        conflict = answers.get("conflict_style", "")
        if "沟通解决" in conflict:
            preferences["important_values"] = ["愿意沟通", "情绪成熟"]
        elif "冷静" in conflict:
            preferences["important_values"] = ["有耐心", "不逼迫"]

        # 生活价值观
        life_value = answers.get("life_value", "")
        value_trait_map = {
            "事业有成": ["有上进心", "事业稳定"],
            "家庭和睦": ["顾家", "温柔体贴"],
            "自由自在": ["有趣", "不束缚对方"],
            "平淡安稳": ["靠谱", "情绪稳定"],
        }
        for k, v in value_trait_map.items():
            if k in life_value:
                preferences.setdefault("preferred_personality", []).extend(v)

        # 最重要的品质
        partner_core = answers.get("partner_core", "")
        if partner_core:
            preferences.setdefault("preferred_personality", []).append(partner_core.strip())

        return preferences
