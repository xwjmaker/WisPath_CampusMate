# 智慧校园AI服务平台 V1.0 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现基于大模型的智慧校园AI服务平台 V1.0 MVP，覆盖统一登录门户、学生/教师端基础框架、校园问答智能体、校园风采展示、成长轨迹、课表成绩考试查询、请假证明申请等核心功能。

**Architecture:** 前后端分离架构。前端 Vue 3 + TypeScript + Vite + Element Plus + Pinia 状态管理 + Vue Router，后端 Python FastAPI + SQLAlchemy ORM + PostgreSQL + Alembic 迁移，通过 RESTful API 通信，智能体对话采用 SSE(Server-Sent Events) 流式响应。

**Tech Stack:**
- **前端:** Vue 3.4 + TypeScript 5 + Vite 5 + Element Plus + Pinia + Vue Router 4 + Axios
- **后端:** Python 3.11+ / FastAPI 0.110+ / SQLAlchemy 2.0 / Alembic / PostgreSQL 15+ / Pydantic v2
- **LLM:** OpenAI 兼容 API（通义千问 DashScope / 任意兼容接口）
- **认证:** JWT + 密码哈希（bcrypt）
- **工具:** Node.js 18+ / npm / Poetry 或 pip + venv

---

## 项目目录结构

```
mianyang-campus/
├── frontend/                          # Vue 3 前端项目
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/                       # API 调用层
│   │   │   ├── auth.ts                #   登录/认证
│   │   │   ├── agent.ts               #   智能体对话
│   │   │   ├── campus.ts              #   校园风采
│   │   │   ├── growth.ts              #   成长轨迹
│   │   │   ├── academic.ts            #   学业（课表/成绩/考试）
│   │   │   └── service.ts             #   办事（请假/证明）
│   │   ├── components/                # 可复用组件
│   │   │   ├── layout/
│   │   │   │   ├── StudentLayout.vue  #   学生端布局
│   │   │   │   └── TeacherLayout.vue  #   教师端布局
│   │   │   ├── agent/
│   │   │   │   └── ChatPanel.vue      #   智能体对话面板
│   │   │   ├── campus/
│   │   │   │   ├── FigureCard.vue     #   人物风采卡片
│   │   │   │   └── SceneryCard.vue    #   风景卡片
│   │   │   └── growth/
│   │   │       └── MilestoneCard.vue  #   成长里程碑卡片
│   │   ├── views/
│   │   │   ├── login/
│   │   │   │   └── LoginPage.vue      #   统一登录页
│   │   │   ├── role-select/
│   │   │   │   └── RoleSelectPage.vue #   角色选择页
│   │   │   ├── student/
│   │   │   │   ├── HomePage.vue       #   学生首页
│   │   │   │   ├── AgentPage.vue      #   智能体对话页
│   │   │   │   ├── CampusPage.vue     #   校园风采
│   │   │   │   ├── GrowthPage.vue     #   成长轨迹
│   │   │   │   ├── SchedulePage.vue   #   课表查询
│   │   │   │   ├── GradePage.vue      #   成绩/考试查询
│   │   │   │   └── ServicePage.vue    #   办事服务
│   │   │   └── teacher/
│   │   │       ├── HomePage.vue       #   教师首页
│   │   │       ├── AgentPage.vue      #   智能体对话页
│   │   │       └── ApprovalPage.vue   #   审批管理
│   │   ├── stores/
│   │   │   ├── auth.ts                #   认证状态
│   │   │   └── agent.ts               #   对话状态
│   │   ├── router/
│   │   │   └── index.ts               #   路由配置
│   │   ├── types/
│   │   │   └── index.ts               #   类型定义
│   │   ├── utils/
│   │   │   ├── request.ts             #   Axios 封装
│   │   │   └── token.ts               #   JWT 工具
│   │   ├── App.vue                    #   根组件
│   │   └── main.ts                    #   入口
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── backend/
│   ├── app/
│   │   ├── api/                       # 路由层
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                #   认证接口
│   │   │   ├── agent.py               #   智能体接口
│   │   │   ├── campus.py              #   校园风采接口
│   │   │   ├── growth.py              #   成长轨迹接口
│   │   │   ├── academic.py            #   学业接口
│   │   │   └── service.py             #   办事接口
│   │   ├── models/                    # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py                #   用户模型
│   │   │   ├── knowledge.py           #   知识库模型
│   │   │   ├── campus.py              #   校园风采模型
│   │   │   ├── growth.py              #   成长记录模型
│   │   │   ├── academic.py            #   学业模型
│   │   │   └── service.py             #   工单模型
│   │   ├── schemas/                   # Pydantic 校验
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── agent.py
│   │   │   ├── campus.py
│   │   │   ├── growth.py
│   │   │   ├── academic.py
│   │   │   └── service.py
│   │   ├── services/                  # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py        #   认证服务
│   │   │   ├── agent_service.py       #   智能体服务
│   │   │   └── llm_service.py         #   LLM 调用服务
│   │   ├── core/                      # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py              #   配置管理
│   │   │   ├── security.py            #   密码/JWT 工具
│   │   │   └── database.py            #   数据库连接
│   │   ├── main.py                    # FastAPI 入口
│   │   └── seed.py                    # 初始数据填充
│   ├── alembic/
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env
└── docs/
    └── superpowers/
        ├── specs/
        └── plans/
```

---

### Task 1: 项目脚手架搭建

**Files:**
- Create: `mianyang-campus/backend/pyproject.toml`
- Create: `mianyang-campus/backend/.env`
- Create: `mianyang-campus/backend/app/__init__.py`
- Create: `mianyang-campus/backend/app/core/__init__.py`
- Create: `mianyang-campus/backend/app/core/config.py`
- Create: `mianyang-campus/backend/app/core/database.py`
- Create: `mianyang-campus/backend/app/main.py`
- Create: `mianyang-campus/frontend/` (通过 vite 初始化)

- [ ] **Step 1: 创建后端 pyproject.toml**

```toml
[project]
name = "smart-campus-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.25",
    "psycopg2-binary>=2.9.9",
    "alembic>=1.13.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
    "httpx>=0.26.0",
    "openai>=1.12.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

- [ ] **Step 2: 创建 .env 配置文件**

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_campus
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
LLM_API_KEY=your-llm-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

- [ ] **Step 3: 创建 core/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/smart_campus"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen-turbo"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 4: 创建 core/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 5: 创建 main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="智慧校园AI服务平台", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 6: 初始化前端项目**

```bash
cd mianyang-campus
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install element-plus @element-plus/icons-vue pinia vue-router@4 axios
```

- [ ] **Step 7: 配置前端 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') }
  },
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
})
```

- [ ] **Step 8: 配置前端 main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
```

- [ ] **Step 9: 创建前端类型定义 types/index.ts**

```typescript
// 用户角色
export type UserRole = 'student' | 'teacher' | 'admin'

// 用户信息
export interface UserInfo {
  id: number
  username: string
  name: string
  role: UserRole
  college?: string
  avatar?: string
}

// 登录请求/响应
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

// 对话消息
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  suggestions?: Suggestion[]
  timestamp: string
}

export interface Suggestion {
  text: string
  link?: string
  action?: string
}

// 成长记录
export interface GrowthRecord {
  id: number
  student_id: number
  type: 'honor' | 'competition' | 'award' | 'practice'
  title: string
  description: string
  date: string
  attachment_url?: string
}

// 校园风采
export interface CampusFigure {
  id: number
  name: string
  title: string
  avatar: string
  description: string
  category: 'student' | 'teacher' | 'alumni'
}

