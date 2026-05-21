from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.agent import router as agent_router
from app.api.campus import router as campus_router
from app.api.growth import router as growth_router
from app.api.academic import router as academic_router
from app.api.service import router as service_router

app = FastAPI(title="智慧校园AI服务平台", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(campus_router)
app.include_router(growth_router)
app.include_router(academic_router)
app.include_router(service_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
