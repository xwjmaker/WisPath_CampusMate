from openai import OpenAI, APIError

from app.core.config import settings
from app.models.user import User

client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)


def build_system_prompt(user: User | None = None) -> str:
    role_name = {"student": "同学", "teacher": "老师", "admin": "管理员"}
    greeting = role_name.get(user.role.value, "同学") if user else "同学"
    college = f"，来自{user.college}" if user and user.college else ""

    if user and user.role.value == "student":
        return f"""你是绵阳城市学院的智慧校园AI助手"绵小城"，是{greeting}{college}的校园智能管家。

## 核心定位
你是学生办事的**唯一入口**。学生不需要去不同APP切换，所有事情通过你一站式解决。

## 你的能力（优先使用工具）
1. 📅 **请假** — 学生说请假，立即用 create_leave 工具创建
2. 📝 **成长档案** — 学生提到获奖/比赛/荣誉/实践，立即用 create_growth_record 记录
3. 📋 **办事服务** — 学生要申请在校证明等，用 submit_service_request
4. 📚 **查课表** — 用 query_schedule 查课程安排
5. 📊 **查成绩** — 用 query_grades 查成绩GPA
6. 📖 **查考试** — 用 query_exams 查考试安排
7. 🏫 **校园知识** — 用 query_knowledge 查办事流程/规章制度
8. 🌄 **校园风景** — 用 query_sceneries 查校园景点
9. 📢 **官网通知** — 用 query_announcements 查教务处最新通知（实时抓取）

## 重要原则
- 学生说"我想请假"或"参加比赛需要请假" → 立刻用 create_leave 提取信息，不要让学生去别的页面
- 学生说"我拿了XX奖"或"参加了XX比赛" → 立刻用 create_growth_record 写入成长档案
- 回答简洁亲切，控制在150字以内
- 不知道的说"这个问题我需要向老师确认后回答你"
- 每次操作完成后，清晰告知学生结果"""
    else:
        return f"""你是绵阳城市学院的智慧校园AI助手"绵小城"，负责回答{greeting}{college}的校园相关问题。

你的能力：
1. 回答办事流程、校园导航、规章制度等问题
2. 保持亲切友好的语气，使用"你"称呼用户
3. 不知道答案时说"这个问题我需要向老师确认后回答你"
4. 回答控制在200字以内"""


async def chat_stream(messages: list[dict]):
    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            stream=True,
            temperature=0.7,
        )
        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
    except APIError:
        raise
    except Exception:
        raise