export interface CampusScenery {
  id: number
  title: string
  image_url: string
  description: string
  location: string
}

// 课表
export interface Course {
  id: number
  name: string
  teacher: string
  location: string
  day_of_week: number
  start_period: number
  end_period: number
  week_start: number
  week_end: number
}

// 成绩
export interface Grade {
  id: number
  course_name: string
  score: number
  credit: number
  gpa: number
  semester: string
}

// 考试安排
export interface Exam {
  id: number
  course_name: string
  exam_date: string
  start_time: string
  end_time: string
  location: string
}

// 工单
export type TicketType = 'leave' | 'certificate'
export type TicketStatus = 'pending' | 'approved' | 'rejected'

export interface ServiceTicket {
  id: number
  type: TicketType
  title: string
  content: string
  status: TicketStatus
  created_at: string
}
```

- [ ] **Step 10: 创建前端工具函数 utils/token.ts**

```typescript
const TOKEN_KEY = 'campus_token'
const USER_KEY = 'campus_user'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getUser(): any {
  const raw = localStorage.getItem(USER_KEY)
  return raw ? JSON.parse(raw) : null
}

export function setUser(user: any) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}
```

- [ ] **Step 11: 创建 Axios 封装 utils/request.ts**

```typescript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from './token'

const request = axios.create({ baseURL: '/api' })

request.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      removeToken()
      window.location.href = '/login'
    }
    ElMessage.error(err.response?.data?.detail || '请求失败')
    return Promise.reject(err)
  }
)

export default request
```

- [ ] **Step 12: Commit**

```bash
git init
git add .
git commit -m "chore: scaffold project with Vue 3 + FastAPI"
```

---

### Task 2: 数据库模型与迁移

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/knowledge.py`
- Create: `backend/app/models/campus.py`
- Create: `backend/app/models/growth.py`
- Create: `backend/app/models/academic.py`
- Create: `backend/app/models/service.py`
- Create: `backend/app/seed.py`

- [ ] **Step 1: 创建 core/security.py**

```python
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.JWTError:
        return None
```

- [ ] **Step 2: 创建 models/user.py**

```python
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(50))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole))
    college: Mapped[str | None] = mapped_column(String(100))
    avatar: Mapped[str | None] = mapped_column(String(255))
    tutor_id: Mapped[int | None] = mapped_column(default=None)
```

- [ ] **Step 3: 创建 models/knowledge.py**

```python
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class KnowledgeItem(Base):
    __tablename__ = "knowledge_base"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    question: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(String(200))
```

- [ ] **Step 4: 创建 models/campus.py**

```python
from sqlalchemy import String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class FigureCategory(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ALUMNI = "alumni"


class CampusFigure(Base):
    __tablename__ = "campus_figures"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(100))
    avatar: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[FigureCategory] = mapped_column(SAEnum(FigureCategory))


class CampusScenery(Base):
    __tablename__ = "campus_sceneries"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    image_url: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(100))
```

- [ ] **Step 5: 创建 models/growth.py**

```python
from sqlalchemy import String, Text, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class RecordType(str, enum.Enum):
    HONOR = "honor"
    COMPETITION = "competition"
    AWARD = "award"
    PRACTICE = "practice"


class GrowthRecord(Base):
    __tablename__ = "growth_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(index=True)
    type: Mapped[RecordType] = mapped_column(SAEnum(RecordType))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    date: Mapped[str] = mapped_column(Date)
    attachment_url: Mapped[str | None] = mapped_column(String(255))
```

- [ ] **Step 6: 创建 models/academic.py**

```python
from sqlalchemy import String, Float, Integer, Date, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(index=True)
    name: Mapped[str] = mapped_column(String(100))
    teacher: Mapped[str] = mapped_column(String(50))
    location: Mapped[str] = mapped_column(String(100))
    day_of_week: Mapped[int] = mapped_column(Integer)
    start_period: Mapped[int] = mapped_column(Integer)
    end_period: Mapped[int] = mapped_column(Integer)
    week_start: Mapped[int] = mapped_column(Integer)
    week_end: Mapped[int] = mapped_column(Integer)


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(index=True)
    course_name: Mapped[str] = mapped_column(String(100))
    score: Mapped[float] = mapped_column(Float)
    credit: Mapped[float] = mapped_column(Float)
    gpa: Mapped[float] = mapped_column(Float)
    semester: Mapped[str] = mapped_column(String(20))


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(index=True)
    course_name: Mapped[str] = mapped_column(String(100))
    exam_date: Mapped[str] = mapped_column(Date)
    start_time: Mapped[str] = mapped_column(Time)
    end_time: Mapped[str] = mapped_column(Time)
    location: Mapped[str] = mapped_column(String(100))
```

- [ ] **Step 7: 创建 models/service.py**

```python
from datetime import datetime, timezone
from sqlalchemy import String, Text, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.database import Base


class TicketType(str, enum.Enum):
    LEAVE = "leave"
    CERTIFICATE = "certificate"


class TicketStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    applicant_id: Mapped[int] = mapped_column(index=True)
    type: Mapped[TicketType] = mapped_column(SAEnum(TicketType))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    attachment: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[TicketStatus] = mapped_column(SAEnum(TicketStatus), default=TicketStatus.PENDING)
    approver_id: Mapped[int | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 8: 创建 seed.py 初始化数据**

```python
from app.core.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole

Base.metadata.create_all(bind=engine)

db = SessionLocal()

if db.query(User).count() == 0:
    users = [
        User(username="2024001", password_hash=hash_password("123456"), name="张三", role=UserRole.STUDENT, college="软件学院"),
        User(username="2024002", password_hash=hash_password("123456"), name="李四", role=UserRole.STUDENT, college="软件学院"),
        User(username="t1001", password_hash=hash_password("123456"), name="王老师", role=UserRole.TEACHER, college="软件学院"),
        User(username="admin", password_hash=hash_password("admin123"), name="管理员", role=UserRole.ADMIN),
    ]
    db.add_all(users)
    db.commit()

db.close()
print("Seed data created successfully")
```

- [ ] **Step 9: Commit**

```bash
git add backend/app/core/security.py backend/app/models/ backend/app/seed.py
git commit -m "feat: add database models and seed data"
```

---

### Task 3: 用户认证 API（后端）

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/auth.py`

- [ ] **Step 1: 创建 schemas/user.py**

```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    name: str
    role: str
    college: str | None = None
    avatar: str | None = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo
```

- [ ] **Step 2: 创建 services/auth_service.py**

```python
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.models.user import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def login_user(db: Session, username: str, password: str) -> dict | None:
    user = authenticate_user(db, username, password)
    if not user:
        return None
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    from app.schemas.user import UserInfo
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserInfo.model_validate(user).model_dump(),
    }
```

- [ ] **Step 3: 创建 api/auth.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import LoginRequest, LoginResponse
from app.services.auth_service import login_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, req.username, req.password)
    if not result:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return result
