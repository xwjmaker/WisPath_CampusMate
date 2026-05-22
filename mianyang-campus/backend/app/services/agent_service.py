import re
import json

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User
from app.models.knowledge import KnowledgeItem
from app.services.llm_service import build_system_prompt
from app.services.tool_registry import TOOL_DEFINITIONS, execute_tool
from app.services.crisis_service import detect_crisis_keywords, save_crisis_summary
from app.services.llm_service import client
from app.core.config import settings


def build_context(message: str, user: User) -> str:
    db = SessionLocal()
    try:
        keywords = [w for w in re.split(r"[，。！？、\s]+", message) if len(w) > 1]
        if not keywords:
            keywords = [message[:10]]
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


async def call_llm_with_tools(messages: list[dict], tools: list[dict]) -> tuple[str, list | None]:
    try:
        kwargs = {
            "model": settings.LLM_MODEL,
            "messages": messages,
            "temperature": 0.7,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        resp = client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        if msg.tool_calls:
            return "", msg.tool_calls
        return msg.content or "", None
    except Exception:
        raise


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

    try:
        first_pass_content, tool_calls = await call_llm_with_tools(messages, TOOL_DEFINITIONS if user.role.value == "student" else [])

        if tool_calls and user.role.value == "student":
            for tc in tool_calls:
                fn_name = tc.function.name
                try:
                    fn_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    fn_args = {}
                result = await execute_tool(fn_name, fn_args, user)
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{"id": tc.id, "type": "function", "function": {"name": fn_name, "arguments": tc.function.arguments}}]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

            second_pass_content, _ = await call_llm_with_tools(messages, [])
            full_reply = second_pass_content
        else:
            full_reply = first_pass_content

        yield full_reply

        # Suggestions extraction
        suggestions = _extract_suggestions(full_reply)
        if suggestions:
            yield f"\n__SUGGESTIONS__:{json.dumps(suggestions, ensure_ascii=False)}"

        # Crisis detection (background, non-blocking)
        keywords = detect_crisis_keywords(message)
        if keywords:
            try:
                crisis_db = SessionLocal()
                await save_crisis_summary(crisis_db, user.id, message, full_reply, keywords)
                crisis_db.close()
            except Exception:
                pass

        # Skill extraction (background)
        _try_extract_skills(message, user)

    except Exception:
        yield "抱歉，我暂时无法回答，请稍后再试。你也可以联系辅导员获取帮助。"
        return


def _extract_suggestions(text: str) -> list[dict]:
    suggestions = []
    pattern = r'\[(.+?)\]\((.+?)\)'
    for match in re.finditer(pattern, text):
        suggestions.append({"text": match.group(1), "link": match.group(2)})
    return suggestions


def _try_extract_skills(user_message: str, user: User):
    if user.role.value != "student":
        return
    skill_keywords = ["学", "考", "参加", "研究", "练习", "做", "开发", "写"]
    if not any(kw in user_message for kw in skill_keywords):
        return
    try:
        prompt = f"""从学生的发言中提取技能和兴趣信息。只提取明确提及的技能或兴趣。

学生发言：{user_message}

以JSON格式返回：
{{
    "skills": [{{"name": "技能名称", "context": "上下文"}}],
    "interests": ["兴趣1", "兴趣2"]
}}
如果没有提取到，返回 {{"skills": [], "interests": []}}"""

        resp = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        extracted = json.loads(content)

        db = SessionLocal()
        try:
            current_user = db.query(User).filter(User.id == user.id).first()
            if not current_user:
                return
            current = current_user.skills_json or {"skills": [], "interests": []}
            changed = False
            for s in extracted.get("skills", []):
                if not any(existing["name"] == s["name"] for existing in current["skills"]):
                    current["skills"].append(s)
                    changed = True
            for i in extracted.get("interests", []):
                if i not in current["interests"]:
                    current["interests"].append(i)
                    changed = True
            if changed:
                current_user.skills_json = current
                db.commit()
        finally:
            db.close()
    except Exception:
        pass
