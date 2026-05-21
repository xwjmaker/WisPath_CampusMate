# MianMate — 智慧校园AI服务平台 (绵阳城市学院)

## 项目环境

- **环境管理:** conda，环境名 `mianyang`
- **Conda 路径:** `D:\anaconda\condabin\conda.bat`
- **后端:** Python FastAPI（`mianyang-campus/backend/`）
- **前端:** Vue 3 + TypeScript + Vite（`mianyang-campus/frontend/`）

## 启动命令

```bash
# 激活 conda 环境
conda activate mianyang

# 后端（mianyang-campus/backend/）
uvicorn app.main:app --reload          # 开发，默认 :8000

# 前端（mianyang-campus/frontend/）
npm run dev                            # 开发，:5173，代理 /api → :8000
npm run build                          # vue-tsc 类型检查 + Vite 构建
```

## 数据库

- **引擎:** PostgreSQL，数据库名 `smart_campus`（见 `backend/.env`）
- **迁移:** 暂无 Alembic，使用 `Base.metadata.create_all()`
- **种子数据:**
  ```bash
  cd mianyang-campus/backend && python -m app.seed
  ```
- **测试账号:** `2024001` / `123456`（学生），`t1001` / `123456`（教师），`admin` / `admin123`

## 项目结构

- `backend/app/main.py` — FastAPI 入口，注册 6 个路由模块
- `backend/app/api/` — 6 个路由：auth, agent(SSE), campus, growth, academic, service
- `backend/app/models/` — SQLAlchemy 模型（users, knowledge_base, campus_figures 等 7 张表）
- `backend/app/services/` — 业务逻辑（auth, agent, llm）
- `frontend/src/main.ts` — Vue 入口，挂载 Pinia + Router + Element Plus
- `frontend/src/router/index.ts` — 路由守卫（除 /login 外均需 JWT）
- `frontend/src/utils/request.ts` — Axios 实例，自动附加 JWT token

## LLM 配置

- **提供商:** 阿里云通义千问 DashScope（兼容 OpenAI SDK）
- **模型:** `qwen-turbo`
- **AI 助手名:** 绵小城
- SSE 流式聊天：`POST /api/agent/chat`

## 注意事项

- 前端 `@` 别名映射到 `src/`
- 后端无测试，前端无测试框架 / linter / formatter
- 教师端页面和学生子页面（schedule, grade, service）尚未实现
- API 路径统一前缀 `/api`
