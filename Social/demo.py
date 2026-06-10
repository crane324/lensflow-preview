"""
Social 数字人生成模块 - 命令行演示脚本

无需启动 Web 服务，直接在终端运行完整流程。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.llm_service import LLMService, get_llm_service
from backend.services.persona_analyzer import PersonaAnalyzer
from backend.services.profile_builder import ProfileBuilder
from backend.services.preference_engine import PreferenceEngine
from backend.prompts.persona_analysis import build_persona_prompt


def print_separator(title: str = ""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def step1_chat_analysis():
    """第一步：分析聊天记录"""
    print_separator("Step 1: 聊天记录人格分析")

    # 读取示例聊天记录
    sample_path = os.path.join(os.path.dirname(__file__), "samples", "sample_chat.txt")
    if os.path.exists(sample_path):
        with open(sample_path, "r", encoding="utf-8") as f:
            chat_text = f.read()
    else:
        print("未找到示例文件，请手动输入聊天记录（输入空行结束）：")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        chat_text = "\n".join(lines)

    print(f"\n📝 聊天记录长度: {len(chat_text)} 字符")

    analyzer = PersonaAnalyzer()
    personality, metadata = analyzer.analyze(chat_text)

    print(f"\n📊 分析结果:")
    print(f"   消息数: {metadata.get('total_messages', 0)}")
    print(f"   说话人: {metadata.get('participants', [])}")
    print(f"   分析目标: {metadata.get('target_speaker', '未知')}")
    print(f"   置信度: {personality.confidence:.0%}")

    print(f"\n🧠 大五人格:")
    bf = personality.big_five
    print(f"   开放性: {bf.openness}/10  |  尽责性: {bf.conscientiousness}/10")
    print(f"   外向性: {bf.extraversion}/10  |  宜人性: {bf.agreeableness}/10")
    print(f"   情绪稳定性: {10 - bf.neuroticism}/10")

    print(f"\n💬 对话风格:")
    cs = personality.conversation_style
    print(f"   主要: {cs.primary_style}  |  句子长度: {cs.sentence_length}")
    print(f"   表情: {cs.emoji_usage}  |  幽默: {cs.humor_type}")
    print(f"   描述: {cs.description}")

    print(f"\n🎯 话题偏好:")
    tp = personality.topic_preferences
    print(f"   最感兴趣: {', '.join(tp.top_interests[:5])}")
    print(f"   专业领域: {', '.join(tp.expertise_areas[:3])}")

    print(f"\n💗 情绪画像:")
    ep = personality.emotion_profile
    print(f"   基线: {ep.baseline}  |  乐观度: {ep.optimism_level}/10")

    print(f"\n🤝 社交策略:")
    ss = personality.social_strategy
    print(f"   发起: {ss.initiation}  |  自我暴露: {ss.self_disclosure}")

    print(f"\n✨ 价值观:")
    v = personality.values
    print(f"   核心: {', '.join(v.primary_values[:4])}")

    print(f"\n📝 总结: {personality.summary}")

    return personality, metadata


def step2_profile_builder(personality=None):
    """第二步：基础信息采集"""
    print_separator("Step 2: 用户画像采集")

    builder = ProfileBuilder()

    # 获取阶段1问题
    q = builder.get_stage_questions(stage=1)
    print(f"\n{q['greeting']}\n")

    answers = {}
    for item in q["questions"]:
        if item["type"] == "choice" and item.get("options"):
            print(f"  {item['question']}")
            for i, opt in enumerate(item["options"]):
                print(f"    [{i+1}] {opt}")
            choice = input(f"  请选择 (1-{len(item['options'])}): ").strip()
            try:
                answers[item["id"]] = item["options"][int(choice) - 1]
            except (ValueError, IndexError):
                answers[item["id"]] = choice
        else:
            answer = input(f"  {item['question']}\n  > ").strip()
            answers[item["id"]] = answer
        print()

    # 构建画像
    profile = builder.build_profile_from_answers(answers)
    print(f"\n  ✅ 用户画像已保存: {profile.nickname}, {profile.age}岁, {profile.occupation}")

    # 阶段2 - AI 个性化追问
    existing_info = builder.get_collected_info_summary(
        profile,
        personality.model_dump() if personality and personality.confidence > 0 else None,
    )

    q2 = builder.get_stage_questions(stage=2, existing_info=existing_info)
    print(f"\n{q2.get('greeting', '')}\n")

    for item in q2.get("questions", []):
        if item["type"] == "choice" and item.get("options"):
            print(f"  {item['question']}")
            for i, opt in enumerate(item["options"]):
                print(f"    [{i+1}] {opt}")
            choice = input(f"  请选择: ").strip()
        else:
            answer = input(f"  {item['question']}\n  > ").strip()
            answers[item["id"]] = answer
        print()

    return profile, answers


def step3_preferences(profile, personality):
    """第三步：偏好分析"""
    print_separator("Step 3: 匹配偏好分析")

    engine = PreferenceEngine()
    match_pref = engine.analyze_preferences(
        user_profile=profile,
        personality=personality,
    )

    print(f"\n💘 你的理想型:")
    print(f"   性格特质: {', '.join(match_pref.preferred_personality)}")
    print(f"   沟通风格: {', '.join(match_pref.preferred_style)}")
    print(f"   看重价值: {', '.join(match_pref.important_values)}")
    print(f"   绝对不要: {', '.join(match_pref.dealbreakers)}")
    if match_pref.description:
        print(f"   描述: {match_pref.description}")

    return match_pref


def step4_generate_persona(profile, personality, match_pref):
    """第四步：生成数字人 System Prompt"""
    print_separator("Step 4: 生成数字人 System Prompt")

    prompt_input = {
        "big_five": personality.big_five.model_dump(),
        "conversation_style": personality.conversation_style.model_dump(),
        "emotion_profile": personality.emotion_profile.model_dump(),
        "social_strategy": personality.social_strategy.model_dump(),
        "topic_preferences": personality.topic_preferences.model_dump(),
        "values": personality.values.model_dump(),
        "user_profile": profile.model_dump(),
    }

    system_prompt = build_persona_prompt(prompt_input)

    print("\n🤖 以下是你的数字人 System Prompt:")
    print("-" * 60)
    print(system_prompt.format(scene_description="校园空间的图书馆里，阳光洒在桌上"))
    print("-" * 60)

    return system_prompt


def main():
    print("\n" + "❤️ " * 20)
    print("     Social - 虚拟AI相亲系统 | 数字人生成")
    print("     让数字人先替你在虚拟世界谈一场恋爱")
    print("❤️ " * 20)

    # 检查 API Key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "sk-your-api-key-here":
        print("\n⚠️  请先设置 OPENAI_API_KEY 环境变量")
        print("   export OPENAI_API_KEY=sk-xxxxx")
        print("\n或者编辑 backend/config.py 中的 api_key")
        return

    print("\n🔧 LLM 服务初始化中...")
    try:
        llm = get_llm_service()
        print(f"   ✅ 已连接: {llm.model}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return

    # Step 1: 聊天分析
    personality, metadata = step1_chat_analysis()

    # Step 2: 用户画像
    profile, answers = step2_profile_builder(personality)

    # Step 3: 偏好分析
    match_pref = step3_preferences(profile, personality)

    # Step 4: 生成数字人
    system_prompt = step4_generate_persona(profile, personality, match_pref)

    print_separator("🎉 数字人生成完成！")
    print("\n你的数字人已经准备好进入虚拟世界了。")
    print("运行 Web 版本体验完整流程:")
    print("  python -m uvicorn backend.main:app --reload")
    print()


if __name__ == "__main__":
    main()