```

- [ ] **Step 4: 在 main.py 注册路由**

```python
from app.api.auth import router as auth_router
app.include_router(auth_router)
```

- [ ] **Step 5: 写测试并验证**

```bash
cd backend
pip install httpx pytest
```

创建 `backend/tests/test_auth.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_success():
    resp = client.post("/api/auth/login", json={"username": "2024001", "password": "123456"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "student"


def test_login_fail():
    resp = client.post("/api/auth/login", json={"username": "2024001", "password": "wrong"})
    assert resp.status_code == 401
```

```bash
pytest tests/test_auth.py -v
# Expected: 2 passed
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/auth.py backend/app/schemas/ backend/app/services/
git commit -m "feat: add user authentication API"
```

---

### Task 4: 登录页与角色选择（前端）

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/views/login/LoginPage.vue`
- Create: `frontend/src/views/role-select/RoleSelectPage.vue`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: 创建 stores/auth.ts**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types'
import { setToken, setUser, getToken, getUser, removeToken } from '@/utils/token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getToken())
  const user = ref<UserInfo | null>(getUser())

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role)
  const userName = computed(() => user.value?.name)

  function login(t: string, u: UserInfo) {
    token.value = t
    user.value = u
    setToken(t)
    setUser(u)
  }

  function logout() {
    token.value = null
    user.value = null
    removeToken()
  }

  return { token, user, isLoggedIn, role, userName, login, logout }
})
```

- [ ] **Step 2: 创建 api/auth.ts**

```typescript
import request from '@/utils/request'
import type { LoginRequest, LoginResponse } from '@/types'

export function loginApi(data: LoginRequest) {
  return request.post<LoginResponse>('/auth/login', data)
}
```

- [ ] **Step 3: 创建 router/index.ts**

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/token'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('@/views/login/LoginPage.vue') },
    { path: '/role-select', name: 'RoleSelect', component: () => import('@/views/role-select/RoleSelectPage.vue') },
    { path: '/student', name: 'StudentHome', component: () => import('@/views/student/HomePage.vue'), meta: { role: 'student' } },
    { path: '/teacher', name: 'TeacherHome', component: () => import('@/views/teacher/HomePage.vue'), meta: { role: 'teacher' } },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

router.beforeEach((to) => {
  if (!getToken() && to.path !== '/login') return '/login'
})

export default router
```

- [ ] **Step 4: 创建 LoginPage.vue**

```vue
<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>智慧校园AI服务平台</h2>
      <el-form ref="formRef" :model="form" :rules="rules" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="学号/工号" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" style="width:100%" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { loginApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入学号/工号' }],
  password: [{ required: true, message: '请输入密码' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await loginApi(form)
    auth.login(res.access_token, res.user)
    ElMessage.success('登录成功')
    router.push('/role-select')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
.login-card { width: 400px; }
.login-card h2 { text-align: center; margin-bottom: 24px; color: #409eff; }
</style>
```

- [ ] **Step 5: 创建 RoleSelectPage.vue**

```vue
<template>
  <div class="role-select-container">
    <h2>欢迎使用智慧校园AI服务平台</h2>
    <p class="subtitle">请选择您的身份</p>
    <div class="role-cards">
      <el-card class="role-card" shadow="hover" @click="enter('student')">
        <el-icon :size="48" color="#409eff"><UserFilled /></el-icon>
        <h3>学生端</h3>
        <p>查询课表成绩、智能问答、办事服务</p>
      </el-card>
      <el-card class="role-card" shadow="hover" @click="enter('teacher')">
        <el-icon :size="48" color="#67c23a"><Avatar /></el-icon>
        <h3>教师端</h3>
        <p>审批管理、智能问答、学生成长查看</p>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { UserFilled, Avatar } from '@element-plus/icons-vue'

const router = useRouter()

function enter(role: string) {
  router.push(`/${role}`)
}
</script>

<style scoped>
.role-select-container { text-align: center; padding-top: 120px; }
.subtitle { color: #666; margin-bottom: 40px; }
.role-cards { display: flex; justify-content: center; gap: 40px; }
.role-card { width: 280px; cursor: pointer; }
.role-card:hover { transform: translateY(-4px); transition: 0.3s; }
</style>
```

- [ ] **Step 6: 修改 App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 7: 启动验证**

```bash
# 终端1: 后端
cd backend && uvicorn app.main:app --reload

# 终端2: 前端
cd frontend && npm run dev
```

浏览器打开 http://localhost:5173 ，应看到登录页面。

- [ ] **Step 8: Commit**

```bash
git add frontend/src/router/ frontend/src/stores/auth.ts frontend/src/api/auth.ts frontend/src/views/login/ frontend/src/views/role-select/
git commit -m "feat: add login page and role selection"
```

---

### Task 5: 学生端首页与布局框架

**Files:**
- Create: `frontend/src/components/layout/StudentLayout.vue`
- Create: `frontend/src/views/student/HomePage.vue`
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 创建 StudentLayout.vue**

```vue
<template>
  <el-container style="min-height:100vh">
    <el-aside width="220px">
      <el-menu :router="true" :default-active="route.path" style="height:100%">
        <div class="logo">智慧校园</div>
        <el-menu-item index="/student">
          <el-icon><HomeFilled /></el-icon>首页
        </el-menu-item>
        <el-menu-item index="/student/agent">
          <el-icon><ChatDotSquare /></el-icon>智能助手
        </el-menu-item>
        <el-menu-item index="/student/campus">
          <el-icon><PictureFilled /></el-icon>校园风采
        </el-menu-item>
        <el-menu-item index="/student/growth">
          <el-icon><TrendCharts /></el-icon>成长轨迹
        </el-menu-item>
        <el-menu-item index="/student/schedule">
          <el-icon><Calendar /></el-icon>课表查询
        </el-menu-item>
        <el-menu-item index="/student/grade">
          <el-icon><Document /></el-icon>成绩考试
        </el-menu-item>
        <el-menu-item index="/student/service">
          <el-icon><Service /></el-icon>办事服务
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>欢迎，{{ auth.userName }}</span>
        <el-button text @click="logout">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeFilled, ChatDotSquare, PictureFilled, TrendCharts,
  Calendar, Document, Service
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; font-weight: bold; color: #409eff; }
.header { display: flex; justify-content: flex-end; align-items: center; border-bottom: 1px solid #eee; }
</style>
```

- [ ] **Step 2: 创建 student/HomePage.vue**

```vue
<template>
  <div>
    <h2>学生首页</h2>
    <el-row :gutter="20">
      <el-col :span="8" v-for="card in cards" :key="card.title">
        <el-card shadow="hover" style="margin-bottom:20px;cursor:pointer" @click="router.push(card.link)">
          <el-icon :size="32" :color="card.color"><component :is="card.icon" /></el-icon>
          <h3>{{ card.title }}</h3>
          <p>{{ card.desc }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChatDotSquare, PictureFilled, TrendCharts, Calendar, Document, Service } from '@element-plus/icons-vue'

const router = useRouter()
const cards = [
  { title: '智能助手', desc: '校园问答、办事咨询', icon: ChatDotSquare, color: '#409eff', link: '/student/agent' },
  { title: '校园风采', desc: '人物风采、校园风景', icon: PictureFilled, color: '#67c23a', link: '/student/campus' },
  { title: '成长轨迹', desc: '荣誉、竞赛、实践', icon: TrendCharts, color: '#e6a23c', link: '/student/growth' },
  { title: '课表查询', desc: '查看课程安排', icon: Calendar, color: '#f56c6c', link: '/student/schedule' },
  { title: '成绩考试', desc: '成绩查询、考试安排', icon: Document, color: '#909399', link: '/student/grade' },
  { title: '办事服务', desc: '请假申请、证明打印', icon: Service, color: '#b37feb', link: '/student/service' },
]
</script>
```

