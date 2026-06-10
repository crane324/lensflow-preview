"""
LLM 服务抽象层

统一封装 OpenAI / DeepSeek / 通义千问 等接口调用
提供 JSON Schema 约束的结构化输出能力
"""
import json
import logging
from typing import Optional, Dict, Any
from openai import OpenAI

from ..config import get_llm_config

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 调用服务"""

    def __init__(self, provider: str = None):
        """
        初始化 LLM 服务

        Args:
            provider: LLM 供应商 (openai/deepseek/qwen)，默认使用 config 中的配置
        """
        config = get_llm_config(provider)

        self.client = OpenAI(
            api_key=config["api_key"],
            base_url=config["api_base"]
        )
        self.model = config["model"]
        self.temperature = config["temperature"]
        self.max_tokens = config["max_tokens"]

        logger.info(f"LLM 服务初始化: provider={provider or config['provider']}, model={self.model}")

    def chat(
        self,
        messages: list[Dict[str, str]],
        temperature: float = None,
        max_tokens: int = None,
        response_format: Optional[Dict] = None,
    ) -> str:
        """
        通用对话接口

        Args:
            messages: 消息列表 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数（可选）
            max_tokens: 最大输出 token（可选）
            response_format: 响应格式（如 {"type": "json_object"}）

        Returns:
            模型回复文本
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    def chat_with_json_output(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """
        获取结构化的 JSON 输出

        Args:
            system_prompt: 系统提示
            user_prompt: 用户提示
            temperature: 温度（建议较低以确保输出稳定）

        Returns:
            解析后的 JSON 字典
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_output = self.chat(
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )

        # 清理可能的 markdown 代码块包裹
        raw_output = raw_output.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[7:]
        if raw_output.startswith("```"):
            raw_output = raw_output[3:]
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3]
        raw_output = raw_output.strip()

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}\n原始输出: {raw_output[:500]}")
            # 尝试修复：找第一个 { 到最后一个 }
            start = raw_output.find("{")
            end = raw_output.rfind("}")
            if start != -1 and end != -1:
                return json.loads(raw_output[start:end+1])
            raise ValueError(f"无法解析 LLM 输出为 JSON: {raw_output[:200]}")

    def batch_analyze(
        self,
        system_prompt: str,
        user_prompts: list[str],
        temperature: float = 0.3,
    ) -> list[Dict[str, Any]]:
        """
        批量分析（顺序执行，用于长文本分片分析）

        Args:
            system_prompt: 统一的系统提示
            user_prompts: 多个用户提示
            temperature: 温度参数

        Returns:
            多个分析结果的列表
        """
        results = []
        for i, prompt in enumerate(user_prompts):
            logger.info(f"批量分析进度: {i+1}/{len(user_prompts)}")
            result = self.chat_with_json_output(system_prompt, prompt, temperature)
            results.append(result)
        return results


# ========== 工厂函数 ==========

_llm_instance: Optional[LLMService] = None


def get_llm_service(provider: str = None) -> LLMService:
    """获取 LLM 服务单例"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMService(provider)
    return _llm_instance


def reset_llm_service():
    """重置 LLM 服务（切换供应商时使用）"""
    global _llm_instance
    _llm_instance = None
