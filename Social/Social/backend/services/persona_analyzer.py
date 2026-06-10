"""
Persona Analyzer — 人格分析服务

核心功能：
1. 接收聊天记录文本，调用 LLM 进行深度人格分析
2. 支持长文本分段分析 + 结果合并
3. 输出结构化的人格画像（Big Five + 对话风格 + 情绪 + 社交 + 价值观）
"""
import logging
from typing import Optional, Dict, Any

from ..models import PersonalityProfile, BigFiveScores, ConversationStyle
from ..models import EmotionProfile, SocialStrategy, TopicPreferences, Values
from ..prompts.persona_analysis import (
    PERSONA_ANALYSIS_SYSTEM_PROMPT,
    build_chat_analysis_prompt,
    SEGMENT_MERGE_SYSTEM_PROMPT,
    build_segment_merge_prompt,
)
from ..utils.chat_parser import parse_chat, chat_to_analysis_text, extract_metadata
from .llm_service import get_llm_service

logger = logging.getLogger(__name__)

# 单段分析最大字符数（超过此值分段处理）
MAX_SEGMENT_CHARS = 6000


class PersonaAnalyzer:
    """人格分析器"""

    def __init__(self):
        self.llm = get_llm_service()

    def analyze(
        self,
        chat_text: str,
        chat_format: str = "auto",
        target_speaker: str = None,
    ) -> tuple[PersonalityProfile, Dict[str, Any]]:
        """
        主入口：分析聊天记录，生成人格画像

        Args:
            chat_text: 原始聊天记录文本
            chat_format: 格式（auto/txt/wechat_json/csv）
            target_speaker: 目标分析对象。为 None 时自动选择。

        Returns:
            (PersonalityProfile 对象, 聊天元数据)
        """
        # Step 1: 解析聊天记录
        logger.info(f"开始解析聊天记录，格式={chat_format}")
        chat_log = parse_chat(chat_text, format=chat_format)
        metadata = extract_metadata(chat_log)

        if chat_log.total_messages == 0:
            logger.warning("未能从聊天记录中解析出有效消息")
            return PersonalityProfile(confidence=0.0), metadata

        # Step 2: 转换为分析文本
        analysis_text, detected_speaker = chat_to_analysis_text(chat_log, target_speaker)
        if not analysis_text.strip():
            logger.warning("分析文本为空")
            return PersonalityProfile(confidence=0.0), metadata

        # 记录目标对象
        if target_speaker is None:
            target_speaker = detected_speaker
        metadata["target_speaker"] = target_speaker

        logger.info(f"分析目标: {target_speaker}, 消息数: {chat_log.total_messages}")

        # Step 3: 分析（根据文本长度决定是否分段）
        if len(analysis_text) <= MAX_SEGMENT_CHARS:
            result = self._analyze_single_segment(analysis_text)
        else:
            result = self._analyze_multi_segment(analysis_text)

        # Step 4: 转换为 PersonalityProfile 对象
        profile = self._dict_to_profile(result)
        return profile, metadata

    def _analyze_single_segment(self, text: str) -> Dict[str, Any]:
        """单段分析"""
        user_prompt = build_chat_analysis_prompt(text)

        logger.info("执行单段人格分析...")
        result = self.llm.chat_with_json_output(
            system_prompt=PERSONA_ANALYSIS_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.3,
        )
        return result

    def _analyze_multi_segment(self, text: str) -> Dict[str, Any]:
        """分段分析 + 合并"""
        # 按 MAX_SEGMENT_CHARS 切分，但尽量在句末切
        segments = self._split_text(text, MAX_SEGMENT_CHARS)

        logger.info(f"聊天记录较长，分为 {len(segments)} 段分析")

        # 逐段分析
        segment_prompts = [build_chat_analysis_prompt(seg) for seg in segments]

        segment_results = self.llm.batch_analyze(
            system_prompt=PERSONA_ANALYSIS_SYSTEM_PROMPT,
            user_prompts=segment_prompts,
            temperature=0.3,
        )

        # 如果只有一段，直接返回
        if len(segment_results) == 1:
            return segment_results[0]

        # 合并多段结果
        merge_prompt = build_segment_merge_prompt(segment_results)

        logger.info("合并多段分析结果...")
        merged = self.llm.chat_with_json_output(
            system_prompt=SEGMENT_MERGE_SYSTEM_PROMPT,
            user_prompt=merge_prompt,
            temperature=0.3,
        )
        return merged

    def _split_text(self, text: str, max_chars: int) -> list[str]:
        """智能分段：在句号/换行处切分"""
        if len(text) <= max_chars:
            return [text]

        segments = []
        current = ""
        lines = text.split("\n")

        for line in lines:
            if len(current) + len(line) + 1 > max_chars and current:
                segments.append(current.strip())
                current = line
            else:
                current += "\n" + line if current else line

        if current.strip():
            segments.append(current.strip())

        return segments

    def _dict_to_profile(self, raw: Dict[str, Any]) -> PersonalityProfile:
        """将 LLM 输出字典转为 PersonalityProfile 对象"""
        try:
            bf = raw.get("big_five", {})
            cs = raw.get("conversation_style", {})
            tp = raw.get("topic_preferences", {})
            ep = raw.get("emotion_profile", {})
            ss = raw.get("social_strategy", {})
            v = raw.get("values", {})

            profile = PersonalityProfile(
                big_five=BigFiveScores(
                    openness=float(bf.get("openness", 5.0)),
                    conscientiousness=float(bf.get("conscientiousness", 5.0)),
                    extraversion=float(bf.get("extraversion", 5.0)),
                    agreeableness=float(bf.get("agreeableness", 5.0)),
                    neuroticism=float(bf.get("neuroticism", 5.0)),
                ),
                conversation_style=ConversationStyle(
                    primary_style=cs.get("primary_style", ""),
                    secondary_styles=cs.get("secondary_styles", []),
                    sentence_length=cs.get("sentence_length", "中等"),
                    emoji_usage=cs.get("emoji_usage", "适中"),
                    question_frequency=cs.get("question_frequency", "适中"),
                    humor_type=cs.get("humor_type", ""),
                    description=cs.get("description", ""),
                ),
                topic_preferences=TopicPreferences(
                    top_interests=tp.get("top_interests", []),
                    interest_levels=tp.get("interest_levels", {}),
                    expertise_areas=tp.get("expertise_areas", []),
                    avoided_topics=tp.get("avoided_topics", []),
                ),
                emotion_profile=EmotionProfile(
                    baseline=ep.get("baseline", "理性冷静"),
                    positive_triggers=ep.get("positive_triggers", []),
                    negative_triggers=ep.get("negative_triggers", []),
                    expressiveness=float(ep.get("expressiveness", 5.0)),
                    optimism_level=float(ep.get("optimism_level", 5.0)),
                ),
                social_strategy=SocialStrategy(
                    initiation=ss.get("initiation", "被动"),
                    response_style=ss.get("response_style", ""),
                    conflict_handling=ss.get("conflict_handling", ""),
                    self_disclosure=ss.get("self_disclosure", "适中"),
                    description=ss.get("description", ""),
                ),
                values=Values(
                    primary_values=v.get("primary_values", []),
                    life_priority=v.get("life_priority", ""),
                    relationship_view=v.get("relationship_view", ""),
                    description=v.get("description", ""),
                ),
                summary=raw.get("summary", ""),
                confidence=float(raw.get("confidence", 0.5)),
            )
            return profile
        except Exception as e:
            logger.error(f"人格画像转换失败: {e}")
            return PersonalityProfile(confidence=0.0)