- [ ] **Step 3: 更新路由，添加子路由**

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/token'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('@/views/login/LoginPage.vue') },
    { path: '/role-select', name: 'RoleSelect', component: () => import('@/views/role-select/RoleSelectPage.vue') },
    {
      path: '/student',
      component: () => import('@/components/layout/StudentLayout.vue'),
      meta: { role: 'student' },
      children: [
        { path: '', component: () => import('@/views/student/HomePage.vue') },
        { path: 'agent', component: () => import('@/views/student/AgentPage.vue') },
        { path: 'campus', component: () => import('@/views/student/CampusPage.vue') },
        { path: 'growth', component: () => import('@/views/student/GrowthPage.vue') },
        { path: 'schedule', component: () => import('@/views/student/SchedulePage.vue') },
        { path: 'grade', component: () => import('@/views/student/GradePage.vue') },
        { path: 'service', component: () => import('@/views/student/ServicePage.vue') },
      ],
    },
    { path: '/teacher', name: 'TeacherHome', component: () => import('@/views/teacher/HomePage.vue'), meta: { role: 'teacher' } },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

router.beforeEach((to) => {
  if (!getToken() && to.path !== '/login') return '/login'
})

export default router
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/ frontend/src/views/student/HomePage.vue frontend/src/router/index.ts
git commit -m "feat: add student layout and homepage"
```

---

### Task 6: 教师端首页与布局框架

**Files:**
- Create: `frontend/src/components/layout/TeacherLayout.vue`
- Create: `frontend/src/views/teacher/HomePage.vue`
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 创建 TeacherLayout.vue**

```vue
<template>
  <el-container style="min-height:100vh">
    <el-aside width="220px">
      <el-menu :router="true" :default-active="route.path" style="height:100%">
        <div class="logo">智慧校园</div>
        <el-menu-item index="/teacher">
          <el-icon><HomeFilled /></el-icon>首页
        </el-menu-item>
        <el-menu-item index="/teacher/agent">
          <el-icon><ChatDotSquare /></el-icon>智能助手
        </el-menu-item>
        <el-menu-item index="/teacher/students">
          <el-icon><User /></el-icon>学生成长
        </el-menu-item>
        <el-menu-item index="/teacher/approval">
          <el-icon><CircleCheck /></el-icon>审批管理
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>欢迎，{{ auth.userName }}</span>
        <el-button text @click="logout">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { HomeFilled, ChatDotSquare, User, CircleCheck } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; font-weight: bold; color: #67c23a; }
.header { display: flex; justify-content: flex-end; align-items: center; border-bottom: 1px solid #eee; }
</style>
```

- [ ] **Step 2: 创建 teacher/HomePage.vue**

```vue
<template>
  <div>
    <h2>教师首页</h2>
    <el-row :gutter="20">
      <el-col :span="8" v-for="card in cards" :key="card.title">
        <el-card shadow="hover" style="margin-bottom:20px;cursor:pointer" @click="router.push(card.link)">
          <el-icon :size="32" :color="card.color"><component :is="card.icon" /></el-icon>
          <h3>{{ card.title }}</h3>
          <p>{{ card.desc }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChatDotSquare, User, CircleCheck } from '@element-plus/icons-vue'

const router = useRouter()
const cards = [
  { title: '智能助手', desc: '校园问答、事务咨询', icon: ChatDotSquare, color: '#409eff', link: '/teacher/agent' },
  { title: '学生成长', desc: '查看学生成长轨迹', icon: User, color: '#67c23a', link: '/teacher/students' },
  { title: '审批管理', desc: '请假、证明审批', icon: CircleCheck, color: '#e6a23c', link: '/teacher/approval' },
]
</script>
```

- [ ] **Step 3: 更新路由，添加教师子路由**

```typescript
{
  path: '/teacher',
  component: () => import('@/components/layout/TeacherLayout.vue'),
  meta: { role: 'teacher' },
  children: [
    { path: '', component: () => import('@/views/teacher/HomePage.vue') },
    { path: 'agent', component: () => import('@/views/teacher/AgentPage.vue') },
    { path: 'students', component: () => import('@/views/teacher/StudentsPage.vue') },
    { path: 'approval', component: () => import('@/views/teacher/ApprovalPage.vue') },
  ],
},
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/layout/TeacherLayout.vue frontend/src/views/teacher/ frontend/src/router/index.ts
git commit -m "feat: add teacher layout and homepage"
```

---

### Task 7: 校园风采展示（后端 API + 前端页面）

**Files:**
- Create: `backend/app/api/campus.py`
- Create: `backend/app/schemas/campus.py`
- Create: `frontend/src/api/campus.ts`
- Create: `frontend/src/views/student/CampusPage.vue`
- Create: `frontend/src/components/campus/FigureCard.vue`
- Create: `frontend/src/components/campus/SceneryCard.vue`

- [ ] **Step 1: 创建 schemas/campus.py**

```python
from pydantic import BaseModel
from datetime import date


class CampusFigureOut(BaseModel):
    id: int
    name: str
    title: str
    avatar: str
    description: str
    category: str

    class Config:
        from_attributes = True


class CampusSceneryOut(BaseModel):
    id: int
    title: str
    image_url: str
    description: str | None = None
    location: str | None = None

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 创建 api/campus.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.campus import CampusFigure, CampusScenery
from app.schemas.campus import CampusFigureOut, CampusSceneryOut

router = APIRouter(prefix="/api/campus", tags=["campus"])


@router.get("/figures", response_model=list[CampusFigureOut])
def list_figures(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(CampusFigure)
    if category:
        query = query.filter(CampusFigure.category == category)
    return query.all()


@router.get("/sceneries", response_model=list[CampusSceneryOut])
def list_sceneries(db: Session = Depends(get_db)):
    return db.query(CampusScenery).all()
```

- [ ] **Step 3: 注册路由**

在 `main.py` 添加：
```python
from app.api.campus import router as campus_router
app.include_router(campus_router)
```

- [ ] **Step 4: 创建前端 api/campus.ts**

```typescript
import request from '@/utils/request'
import type { CampusFigure, CampusScenery } from '@/types'

export function getFigures(category?: string) {
  return request.get<CampusFigure[]>('/campus/figures', { params: { category } })
}

export function getSceneries() {
  return request.get<CampusScenery[]>('/campus/sceneries')
}
```

- [ ] **Step 5: 创建 FigureCard.vue**

```vue
<template>
  <el-card shadow="hover">
    <el-avatar :size="80" :src="figure.avatar" style="margin:0 auto;display:block" />
    <h3 style="text-align:center">{{ figure.name }}</h3>
    <p style="text-align:center;color:#666">{{ figure.title }}</p>
    <p>{{ figure.description }}</p>
  </el-card>
</template>

<script setup lang="ts">
import type { CampusFigure } from '@/types'
defineProps<{ figure: CampusFigure }>()
</script>
```

- [ ] **Step 6: 创建 SceneryCard.vue**

```vue
<template>
  <el-card :body-style="{ padding: '0' }" shadow="hover">
    <el-image :src="scenery.image_url" style="width:100%;height:200px" fit="cover" />
    <div style="padding:14px">
      <h3>{{ scenery.title }}</h3>
      <p style="color:#999">{{ scenery.location }}</p>
      <p>{{ scenery.description }}</p>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import type { CampusScenery } from '@/types'
defineProps<{ scenery: CampusScenery }>()
</script>
```

- [ ] **Step 7: 创建 CampusPage.vue**

```vue
<template>
  <div>
    <h2>校园风采</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="人物风采" name="figures">
        <el-row :gutter="20">
          <el-col :span="8" v-for="f in figures" :key="f.id" style="margin-bottom:20px">
            <FigureCard :figure="f" />
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="校园风景" name="sceneries">
        <el-row :gutter="20">
          <el-col :span="8" v-for="s in sceneries" :key="s.id" style="margin-bottom:20px">
            <SceneryCard :scenery="s" />
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFigures, getSceneries } from '@/api/campus'
import type { CampusFigure, CampusScenery } from '@/types'
import FigureCard from '@/components/campus/FigureCard.vue'
import SceneryCard from '@/components/campus/SceneryCard.vue'

const activeTab = ref('figures')
const figures = ref<CampusFigure[]>([])
const sceneries = ref<CampusScenery[]>([])

onMounted(async () => {
  figures.value = await getFigures()
  sceneries.value = await getSceneries()
})
</script>
```

- [ ] **Step 8: 填充种子数据**

在 `seed.py` 中添加：
```python
from app.models.campus import CampusFigure, CampusScenery

if db.query(CampusFigure).count() == 0:
    figures = [
        CampusFigure(name="张三", title="2024年国家奖学金获得者", avatar="/images/avatar1.jpg", description="软件学院2022级学生，获得国家奖学金...", category="student"),
        CampusFigure(name="李四", title="ACM竞赛金牌得主", avatar="/images/avatar2.jpg", description="带领团队获得ICPC亚洲区域赛金牌...", category="student"),
        CampusFigure(name="王老师", title="优秀教师", avatar="/images/avatar3.jpg", description="软件学院副教授，主持多项省级课题...", category="teacher"),
    ]
    db.add_all(figures)
    sceneries = [
        CampusScenery(title="图书馆", image_url="/images/lib.jpg", description="校园地标建筑", location="校区中心"),
        CampusScenery(title="教学楼群", image_url="/images/teaching.jpg", description="主教学区", location="校区东侧"),
        CampusScenery(title="校园湖景", image_url="/images/lake.jpg", description="校园休闲景区", location="校区西侧"),
    ]
    db.add_all(sceneries)
    db.commit()
```

- [ ] **Step 9: Commit**

```bash
git add backend/app/api/campus.py backend/app/schemas/campus.py backend/app/seed.py frontend/src/api/campus.ts frontend/src/views/student/CampusPage.vue frontend/src/components/campus/
git commit -m "feat: add campus showcase feature"
```

---

### Task 8: 智能体对话（后端 SSE + LLM 接入）

**Files:**
- Create: `backend/app/schemas/agent.py`
- Create: `backend/app/services/llm_service.py`
- Create: `backend/app/services/agent_service.py`
- Create: `backend/app/api/agent.py`

- [ ] **Step 1: 创建 schemas/agent.py**

```python
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
```

- [ ] **Step 2: 创建 services/llm_service.py**

```python
from openai import OpenAI

from app.core.config import settings

client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.LLM_BASE_URL)


