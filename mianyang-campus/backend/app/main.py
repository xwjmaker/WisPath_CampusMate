from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import engine, Base
from app.api.auth import router as auth_router
from app.api.agent import router as agent_router
from app.api.campus import router as campus_router
from app.api.growth import router as growth_router
from app.api.academic import router as academic_router
from app.api.service import router as service_router
from app.api.leave import router as leave_router
from app.api.crisis import router as crisis_router
from app.api.teacher import router as teacher_router
from app.api.upload import router as upload_router
from app.api.conversations import router as conversations_router
from app.api.messages import router as messages_router
from app.api.announcement import router as announcement_router
from app.api.test_role import router as test_role_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # 自动运行种子数据（仅首次创建时插入）
    import importlib
    importlib.import_module("app.seed")
    yield

app = FastAPI(title="智慧校园AI服务平台", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(campus_router)
app.include_router(growth_router)
app.include_router(academic_router)
app.include_router(service_router)
app.include_router(leave_router)
app.include_router(crisis_router)
app.include_router(teacher_router)
app.include_router(conversations_router)
app.include_router(upload_router)
app.include_router(messages_router)
app.include_router(announcement_router)
app.include_router(test_role_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
