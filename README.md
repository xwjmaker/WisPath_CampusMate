# 智慧校园AI服务平台 (Smart Campus AI)

绵阳城市学院智慧校园 AI 服务平台，提供校园信息查询、AI 对话助手、学生成长档案、教师管理等一体化服务。

## 技术栈

### 后端
- **框架:** Python FastAPI
- **ORM:** SQLAlchemy + Pydantic
- **数据库:** MySQL (mysql+pymysql)
- **AI:** 阿里云通义千问 DashScope (默认)，.env 可覆盖（当前为 `mimo-v2.5` via token-plan）
- **认证:** JWT (python-jose, passlib)

### 前端
- **框架:** Vue 3 (Composition API) + TypeScript
- **构建:** Vite 5
- **UI 库:** Element Plus
- **状态管理:** Pinia
- **图表:** ECharts + vue-echarts
- **网络:** Axios

## 快速开始

### 环境要求
- Python >= 3.11
- Node.js >= 18
- MySQL 8.0+

### 后端

```bash
# 进入后端目录
cd mianyang-campus/backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（编辑 .env）
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/smart_campus
# LLM_API_KEY=your-dashscope-api-key

# 初始化数据库（会自动建表）
python -m app.seed

# 启动开发服务器
uvicorn app.main:app --reload
```

### 前端

```bash
# 进入前端目录
cd mianyang-campus/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev        # 默认 :5173，代理 /api → :8000

# 构建生产版本
npm run build      # vue-tsc 类型检查 + Vite 构建
```

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 学生 | 2024001 | 123456 |
| 教师 | t1001 | 123456 |
| 管理员 | admin | admin123 |

## 功能模块

### 学生端
- **AI 助手** — 绵小城智能对话，支持语音输入、文件上传、项目式对话
- **成长档案** — 成长记录（荣誉/竞赛/实践/论文/成果）、技能与兴趣标签、项目展示、综合评分雷达图
- **课表查询** — 查看学期课程安排
- **成绩查询** — 查看各科成绩与 GPA
- **校园风采** — 校园风景图片浏览
- **办事服务** — 在线申请服务
- **请假申请** — 提交请假审批

### 教师端
- **班级首页** — 班级概览、综合评分统计
- **AI 助手** — 绵小城智能对话（教师专项）
- **学生管理** — 名下学生列表、综合评分、成长档案详情查看（含危机预警和请假记录）
- **审批管理** — 请假申请审批
- **消息管理** — 与学生实时通信（WebSocket）

### 通用
- **校园知识库** — 办事流程、规章制度问答
- **官网通知** — 教务处最新公告
- **危机预警** — 基于对话分析的 AI 心理预警（严重/中等/轻微三级）

## API 路由总览

| 前缀 | 模块 | 说明 |
|------|------|------|
| `/api/auth` | auth | 登录注册 |
| `/api/agent/chat` | agent | AI 助手 SSE 流式聊天 |
| `/api/campus` | campus | 校园服务 |
| `/api/growth` | growth | 成长档案 CRUD |
| `/api/academic` | academic | 学业管理 |
| `/api/service` | service | 服务大厅 |
| `/api/leave` | leave | 请假审批 |
| `/api/crisis` | crisis | 危机预警 |
| `/api/teacher` | teacher | 教师端接口 |
| `/api/upload` | upload | 文件上传 |
| `/api/conversations` | conversations | 对话历史 |
| `/api/messages` | messages | 消息管理 + WebSocket |
| `/api/announcement` | announcement | 公告通知 |
| `/api/admin` | admin | 管理后台 |
| `/api/notification` | notification | 通知管理 |
| `/api/feedback` | feedback | 反馈管理 |
| `/api/setting` | setting | 系统设置 |
| `/api/grade-analysis` | grade_analysis | 成绩分析 |
| `/api/profile` | profile | 个人资料 |

## 项目结构

```
mianyang-campus/
├── backend/
│   └── app/
│       ├── main.py          # 入口，注册路由
│       ├── seed.py           # 种子数据
│       ├── api/              # 路由层（13 个模块）
│       ├── core/             # 核心配置（数据库、依赖注入）
│       ├── models/           # SQLAlchemy 模型（26 张表）
│       ├── schemas/          # Pydantic 数据模式
│       └── services/         # 业务逻辑（auth、agent、llm、scoring、ws）
├── frontend/
│   └── src/
│       ├── main.ts           # Vue 入口
│       ├── router/           # 路由配置 + 守卫
│       ├── stores/           # Pinia 状态管理
│       ├── api/              # API 请求封装
│       ├── components/       # 通用组件
│       ├── composables/      # 组合式函数
│       ├── views/            # 页面组件
│       └── types/            # TypeScript 类型定义
└── docs/                     # 设计文档
```
