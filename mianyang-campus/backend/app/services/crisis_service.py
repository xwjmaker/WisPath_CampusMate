import re
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.crisis import AIDialogSummary, CrisisLevel
from app.models.user import User
from app.services.llm_service import _get_client
from app.core.config import settings

CRISIS_KEYWORDS = [
    "失眠", "睡不着", "焦虑", "抑郁", "压力大", "不想活", "自杀",
    "自残", "想死", "没意思", "活着累", "撑不住", "崩溃", "绝望",
    "不想上学", "害怕", "心慌", "难受", "想哭",
]


def detect_crisis_keywords(text: str) -> list[str]:
    matched = []
    for kw in CRISIS_KEYWORDS:
        if kw in text:
            matched.append(kw)
    return matched


async def generate_crisis_summary(user_message: str, ai_reply: str, keywords: list[str]) -> dict | None:
    if not keywords:
        return None
    try:
        prompt = f"""你是一名校园心理健康辅助分析助手。学生向AI助手发送了以下消息，其中包含潜在心理危机关键词：{', '.join(keywords)}。

学生消息：{user_message}
AI回复：{ai_reply}

请生成一段脱敏摘要（不包含具体姓名、班级、学号等可识别信息），并评估危机等级。

以JSON格式返回：
{{
    "summary": "脱敏后的摘要描述",
    "level": "severe" 或 "moderate" 或 "mild"
}}

等级定义：
- severe: 明确的自杀/自残倾向
- moderate: 明显的焦虑、抑郁、压力过大
- mild: 轻度情绪困扰"""

        resp = _get_client().chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        import json
        result = json.loads(content)
        return result
    except Exception:
        return {
            "summary": f"学生消息中包含敏感关键词：{', '.join(keywords)}",
            "level": "mild",
        }


async def save_crisis_summary(db: Session, student_id: int, user_message: str, ai_reply: str, keywords: list[str]):
    if not keywords:
        return
    result = await generate_crisis_summary(user_message, ai_reply, keywords)
    if not result:
        return
    summary = AIDialogSummary(
        student_id=student_id,
        summary=result.get("summary", ""),
        level=result.get("level", "mild"),
        keywords_matched=",".join(keywords),
        raw_snippet=user_message[:200],
    )
    db.add(summary)
    db.commit()
