# 教师端门户增强设计方案

## 概述

对教师端进行全面的 UI/UX 升级和功能增强，涵盖布局美化、审批管理智能化、学生成长档案增强、师生消息系统、以及智能助手集成。

## 1. 布局改造 — TeacherLayout.vue

### 侧边栏
- 顶部展示校徽（`/images/校徽.png`）+ 校训"博学、笃行、严谨、创新"
- 菜单项：预警雷达、智能助手、审批管理、学生成长、消息
- 底部显示用户头像 + 姓名，点击弹出下拉菜单（仅包含"退出登录"）

### 顶部栏
- 右侧显示用户头像 + 姓名
- 左侧显示当前页面标题
- 点击姓名/头像弹出下拉菜单 → 退出登录

## 2. 智能助手 — AgentPage.vue

- 使用 `ChatShell` + `Sidebar` 完整模式，与 student 端架构一致
- 快捷入口卡片适配教师端：请假审批、预警管理、学生档案、危机干预
- 教师端消息存储使用 `useTeacherAgentStore`
- 页面标题："智能助手 - 绵小城"

## 3. 审批管理 — ApprovalPage.vue

### Tab 结构
- **待审批**：请假 + 办事申请列表，每条显示 AI 分析结果
- **已通过**：历史已批准记录，含审批人 + 时间
- **已拒绝**：历史已拒绝记录，含拒绝理由 + 时间

### AI 审批分析
- 页面加载时自动对每条待批项调用 LLM 分析（通过 agent/chat 端点）
- 显示分析结果在每条记录旁（绿色通过建议/红色拒绝建议 + 理由）
- AI 分析触发：页面加载自动分析，避免阻塞 UI

### 待批项展示
- 学生姓名、类型、日期范围、原因
- AI 分析结论（自动加载）
- 通过/拒绝 按钮
- 拒绝理由对话框

### 已通过/已拒绝
- 展示历史记录

## 4. 学生成长档案 — StudentsPage.vue

### 默认加载
- 进入页面时自动加载教师名下所有学生

### 学生卡片
- 头像、姓名、学院
- 危机等级标签
- 成果数量（成长记录数）
- 综合评分（百分制，颜色分级：>=90 绿，>=75 蓝，>=60 黄，<60 红）
- 技能标签
- 操作按钮：**查询详情**、**联系学生**

### 综合评分算法（后端）
- 基础分 + growth_records * 10 + GPA_weighted - crisis_penalty
- 基础分 60
- 成长记录每条 +5 分（上限 30）
- GPA 加权：4.0 满分对应 +10 分（线性映射）
- 有严重危机 -20，中度 -10，轻度 -5

### 查询详情
- 点击"查询详情"才加载完整信息：成长记录时间线 + 预警列表 + 请假记录
- 未点击时卡片仅显示概要

### 联系学生
- 点击弹出消息发送对话框
- 消息通过后端 API 发送

### 空状态
- 名下无学生时显示"暂无学生记录"（带插画图标）

## 5. 师生消息系统

### 后端模型 — Message
```sql
Table: messages
- id: int PK autoincrement
- sender_id: int FK (users.id)
- receiver_id: int FK (users.id)
- content: Text
- read: bool default false
- created_at: DateTime
```

### 后端 API
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/messages/send` | POST | 发送消息（sender_id, receiver_id, content） |
| `/api/messages/conversations` | GET | 当前用户的会话列表（对方信息 + 最后一条消息 + 未读数） |
| `/api/messages/{user_id}` | GET | 与指定用户的消息历史（按时间正序） |
| `/api/messages/read/{user_id}` | PUT | 标记与某人的所有消息为已读 |

### 前端 — 学生端
- 布局顶栏（学生端）新增消息图标 + 未读气泡数量
- 点击消息图标弹出消息面板（侧边抽屉）
- 消息面板：会话列表 + 消息详情 + 发送框
- 只能与辅导员（tutor）通信

### 前端 — 教师端
- 侧边栏新增"消息"菜单项，右侧显示未读计数
- "消息"页面：会话列表（按学生分组）+ 消息详情 + 发送框
- 学生卡片"联系学生"打开消息对话框

## 6. 后端新增端点

### Teacher 模块
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/teacher/students/score` | GET | 所有学生的综合评分 |

### Leave 模块
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/leave/all` | GET | 教师名下所有审批记录（待批/已通过/已拒绝） |
| `/api/leave/{id}/analyze` | GET | AI 审批建议 |

### New: Messages 模块
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/messages/send` | POST | 发送消息 |
| `/api/messages/conversations` | GET | 会话列表 |
| `/api/messages/{user_id}` | GET | 消息历史 |
| `/api/messages/read/{user_id}` | PUT | 标记已读 |

## 7. 文件改动清单

### 后端
- **新建** `app/api/messages.py` — 消息系统路由
- **新建** `app/models/message.py` — Message 模型
- **新建** `app/schemas/message.py` — Message schema
- **修改** `app/main.py` — 注册 messages 路由
- **修改** `app/api/leave.py` — 新增 `GET /all` 和 `GET /{id}/analyze` 端点
- **修改** `app/api/teacher.py` — 新增评分端点

### 前端
- **修改** `src/components/layout/TeacherLayout.vue` — 校徽校训 + 下拉退出菜单
- **修改** `src/views/teacher/AgentPage.vue` — ChatShell 集成 + 教师快捷入口
- **修改** `src/views/teacher/ApprovalPage.vue` — AI 分析 + 已通过/已拒绝 Tab
- **修改** `src/views/teacher/StudentsPage.vue` — 评分 + 联系学生 + 空状态
- **新建** `src/api/messages.ts`
- **新建** `src/views/teacher/MessagesPage.vue` — 教师消息页面
- **修改** `src/router/index.ts` — 添加消息路由
- **新建** `src/components/chat/StudentContactPanel.vue` — 学生端联系教师组件
- **修改** `src/components/layout/StudentLayout.vue` — 消息图标 + 未读气泡
- **修改** `src/api/leave.ts` — 新增接口

## 8. 综合评分算法

```
综合评分 = min(100, max(0, base_score + growth_bonus + gpa_bonus - crisis_penalty))

base_score = 60
growth_bonus = min(growth_count * 5, 30)
gpa_bonus = min(gpa / 4.0 * 10, 10)  # GPA 从 grades 表计算
crisis_penalty = 
  - 有 severe 级别未解决预警: 20
  - 有 moderate 级别未解决预警: 10  
  - 有 mild 级别未解决预警: 5
  - 多个取最高
```

## 9. 颜色参考

- 评分 >= 90: `#67c23a` (绿色)
- 评分 >= 75: `#409eff` (蓝色)
- 评分 >= 60: `#e6a23c` (黄色)
- 评分 < 60: `#f56c6c` (红色)
- 消息未读气泡: `#f56c6c`
- 玻璃拟态背景: `rgba(255, 255, 255, 0.85)` + `backdrop-filter: blur(20px)`