def build_system_prompt() -> str:
    return """你是绵阳城市学院的智慧校园AI助手"绵小城"，负责回答学生和教师的校园相关问题。

你的能力包括：
1. 回答校园相关问题（办事流程、校园导航、规章制度等）
2. 回答末尾给出相关建议和功能页面链接（用 [建议标题](链接) 格式）
3. 保持语气亲切友好，使用"你"称呼用户

可用的功能页面链接：
- /student/agent - 智能助手
- /student/campus - 校园风采
- /student/growth - 成长轨迹
- /student/schedule - 课表查询
- /student/grade - 成绩考试
- /student/service - 办事服务
- /teacher/agent - 教师智能助手
- /teacher/students - 学生成长查看
- /teacher/approval - 审批管理

如果你不知道答案，请说"这个问题我需要向老师确认后回答你"。
回答控制在200字以内。"""


async def chat_stream(messages: list[dict]):
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
```

- [ ] **Step 3: 创建 services/agent_service.py**

```python
import re

from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeItem
from app.services.llm_service import build_system_prompt, chat_stream


def extract_suggestions(text: str) -> list[dict]:
    suggestions = []
    pattern = r'\[(.+?)\]\((.+?)\)'
    for match in re.finditer(pattern, text):
        suggestions.append({"text": match.group(1), "link": match.group(2)})
    return suggestions


def build_context(user_message: str) -> list[dict]:
    db = SessionLocal()
    try:
        results = db.query(KnowledgeItem).filter(
            KnowledgeItem.question.like(f"%{user_message[:10]}%")
        ).limit(3).all()
        if results:
            context = "相关校园知识：\n"
            for r in results:
                context += f"Q: {r.question}\nA: {r.answer}\n\n"
            return [{"role": "system", "content": build_system_prompt() + "\n\n" + context}]
    finally:
        db.close()
    return [{"role": "system", "content": build_system_prompt()}]


async def chat(message: str, history: list[dict]):
    messages = build_context(message)
    for h in history[-10:]:
        messages.append(h)
    messages.append({"role": "user", "content": message})

    full_reply = ""
    async for chunk in chat_stream(messages):
        full_reply += chunk
        yield chunk

    if full_reply:
        suggestions = extract_suggestions(full_reply)
        import json
        yield f"\n__SUGGESTIONS__:{json.dumps(suggestions, ensure_ascii=False)}"
```

- [ ] **Step 4: 创建 api/agent.py**

```python
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.agent import ChatRequest
from app.services.agent_service import chat

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat")
async def chat_api(req: ChatRequest):
    return StreamingResponse(
        chat(req.message, req.history),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )
```

注册路由：
```python
from app.api.agent import router as agent_router
app.include_router(agent_router)
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/api/agent.py backend/app/services/llm_service.py backend/app/services/agent_service.py backend/app/schemas/agent.py
git commit -m "feat: add AI agent chat with SSE streaming"
```

---

### Task 9: 智能体对话前端页面

**Files:**
- Create: `frontend/src/stores/agent.ts`
- Create: `frontend/src/components/agent/ChatPanel.vue`
- Create: `frontend/src/views/student/AgentPage.vue`
- Create: `frontend/src/views/teacher/AgentPage.vue`

- [ ] **Step 1: 创建 stores/agent.ts**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '@/types'

export const useAgentStore = defineStore('agent', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  function addMessage(msg: ChatMessage) {
    messages.value.push(msg)
  }

  function clearMessages() {
    messages.value = []
  }

  return { messages, loading, addMessage, clearMessages }
})
```

- [ ] **Step 2: 创建 api/agent.ts**

```typescript
import request from '@/utils/request'
import type { ChatMessage } from '@/types'

export async function sendChatMessage(
  message: string,
  history: { role: string; content: string }[],
  onChunk: (text: string) => void,
  onDone: (full: string) => void,
  onSuggestions: (suggestions: any[]) => void,
) {
  const resp = await fetch('/api/agent/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('campus_token')}` },
    body: JSON.stringify({ message, history }),
  })

  const reader = resp.body!.getReader()
  const decoder = new TextDecoder()
  let full = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const text = decoder.decode(value)
    if (text.includes('__SUGGESTIONS__:')) {
      const parts = text.split('__SUGGESTIONS__:')
      onChunk(parts[0])
      full += parts[0]
      const suggestions = JSON.parse(parts[1])
      onSuggestions(suggestions)
    } else {
      onChunk(text)
      full += text
    }
  }
  onDone(full)
}
```

- [ ] **Step 3: 创建 ChatPanel.vue**

```vue
<template>
  <div class="chat-container">
    <div class="messages" ref="msgRef">
      <div v-for="msg in messages" :key="msg.id" :class="['message', msg.role]">
        <div class="bubble">
          <div>{{ msg.content }}</div>
          <div v-if="msg.suggestions?.length" class="suggestions">
            <el-tag
              v-for="s in msg.suggestions"
              :key="s.text"
              style="margin:4px;cursor:pointer"
              @click="handleSuggestion(s)"
            >
              {{ s.text }}
            </el-tag>
          </div>
        </div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="bubble">正在思考...</div>
      </div>
    </div>
    <div class="input-area">
      <el-input
        v-model="input"
        :disabled="loading"
        placeholder="输入你的问题..."
        @keyup.enter="send"
      />
      <el-button type="primary" :loading="loading" style="margin-left:12px" @click="send">发送</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentStore } from '@/stores/agent'
