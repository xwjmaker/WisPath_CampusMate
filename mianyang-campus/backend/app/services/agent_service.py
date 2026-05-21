import re
import json

from sqlalchemy import or_

from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeItem
from app.models.user import User
from app.services.llm_service import build_system_prompt, chat_stream


def extract_suggestions(text: str) -> list[dict]:
    suggestions = []
    pattern = r'\[(.+?)\]\((.+?)\)'
    for match in re.finditer(pattern, text):
        suggestions.append({"text": match.group(1), "link": match.group(2)})
    return suggestions


def build_context(user_message: str, user: User) -> str:
    db = SessionLocal()
    try:
        keywords = [w for w in re.split(r"[，。！？、\s]+", user_message) if len(w) > 1]
        if not keywords:
            keywords = [user_message[:10]]
        conditions = []
        for kw in keywords[:5]:
            conditions.append(KnowledgeItem.question.like(f"%{kw}%"))
            conditions.append(KnowledgeItem.answer.like(f"%{kw}%"))
            conditions.append(KnowledgeItem.tags.like(f"%{kw}%"))
        results = db.query(KnowledgeItem).filter(or_(*conditions)).limit(5).all() if conditions else []
        if results:
            context = "相关校园知识：\n"
            for r in results:
                context += f"[{r.category}] Q: {r.question}\nA: {r.answer}\n\n"
            return context
        return ""
    finally:
        db.close()


async def chat(message: str, history: list[dict], user: User):
    system_prompt = build_system_prompt(user)
    context = build_context(message, user)
    system_content = system_prompt
    if context:
        system_content += "\n\n参考以下校园知识回答：\n" + context

    messages = [{"role": "system", "content": system_content}]
    for h in history[-10:]:
        messages.append(h)
    messages.append({"role": "user", "content": message})

    full_reply = ""
    try:
        async for chunk in chat_stream(messages):
            full_reply += chunk
            yield chunk
    except Exception:
        yield "抱歉，我暂时无法回答，请稍后再试。你也可以查看 [智能助手](/student/agent) 或联系辅导员。"
        return

    if full_reply:
        suggestions = extract_suggestions(full_reply)
        yield f"\n__SUGGESTIONS__:{json.dumps(suggestions, ensure_ascii=False)}"
