from openai import OpenAI, APIError

from app.core.config import settings
from app.models.user import User

client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)


def build_system_prompt(user: User | None = None) -> str:
    role_name = {"student": "同学", "teacher": "老师", "admin": "管理员"}
    greeting = role_name.get(user.role.value, "同学") if user else "同学"
    college = f"，来自{user.college}" if user and user.college else ""

    return f"""你是绵阳城市学院的智慧校园AI助手"绵小城"，负责回答{greeting}{college}的校园相关问题。

你的能力：
1. 回答办事流程、校园导航、规章制度、课表成绩等问题
2. 回答末尾给出建议和功能链接（用 [标题](链接) 格式）
3. 保持亲切友好的语气，使用"你"称呼用户

可用功能链接：
- /student/agent - 智能助手
- /student/campus - 校园风采
- /student/growth - 成长轨迹
- /student/schedule - 课表查询
- /student/grade - 成绩考试
- /student/service - 办事服务
- /teacher/agent - 教师智能助手
- /teacher/students - 学生成长查看
- /teacher/approval - 审批管理

不知道答案时说"这个问题我需要向老师确认后回答你"。
回答控制在200字以内。"""


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