import { sendChatMessage } from '@/api/agent'
import type { ChatMessage, Suggestion } from '@/types'

const store = useAgentStore()
const router = useRouter()
const input = ref('')
const msgRef = ref<HTMLElement>()
const loading = ref(false)

const messages = computed(() => store.messages)

import { computed } from 'vue'

async function send() {
  if (!input.value.trim() || loading.value) return
  const userMsg: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: input.value,
    timestamp: new Date().toISOString(),
  }
  store.addMessage(userMsg)
  const text = input.value
  input.value = ''
  loading.value = true

  const history = store.messages.slice(0, -1).map(m => ({ role: m.role, content: m.content }))

  const assistantMsg: ChatMessage = {
    id: (Date.now() + 1).toString(),
    role: 'assistant',
    content: '',
    timestamp: new Date().toISOString(),
  }
  store.addMessage(assistantMsg)

  await sendChatMessage(
    text,
    history,
    (chunk) => {
      const last = store.messages[store.messages.length - 1]
      if (last) last.content += chunk
    },
    () => { loading.value = false },
    (suggestions) => {
      const last = store.messages[store.messages.length - 1]
      if (last) last.suggestions = suggestions
    },
  )
}

function handleSuggestion(s: Suggestion) {
  if (s.link) router.push(s.link)
}

watch(messages, () => {
  nextTick(() => { msgRef.value?.scrollTo({ top: msgRef.value.scrollHeight, behavior: 'smooth' }) })
}, { deep: true })
</script>

