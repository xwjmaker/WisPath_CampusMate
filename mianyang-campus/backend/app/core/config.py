from os import environ
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:123456@localhost:3306/smart_campus"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen-turbo"
    LLM_AGENT_MODEL: str = "qwen-turbo"
    LLM_AGENT_TEMPERATURE: float = 0.7
    LLM_AGENT_MAX_TOKENS: int = 10000

    class Config:
        env_file = str(Path(__file__).resolve().parent.parent / ".env")

    @property
    def llm_api_key(self) -> str:
        return self.LLM_API_KEY or environ.get("OPENAI_API_KEY", "")


settings = Settings()
