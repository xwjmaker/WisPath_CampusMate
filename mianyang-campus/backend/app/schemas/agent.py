from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class Suggestion(BaseModel):
    text: str
    link: str | None = None
    action: str | None = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[Suggestion] = []