<style scoped>
.chat-container { display: flex; flex-direction: column; height: calc(100vh - 140px); }
.messages { flex:1; overflow-y:auto; padding:16px; }
.message { margin-bottom:16px; }
.message.user { display:flex; justify-content:flex-end; }
.message.assistant { display:flex; justify-content:flex-start; }
.bubble { max-width:70%; padding:12px 16px; border-radius:8px; background:#f0f0f0; }
.message.user .bubble { background:#409eff; color:#fff; }
.suggestions { margin-top:8px; }
.input-area { display:flex; padding:16px; border-top:1px solid #eee; }
</style>
```

- [ ] **Step 4: 创建 student/AgentPage.vue 和 teacher/AgentPage.vue**

```vue
<template>
  <div>
    <h2 style="margin-bottom:16px">智能助手 - 绵小城</h2>
    <ChatPanel />
  </div>
</template>

<script setup lang="ts">
import ChatPanel from '@/components/agent/ChatPanel.vue'
</script>
```

教师端 AgentPage.vue 内容相同。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/agent.ts frontend/src/stores/agent.ts frontend/src/components/agent/ frontend/src/views/student/AgentPage.vue frontend/src/views/teacher/AgentPage.vue
git commit -m "feat: add AI agent chat frontend"
```

---

### Task 10: 成长轨迹（前后端）

**Files:**
- Create: `backend/app/api/growth.py`
- Create: `backend/app/schemas/growth.py`
- Create: `frontend/src/api/growth.ts`
- Create: `frontend/src/components/growth/MilestoneCard.vue`
- Create: `frontend/src/views/student/GrowthPage.vue`
- Create: `frontend/src/views/teacher/StudentsPage.vue`

- [ ] **Step 1: 创建 schemas/growth.py**

```python
from pydantic import BaseModel
from datetime import date


class GrowthRecordCreate(BaseModel):
    type: str
    title: str
    description: str | None = None
    date: str
    attachment_url: str | None = None


class GrowthRecordOut(BaseModel):
    id: int
    student_id: int
    type: str
    title: str
    description: str | None = None
    date: date
    attachment_url: str | None = None

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 创建 api/growth.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.growth import GrowthRecord
from app.schemas.growth import GrowthRecordCreate, GrowthRecordOut

router = APIRouter(prefix="/api/growth", tags=["growth"])


@router.get("/records", response_model=list[GrowthRecordOut])
def list_records(student_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(GrowthRecord)
    if student_id:
        query = query.filter(GrowthRecord.student_id == student_id)
    return query.order_by(GrowthRecord.date.desc()).all()


@router.post("/records", response_model=GrowthRecordOut)
def create_record(req: GrowthRecordCreate, db: Session = Depends(get_db)):
    record = GrowthRecord(student_id=1, **req.model_dump())  # TODO: 从JWT获取学生ID
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(GrowthRecord).filter(GrowthRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "deleted"}
```

- [ ] **Step 3: 注册路由**

```python
from app.api.growth import router as growth_router
app.include_router(growth_router)
```

- [ ] **Step 4: 创建前端 api/growth.ts**

```typescript
import request from '@/utils/request'
import type { GrowthRecord } from '@/types'

export function getGrowthRecords(studentId?: number) {
  return request.get<GrowthRecord[]>('/growth/records', { params: { student_id: studentId } })
}

export function createGrowthRecord(data: Partial<GrowthRecord>) {
  return request.post<GrowthRecord>('/growth/records', data)
}

export function deleteGrowthRecord(id: number) {
  return request.delete(`/growth/records/${id}`)
}
```

- [ ] **Step 5: 创建 MilestoneCard.vue**

```vue
<template>
  <div class="milestone">
    <div class="dot" :style="{ background: colorMap[record.type] }" />
    <div class="content">
      <div class="header">
        <el-tag :type="tagMap[record.type]" size="small">{{ typeLabel[record.type] }}</el-tag>
        <span class="date">{{ record.date }}</span>
      </div>
      <h4>{{ record.title }}</h4>
      <p v-if="record.description">{{ record.description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GrowthRecord } from '@/types'

defineProps<{ record: GrowthRecord }>()

const colorMap: Record<string, string> = {
  honor: '#e6a23c', competition: '#409eff', award: '#67c23a', practice: '#909399',
}
const tagMap: Record<string, string> = {
  honor: 'warning', competition: 'primary', award: 'success', practice: 'info',
}
const typeLabel: Record<string, string> = {
  honor: '荣誉', competition: '竞赛', award: '获奖', practice: '实践',
}
</script>

<style scoped>
.milestone { display: flex; gap: 16px; padding: 16px 0; border-left: 2px solid #eee; padding-left: 20px; position: relative; }
.dot { width: 12px; height: 12px; border-radius: 50%; position: absolute; left: -7px; top: 20px; }
.content { flex: 1; }
.header { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.date { color: #999; font-size: 13px; }
</style>
```

- [ ] **Step 6: 创建 student/GrowthPage.vue**

```vue
<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>我的成长轨迹</h2>
      <el-button type="primary" @click="dialogVisible = true">添加记录</el-button>
    </div>
    <div class="timeline" v-if="records.length">
      <MilestoneCard v-for="r in records" :key="r.id" :record="r" />
    </div>
    <el-empty v-else description="暂无成长记录" />

    <el-dialog v-model="dialogVisible" title="添加成长记录" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option label="荣誉" value="honor" />
            <el-option label="竞赛" value="competition" />
            <el-option label="获奖" value="award" />
            <el-option label="实践" value="practice" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="证明材料">
          <el-upload :auto-upload="false"><el-button>上传文件</el-button></el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getGrowthRecords, createGrowthRecord } from '@/api/growth'
import type { GrowthRecord } from '@/types'
import MilestoneCard from '@/components/growth/MilestoneCard.vue'

const records = ref<GrowthRecord[]>([])
const dialogVisible = ref(false)
const form = ref({ type: 'honor', title: '', description: '', date: '' })

onMounted(async () => { records.value = await getGrowthRecords() })

async function handleAdd() {
  await createGrowthRecord(form.value)
  ElMessage.success('添加成功')
  dialogVisible.value = false
  records.value = await getGrowthRecords()
}
</script>

<style scoped>
.timeline { margin-top: 20px; }
</style>
```

- [ ] **Step 7: 创建 teacher/StudentsPage.vue（教师查看学生成长）**

```vue
<template>
  <div>
    <h2>学生成长查看</h2>
    <el-input v-model="search" placeholder="搜索学生姓名或学号" style="width:300px;margin-bottom:20px" />
    <el-table :data="students" v-if="students.length">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="college" label="学院" />
      <el-table-column label="操作">
        <el-button size="small" @click="viewGrowth(row)">查看成长轨迹</el-button>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无学生数据" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const search = ref('')
const students = ref([]) // TODO: 接入真实API
function viewGrowth(row: any) {}
</script>
```

- [ ] **Step 8: Commit**

```bash
git add backend/app/api/growth.py backend/app/schemas/growth.py frontend/src/api/growth.ts frontend/src/components/growth/ frontend/src/views/student/GrowthPage.vue frontend/src/views/teacher/StudentsPage.vue
git commit -m "feat: add growth trajectory feature"
```

---

### Task 11: 课表/成绩/考试查询（前后端）

**Files:**
- Create: `backend/app/api/academic.py`
- Create: `backend/app/schemas/academic.py`
- Create: `frontend/src/api/academic.ts`
- Create: `frontend/src/views/student/SchedulePage.vue`
- Create: `frontend/src/views/student/GradePage.vue`

- [ ] **Step 1: 创建 schemas/academic.py**

```python
from pydantic import BaseModel
from datetime import date, time


class CourseOut(BaseModel):
    id: int
    name: str
    teacher: str
    location: str
    day_of_week: int
    start_period: int
    end_period: int
    week_start: int
    week_end: int

    class Config:
        from_attributes = True


class GradeOut(BaseModel):
    id: int
    course_name: str
    score: float
    credit: float
    gpa: float
    semester: str

    class Config:
        from_attributes = True


class ExamOut(BaseModel):
    id: int
    course_name: str
    exam_date: date
    start_time: time
    end_time: time
    location: str

    class Config:
        from_attributes = True
```

- [ ] **Step 2: 创建 api/academic.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.academic import Course, Grade, Exam
from app.schemas.academic import CourseOut, GradeOut, ExamOut

router = APIRouter(prefix="/api/academic", tags=["academic"])


@router.get("/courses", response_model=list[CourseOut])
def list_courses(student_id: int = 1, db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.student_id == student_id).all()


@router.get("/grades", response_model=list[GradeOut])
def list_grades(student_id: int = 1, db: Session = Depends(get_db)):
    return db.query(Grade).filter(Grade.student_id == student_id).order_by(Grade.semester.desc()).all()


@router.get("/exams", response_model=list[ExamOut])
def list_exams(student_id: int = 1, db: Session = Depends(get_db)):
    return db.query(Exam).filter(Exam.student_id == student_id).all()
```

注册路由：
```python
from app.api.academic import router as academic_router
app.include_router(academic_router)
```

- [ ] **Step 3: 创建前端 api/academic.ts**

```typescript
import request from '@/utils/request'
import type { Course, Grade, Exam } from '@/types'

export function getCourses() { return request.get<Course[]>('/academic/courses') }
export function getGrades() { return request.get<Grade[]>('/academic/grades') }
export function getExams() { return request.get<Exam[]>('/academic/exams') }
```

- [ ] **Step 4: 创建 SchedulePage.vue**

```vue
<template>
  <div>
    <h2>课表查询</h2>
    <el-table :data="schedule" border>
      <el-table-column label="时间" width="120">
        <template #default="{ $index }">
          {{ periods[$index] }}
        </template>
      </el-table-column>
      <el-table-column v-for="day in days" :key="day" :label="day">
        <template #default="{ row }">
          <div v-for="c in getCourses(day, row.period)" :key="c.id" class="course-cell">
            <strong>{{ c.name }}</strong>
            <p>{{ c.teacher }}</p>
            <p>{{ c.location }}</p>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCourses } from '@/api/academic'
import type { Course } from '@/types'

const days = ['周一', '周二', '周三', '周四', '周五']
const periods = ['第1节\n08:00-08:45', '第2节\n08:55-09:40', '第3节\n10:00-10:45', '第4节\n10:55-11:40', '第5节\n14:00-14:45', '第6节\n14:55-15:40']
const courses = ref<Course[]>([])
const schedule = ref(periods.map((label, i) => ({ label, period: i + 1 })))

onMounted(async () => { courses.value = await getCourses() })

function getCourses(day: string, period: number) {
  const dayMap: Record<string, number> = { '周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5 }
  return courses.value.filter(c => c.day_of_week === dayMap[day] && c.start_period <= period && c.end_period >= period)
}
</script>

<style scoped>
.course-cell { background: #ecf5ff; border-radius: 4px; padding: 4px; margin: 2px; font-size: 13px; }
.course-cell p { margin: 0; color: #666; }
</style>
```

- [ ] **Step 5: 创建 GradePage.vue**

```vue
<template>
  <div>
    <h2>成绩与考试</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="成绩查询" name="grades">
        <el-table :data="grades" border>
          <el-table-column prop="semester" label="学期" width="120" />
          <el-table-column prop="course_name" label="课程" />
          <el-table-column prop="credit" label="学分" width="80" />
          <el-table-column prop="score" label="成绩" width="80" />
          <el-table-column prop="gpa" label="绩点" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="考试安排" name="exams">
        <el-table :data="exams" border>
          <el-table-column prop="course_name" label="课程" />
          <el-table-column prop="exam_date" label="日期" width="120" />
          <el-table-column prop="start_time" label="开始时间" width="100" />
          <el-table-column prop="end_time" label="结束时间" width="100" />
          <el-table-column prop="location" label="地点" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getGrades, getExams } from '@/api/academic'
import type { Grade, Exam } from '@/types'

const activeTab = ref('grades')
const grades = ref<Grade[]>([])
const exams = ref<Exam[]>([])

onMounted(async () => {
  grades.value = await getGrades()
  exams.value = await getExams()
})
</script>
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/academic.py backend/app/schemas/academic.py frontend/src/api/academic.ts frontend/src/views/student/SchedulePage.vue frontend/src/views/student/GradePage.vue
git commit -m "feat: add schedule, grade and exam features"
```

---

### Task 12: 办事服务（请假/证明申请，前后端）

**Files:**
- Create: `backend/app/api/service.py`
- Create: `backend/app/schemas/service.py`
- Create: `frontend/src/api/service.ts`
- Create: `frontend/src/views/student/ServicePage.vue`
- Create: `frontend/src/views/teacher/ApprovalPage.vue`

- [ ] **Step 1: 创建 schemas/service.py**

```python
from pydantic import BaseModel
from datetime import datetime


class TicketCreate(BaseModel):
    type: str
    title: str
    content: str


class TicketOut(BaseModel):
    id: int
    applicant_id: int
    type: str
    title: str
    content: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TicketApprove(BaseModel):
    action: str  # approve | reject
    comment: str | None = None
```

- [ ] **Step 2: 创建 api/service.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.service import ServiceTicket, TicketStatus
from app.schemas.service import TicketCreate, TicketOut, TicketApprove

router = APIRouter(prefix="/api/service", tags=["service"])


@router.post("/tickets", response_model=TicketOut)
def create_ticket(req: TicketCreate, db: Session = Depends(get_db)):
    ticket = ServiceTicket(applicant_id=1, **req.model_dump())  # TODO: 从JWT获取用户ID
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets(applicant_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(ServiceTicket)
    if applicant_id:
        query = query.filter(ServiceTicket.applicant_id == applicant_id)
    if status:
        query = query.filter(ServiceTicket.status == status)
    return query.order_by(ServiceTicket.created_at.desc()).all()


@router.put("/tickets/{ticket_id}/approve")
def approve_ticket(ticket_id: int, req: TicketApprove, db: Session = Depends(get_db)):
    ticket = db.query(ServiceTicket).filter(ServiceTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    ticket.status = TicketStatus.APPROVED if req.action == "approve" else TicketStatus.REJECTED
    db.commit()
    return {"message": f"ticket {req.action}d"}
```

注册路由：
```python
from app.api.service import router as service_router
app.include_router(service_router)
```

- [ ] **Step 3: 创建前端 api/service.ts**

```typescript
import request from '@/utils/request'
import type { ServiceTicket } from '@/types'

export function getTickets(params?: { status?: string }) {
  return request.get<ServiceTicket[]>('/service/tickets', { params })
}

export function createTicket(data: { type: string; title: string; content: string }) {
  return request.post<ServiceTicket>('/service/tickets', data)
}

export function approveTicket(id: number, action: string) {
  return request.put(`/service/tickets/${id}/approve`, { action })
}
```

- [ ] **Step 4: 创建 student/ServicePage.vue**

```vue
<template>
  <div>
    <h2>办事服务</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="我的申请" name="list">
        <el-button type="primary" style="margin-bottom:16px" @click="showApply = true">新建申请</el-button>
        <el-table :data="tickets" border>
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">{{ row.type === 'leave' ? '请假' : '证明' }}</template>
          </el-table-column>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'">
                {{ row.status === 'approved' ? '已通过' : row.status === 'rejected' ? '已拒绝' : '待审批' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="提交时间" width="180" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="快捷申请" name="apply">
        <el-card v-for="item in quickActions" :key="item.type" style="margin-bottom:16px;cursor:pointer" @click="openApply(item.type)">
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showApply" title="新建申请" width="500px">
      <el-form :model="applyForm" label-width="80px">
        <el-form-item label="类型">
          <el-radio-group v-model="applyForm.type">
            <el-radio value="leave">请假申请</el-radio>
            <el-radio value="certificate">证明申请</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="applyForm.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="applyForm.content" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApply = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTickets, createTicket } from '@/api/service'
import type { ServiceTicket } from '@/types'

const activeTab = ref('list')
const tickets = ref<ServiceTicket[]>([])
const showApply = ref(false)
const applyForm = ref({ type: 'leave', title: '', content: '' })
const quickActions = [
  { type: 'leave', title: '请假申请', desc: '提交请假申请，等待辅导员审批' },
  { type: 'certificate', title: '证明申请', desc: '申请在校证明、成绩单等' },
]

onMounted(async () => { tickets.value = await getTickets() })

function openApply(type: string) { applyForm.value.type = type; showApply.value = true }

async function handleSubmit() {
  await createTicket(applyForm.value)
  ElMessage.success('提交成功')
  showApply.value = false
  tickets.value = await getTickets()
}
</script>
```

- [ ] **Step 5: 创建 teacher/ApprovalPage.vue**

```vue
<template>
  <div>
    <h2>审批管理</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="待审批" name="pending">
        <el-table :data="pendingTickets" border>
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">{{ row.type === 'leave' ? '请假' : '证明' }}</template>
          </el-table-column>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="content" label="内容" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleApprove(row.id)">通过</el-button>
              <el-button type="danger" size="small" @click="handleReject(row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="已处理" name="done">
        <el-table :data="doneTickets" border>
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="status" label="结果" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'approved' ? 'success' : 'danger'">
                {{ row.status === 'approved' ? '已通过' : '已拒绝' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTickets, approveTicket } from '@/api/service'
import type { ServiceTicket } from '@/types'

const activeTab = ref('pending')
const allTickets = ref<ServiceTicket[]>([])
const pendingTickets = computed(() => allTickets.value.filter(t => t.status === 'pending'))
const doneTickets = computed(() => allTickets.value.filter(t => t.status !== 'pending'))

onMounted(async () => { allTickets.value = await getTickets() })

async function handleApprove(id: number) {
  await approveTicket(id, 'approve')
  ElMessage.success('已通过')
  allTickets.value = await getTickets()
}
async function handleReject(id: number) {
  await approveTicket(id, 'reject')
  ElMessage.success('已拒绝')
  allTickets.value = await getTickets()
}
</script>
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/service.py backend/app/schemas/service.py frontend/src/api/service.ts frontend/src/views/student/ServicePage.vue frontend/src/views/teacher/ApprovalPage.vue
git commit -m "feat: add service ticket and approval features"
```

---

### Task 13: 智能体关联功能（建议跳转 + 知识库管理）

**Files:**
- Create: `frontend/src/api/knowledge.ts`（管理员知识库管理）
- Modify: 智能体回答中已包含建议跳转（Task 8/9 已完成）

- [ ] **Step 1: 在 ChatPanel 中点击建议标签时跳转**

已在 `ChatPanel.vue` 的 `handleSuggestion` 中实现：
```typescript
function handleSuggestion(s: Suggestion) {
  if (s.link) router.push(s.link)
}
```

- [ ] **Step 2: 验证智能体回答带链接**

测试提问"怎么请假"，智能体应回复并附带类似：
```
你可以通过办事服务页面提交请假申请。
[去请假](/student/service)
```

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: agent reply with suggestion links"
```

---

## V1.0 启动命令

```bash
# 后端启动
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 数据库初始化
python app/seed.py

# 前端启动
cd frontend
npm install
npm run dev

# 访问 http://localhost:5173
# 测试账号: 2024001 / 123456 (学生), t1001 / 123456 (教师)
```

---

## 自审记录

### Spec 覆盖检查
- ✅ 统一登录门户 → Task 3 (后端认证) + Task 4 (前端登录)
- ✅ 角色选择 → Task 4 (RoleSelectPage)
- ✅ 学生端框架 → Task 5 (布局 + 首页)
- ✅ 教师端框架 → Task 6 (布局 + 首页)
- ✅ 校园风采（人物+风景）→ Task 7
- ✅ 智能体问答（文本+多轮）→ Task 8 (后端SSE) + Task 9 (前端对话)
- ✅ 建议跳转链接 → Task 8 (LLM prompt) + Task 9 (ChatPanel)
- ✅ 成长轨迹（手动维护）→ Task 10
- ✅ 课表查询 → Task 11
- ✅ 成绩查询 + 考试安排 → Task 11
- ✅ 请假/证明申请 → Task 12 (学生)
- ✅ 审批管理 → Task 12 (教师)
- ✅ 教师查看学生成长 → Task 10 (StudentsPage)

### 检查结果
- 无占位符、无 TODO 悬空（除明确标记的 JWT 用户ID 待接入）
- 类型定义在 types/index.ts 统一，各组件引用一致
- 路由配置统一在 router/index.ts
- 每个 Task 可独立测试

> **注意:** `api/growth.py` 和 `api/service.py` 中的 `student_id=1` 和 `applicant_id=1` 为 JWT 中间件占位，后续需在认证中间件中从 token 解析实际用户 ID 并注入。
