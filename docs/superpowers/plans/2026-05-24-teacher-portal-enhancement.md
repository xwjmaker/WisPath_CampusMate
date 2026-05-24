# 教师端门户增强实现计划

**Goal:** 教师端全面 UI/UX 升级（布局、审批AI分析、学生评分、师生消息系统）

**Architecture:** 后端新增 messages 路由 + 综合评分 API + AI 审批分析 / 前端改造 TeacherLayout/ChatShell 集成 + ApprovalPage/StudentsPage 增强 + 师生消息组件

**Tech Stack:** Python FastAPI + SQLAlchemy + Vue 3 + Element Plus

---

### Task 1: 后端 — Message 模型 + Schema + API

**Files:**
- Create: `backend/app/models/message.py`
- Create: `backend/app/schemas/message.py`
- Create: `backend/app/api/messages.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Create Message model**

`backend/app/models/message.py`:
```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from app.core.database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 2: Create Message schemas**

`backend/app/schemas/message.py`:
```python
from datetime import datetime
from pydantic import BaseModel

class MessageSend(BaseModel):
    receiver_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    read: bool
    created_at: datetime
    class Config: from_attributes = True

class ConversationOut(BaseModel):
    user_id: int
    user_name: str
    user_avatar: str | None = None
    last_message: str
    last_message_time: datetime | None = None
    unread_count: int = 0
```

- [ ] **Step 3: Create Messages API**

`backend/app/api/messages.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserRole
from app.models.message import Message
from app.schemas.message import MessageSend, MessageOut, ConversationOut

router = APIRouter(prefix="/api/messages", tags=["messages"])

@router.post("/send")
def send_message(data: MessageSend, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    receiver = db.query(User).filter(User.id == data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="接收用户不存在")
    msg = Message(sender_id=user.id, receiver_id=data.receiver_id, content=data.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "created_at": msg.created_at.isoformat()}

@router.get("/conversations")
def get_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sent_ids = db.query(Message.receiver_id).filter(Message.sender_id == user.id).distinct().subquery()
    received_ids = db.query(Message.sender_id).filter(Message.receiver_id == user.id).distinct().subquery()
    all_ids = db.query(sent_ids.c.receiver_id).union(db.query(received_ids.c.sender_id)).subquery()
    other_users = db.query(User).filter(User.id.in_(db.query(all_ids))).all()
    result = []
    for other in other_users:
        last_msg = db.query(Message).filter(
            or_(
                (Message.sender_id == user.id) & (Message.receiver_id == other.id),
                (Message.sender_id == other.id) & (Message.receiver_id == user.id)
            )
        ).order_by(Message.created_at.desc()).first()
        unread = db.query(Message).filter(
            Message.sender_id == other.id, Message.receiver_id == user.id, Message.read == False
        ).count()
        result.append(ConversationOut(
            user_id=other.id,
            user_name=other.name,
            user_avatar=other.avatar,
            last_message=last_msg.content[:80] if last_msg else "",
            last_message_time=last_msg.created_at if last_msg else None,
            unread_count=unread,
        ))
    return result

@router.get("/{user_id}")
def get_messages(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(
        or_(
            (Message.sender_id == user.id) & (Message.receiver_id == user_id),
            (Message.sender_id == user_id) & (Message.receiver_id == user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    return [MessageOut(id=m.id, sender_id=m.sender_id, receiver_id=m.receiver_id,
                       content=m.content, read=m.read, created_at=m.created_at) for m in msgs]

@router.put("/read/{user_id}")
def mark_read(user_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Message).filter(
        Message.sender_id == user_id, Message.receiver_id == user.id, Message.read == False
    ).update({"read": True})
    db.commit()
    return {"message": "marked read"}
```

- [ ] **Step 4: Register in models/__init__.py**

Add line: `from app.models.message import Message`

- [ ] **Step 5: Register in main.py**

Add import: `from app.api.messages import router as messages_router`
Add: `app.include_router(messages_router)`

- [ ] **Step 6: Commit**
```bash
git add backend/app/models/message.py backend/app/schemas/message.py backend/app/api/messages.py backend/app/models/__init__.py backend/app/main.py
git commit -m "feat: 新增师生消息系统后端API"
```

---

### Task 2: 后端 — 教师/审批功能增强

**Files:**
- Modify: `backend/app/api/teacher.py`
- Modify: `backend/app/api/leave.py`

- [ ] **Step 1: Add score field to StudentOut + GET /api/teacher/students/score endpoint**

`backend/app/api/teacher.py`:
- Add import: `from app.models.academic import Grade`
- Add `score` field to `StudentOut` (float, default=0)
- In `list_students`, compute score for each student:
```python
def calc_student_score(db, student_id):
    base = 60.0
    growth_count = db.query(GrowthRecord).filter(GrowthRecord.student_id == student_id).count()
    growth_bonus = min(growth_count * 5, 30)
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    avg_gpa = sum(g.gpa * g.credit for g in grades) / sum(g.credit for g in grades) if grades and sum(g.credit for g in grades) > 0 else 0
    gpa_bonus = min(avg_gpa / 4.0 * 10, 10)
    latest_crisis = db.query(AIDialogSummary).filter(
        AIDialogSummary.student_id == student_id, AIDialogSummary.resolved == False
    ).order_by(AIDialogSummary.created_at.desc()).first()
    crisis_penalty = {"severe": 20, "moderate": 10, "mild": 5}.get(latest_crisis.level.value if latest_crisis else "", 0)
    return round(max(0, min(100, base + growth_bonus + gpa_bonus - crisis_penalty)), 1)
```

- [ ] **Step 2: Add GET /api/leave/all and GET /api/leave/{id}/analyze**

`backend/app/api/leave.py`:
- Add import: `from app.services.llm_service import client`
- Add import: `from app.core.config import settings`

Add endpoint `GET /api/leave/all`:
```python
@router.get("/all", response_model=list[LeaveRequestOut])
def list_all_requests(status: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != UserRole.TEACHER and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="仅教师可查看")
    query = db.query(LeaveRequest)
    if user.role != UserRole.ADMIN:
        student_ids = [s.id for s in db.query(User).filter(User.tutor_id == user.id).all()]
        query = query.filter(LeaveRequest.student_id.in_(student_ids)) if student_ids else query.filter("0=1")
    if status:
        query = query.filter(LeaveRequest.status == status)
    requests = query.order_by(LeaveRequest.created_at.desc()).all()
    result = []
    for r in requests:
        student = db.query(User).filter(User.id == r.student_id).first()
        result.append(LeaveRequestOut(
            id=r.id, student_id=r.student_id, student_name=student.name if student else "",
            start_date=r.start_date, end_date=r.end_date, reason=r.reason,
            leave_type=r.leave_type.value if hasattr(r.leave_type, 'value') else r.leave_type,
            status=r.status.value if hasattr(r.status, 'value') else r.status,
            reject_reason=r.reject_reason,
            created_at=r.created_at.isoformat() if r.created_at else "",
        ))
    return result
```

Add endpoint `GET /api/leave/{id}/analyze`:
```python
@router.get("/{id}/analyze")
def analyze_leave(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="请假申请不存在")
    student = db.query(User).filter(User.id == leave.student_id).first()
    prompt = f"""请分析以下请假申请，给出审批建议（approve/reject）和理由，用JSON格式返回：
学生：{student.name if student else "未知"}
类型：{leave.leave_type.value if hasattr(leave.leave_type, 'value') else leave.leave_type}
时间：{leave.start_date} 至 {leave.end_date}
原因：{leave.reason}

回复格式：{{"suggestion": "approve"或"reject", "reason": "理由"}}"""
    try:
        resp = client.chat.completions.create(
            model=settings.LLM_MODEL, messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=300,
        )
        content = resp.choices[0].message.content
        import json
        try:
            return json.loads(content)
        except:
            return {"suggestion": "approve", "reason": content[:200]}
    except Exception as e:
        return {"suggestion": "approve", "reason": "AI分析暂时不可用，请自行判断"}
```

- [ ] **Step 3: Commit**
```bash
git add backend/app/api/teacher.py backend/app/api/leave.py
git commit -m "feat: 新增综合评分 + 请假审批AI分析"
```

---

### Task 3: 前端 — API 封装

**Files:**
- Create: `frontend/src/api/messages.ts`
- Modify: `frontend/src/api/leave.ts`
- Modify: `frontend/src/api/teacher.ts`

- [ ] **Step 1: Create messages API**

`frontend/src/api/messages.ts`:
```typescript
import request from '@/utils/request'

export interface MessageOut {
  id: number; sender_id: number; receiver_id: number; content: string; read: boolean; created_at: string
}

export interface ConversationOut {
  user_id: number; user_name: string; user_avatar: string | null
  last_message: string; last_message_time: string | null; unread_count: number
}

export function getConversations() {
  return request.get<ConversationOut[]>('/messages/conversations')
}

export function getMessages(userId: number) {
  return request.get<MessageOut[]>(`/messages/${userId}`)
}

export function sendMessage(receiverId: number, content: string) {
  return request.post<{ id: number; created_at: string }>('/messages/send', { receiver_id: receiverId, content })
}

export function markRead(userId: number) {
  return request.put(`/messages/read/${userId}`)
}
```

- [ ] **Step 2: Update leave.ts**

Add:
```typescript
export function getAllLeaves(status?: string) {
  const params = status ? { status } : {}
  return request.get<LeaveRequestOut[]>('/leave/all', { params })
}

export function analyzeLeave(id: number) {
  return request.get<{ suggestion: string; reason: string }>(`/leave/${id}/analyze`)
}
```

- [ ] **Step 3: Update teacher.ts**

Add `score` to `StudentSummary` interface, add:
```typescript
export function getStudentScores() {
  return request.get<Record<number, number>>('/teacher/students/score')
}
```

- [ ] **Step 4: Commit**
```bash
git add frontend/src/api/messages.ts frontend/src/api/leave.ts frontend/src/api/teacher.ts
git commit -m "feat: 前端API封装（消息/评分/审批分析）"
```

---

### Task 4: 前端 — TeacherLayout + Router + MessagesPage

**Files:**
- Modify: `frontend/src/components/layout/TeacherLayout.vue`
- Modify: `frontend/src/router/index.ts`
- Create: `frontend/src/views/teacher/MessagesPage.vue`

- [ ] **Step 1: Rewrite TeacherLayout.vue**

Full rewrite with logo + motto in sidebar, dropdown logout, modern glass-effect styling:
```vue
<template>
  <div class="teacher-shell">
    <aside class="t-sidebar">
      <div class="t-logo">
        <img src="/images/校徽.png" class="t-badge" />
        <span class="t-motto">博学、笃行<br/>严谨、创新</span>
      </div>
      <el-menu :router="true" :default-active="route.path" class="t-menu">
        <el-menu-item index="/teacher">
          <el-icon><WarningFilled /></el-icon><span>预警雷达</span>
        </el-menu-item>
        <el-menu-item index="/teacher/agent">
          <el-icon><ChatDotSquare /></el-icon><span>智能助手</span>
        </el-menu-item>
        <el-menu-item index="/teacher/approval">
          <el-icon><CircleCheck /></el-icon><span>审批管理</span>
        </el-menu-item>
        <el-menu-item index="/teacher/students">
          <el-icon><User /></el-icon><span>学生成长</span>
        </el-menu-item>
        <el-menu-item index="/teacher/messages">
          <el-icon><Message /></el-icon>
          <span>消息</span>
          <el-badge v-if="unreadCount" :value="unreadCount" class="msg-badge" />
        </el-menu-item>
      </el-menu>
      <div class="t-user">
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="t-user-btn">
            <el-avatar :size="32">{{ auth.userName?.[0] }}</el-avatar>
            <span class="t-user-name">{{ auth.userName }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-item command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </template>
        </el-dropdown>
      </div>
    </aside>
    <main class="t-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getConversations } from '@/api/messages'
import { WarningFilled, ChatDotSquare, CircleCheck, User, Message, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const unreadCount = ref(0)
let pollTimer: any = null

function handleCommand(cmd: string) {
  if (cmd === 'logout') { auth.logout(); router.push('/') }
}

async function pollUnread() {
  if (auth.role !== 'teacher' && auth.role !== 'admin') return
  try {
    const convs = await getConversations()
    unreadCount.value = convs.reduce((sum, c) => sum + c.unread_count, 0)
  } catch {}
}

onMounted(() => { pollUnread(); pollTimer = setInterval(pollUnread, 5000) })
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.teacher-shell { display: flex; height: 100vh; background: #f5f7fa; }
.t-sidebar {
  width: 220px; flex-shrink: 0; display: flex; flex-direction: column;
  background: rgba(255,255,255,.85); backdrop-filter: blur(20px);
  border-right: 1px solid rgba(0,0,0,.06); box-shadow: 2px 0 12px rgba(0,0,0,.03);
}
.t-logo {
  display: flex; align-items: center; gap: 10px; padding: 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}
.t-badge { height: 36px; width: auto; }
.t-motto {
  font-size: 14px; font-weight: 700; line-height: 1.4;
  background: linear-gradient(135deg, #c41d7f, #e8a020);
  background-clip: text; -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; letter-spacing: 3px;
}
.t-menu { flex: 1; border-right: none; --el-menu-bg-color: transparent; }
.t-menu .el-menu-item { margin: 2px 8px; border-radius: 8px; }
.t-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: #fff; font-weight: 600;
}
.t-menu .el-menu-item.is-active .el-icon { color: #fff; }
.msg-badge { margin-left: auto; }
.t-user { padding: 12px 16px; border-top: 1px solid #f0f0f0; }
.t-user-btn {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 4px 8px; border-radius: 8px; transition: background .2s;
}
.t-user-btn:hover { background: #f0f4f9; }
.t-user-name { font-size: 14px; color: #333; flex: 1; }
.t-main { flex: 1; overflow-y: auto; padding: 24px; }
</style>
```

- [ ] **Step 2: Update router**

In `parent.children` of `/teacher`, add:
```typescript
{ path: 'messages', component: () => import('@/views/teacher/MessagesPage.vue') },
```

- [ ] **Step 3: Create MessagesPage.vue**

```vue
<template>
  <div class="msg-page">
    <div class="msg-sidebar">
      <h3>消息</h3>
      <div v-if="conversations.length === 0" class="no-msg">暂无消息</div>
      <div v-for="c in conversations" :key="c.user_id"
        :class="['conv-item', { active: activeUserId === c.user_id }]"
        @click="selectConversation(c.user_id)">
        <el-badge :value="c.unread_count" :hidden="!c.unread_count" class="conv-badge">
          <el-avatar :size="36">{{ c.user_name[0] }}</el-avatar>
        </el-badge>
        <div class="conv-info">
          <strong>{{ c.user_name }}</strong>
          <small>{{ c.last_message.slice(0, 30) }}{{ c.last_message.length > 30 ? '...' : '' }}</small>
        </div>
      </div>
    </div>
    <div class="msg-chat">
      <template v-if="activeUserId">
        <div class="msg-list" ref="msgListRef">
          <div v-for="m in messages" :key="m.id"
            :class="['msg-bubble', m.sender_id === auth.user?.id ? 'mine' : 'theirs']">
            <div class="bubble-text">{{ m.content }}</div>
            <div class="bubble-time">{{ formatTime(m.created_at) }}</div>
          </div>
        </div>
        <div class="msg-input-bar">
          <el-input v-model="newMsg" placeholder="输入消息..." @keyup.enter="sendMsg" />
          <el-button type="primary" @click="sendMsg" :disabled="!newMsg.trim()">发送</el-button>
        </div>
      </template>
      <div v-else class="no-selection">选择一个学生开始聊天</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getConversations, getMessages, sendMessage, markRead, type ConversationOut, type MessageOut } from '@/api/messages'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const conversations = ref<ConversationOut[]>([])
const activeUserId = ref<number | null>(null)
const messages = ref<MessageOut[]>([])
const newMsg = ref('')
const msgListRef = ref<HTMLDivElement>()

async function loadConversations() {
  try { conversations.value = await getConversations() } catch {}
}

async function selectConversation(userId: number) {
  activeUserId.value = userId
  try {
    messages.value = await getMessages(userId)
    await markRead(userId)
    loadConversations()
    nextTick(() => msgListRef.value?.scrollTo({ top: msgListRef.value.scrollHeight, behavior: 'smooth' }))
  } catch {}
}

async function sendMsg() {
  if (!newMsg.value.trim() || !activeUserId.value) return
  try {
    await sendMessage(activeUserId.value, newMsg.value.trim())
    messages.value.push({
      id: Date.now(), sender_id: auth.user!.id, receiver_id: activeUserId.value,
      content: newMsg.value.trim(), read: true, created_at: new Date().toISOString()
    })
    newMsg.value = ''
    nextTick(() => msgListRef.value?.scrollTo({ top: msgListRef.value.scrollHeight, behavior: 'smooth' }))
  } catch { ElMessage.error('发送失败') }
}

function formatTime(t: string) {
  try { return new Date(t).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) } catch { return t }
}

onMounted(loadConversations)
</script>

<style scoped>
.msg-page { display: flex; height: calc(100vh - 48px); background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.04); }
.msg-sidebar { width: 280px; border-right: 1px solid #f0f0f0; display: flex; flex-direction: column; }
.msg-sidebar h3 { padding: 16px; margin: 0; font-size: 16px; border-bottom: 1px solid #f0f0f0; }
.conv-item { display: flex; align-items: center; gap: 10px; padding: 12px 16px; cursor: pointer; transition: background .15s; }
.conv-item:hover, .conv-item.active { background: #f0f7ff; }
.conv-info { flex: 1; min-width: 0; }
.conv-info strong { font-size: 14px; display: block; }
.conv-info small { font-size: 12px; color: #999; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conv-badge { --el-badge-bg-color: #f56c6c; }
.msg-chat { flex: 1; display: flex; flex-direction: column; }
.msg-list { flex: 1; overflow-y: auto; padding: 16px; }
.msg-bubble { margin-bottom: 12px; max-width: 70%; }
.msg-bubble.mine { margin-left: auto; }
.msg-bubble.theirs { margin-right: auto; }
.bubble-text { padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.5; }
.mine .bubble-text { background: #409eff; color: #fff; border-bottom-right-radius: 4px; }
.theirs .bubble-text { background: #f0f4f9; color: #333; border-bottom-left-radius: 4px; }
.bubble-time { font-size: 11px; color: #bbb; margin-top: 2px; padding: 0 4px; }
.mine .bubble-time { text-align: right; }
.msg-input-bar { display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid #f0f0f0; }
.msg-input-bar .el-input { flex: 1; }
.no-msg, .no-selection { padding: 40px; text-align: center; color: #999; }
</style>
```

- [ ] **Step 4: Commit**
```bash
git add frontend/src/components/layout/TeacherLayout.vue frontend/src/router/index.ts frontend/src/views/teacher/MessagesPage.vue
git commit -m "feat: 教师布局重构+消息页面+路由"
```

---

### Task 5: 前端 — AgentPage ChatShell 集成

**Files:**
- Modify: `frontend/src/views/teacher/AgentPage.vue`

Rewriting to use ChatShell:
```vue
<template>
  <div class="agent-page">
    <ChatShell />
  </div>
</template>

<script setup lang="ts">
import ChatShell from '@/components/agent/ChatShell.vue'
</script>

<style scoped>
.agent-page { height: calc(100vh - 48px); }
</style>
```

Commit.

---

### Task 6: 前端 — StudentsPage 增强

**Files:**
- Modify: `frontend/src/views/teacher/StudentsPage.vue`

Key changes:
- Add `score` to card display (colored)
- Add "查询详情" and "联系学生" buttons below card
- Empty state when no students
- Contact dialog integration

- [ ] **Step: Implementation**

Full rewrite with:
1. Show score on each card (colored by value)
2. Show growth_count as "成果数量"
3. Action buttons: 查询详情 (opens drawer with full data+alerts), 联系学生 (message dialog)
4. Empty state when no students
5. Click-to-query: drawer only opens when "查询详情" is clicked

---

### Task 7: 前端 — ApprovalPage 增强

**Files:**
- Modify: `frontend/src/views/teacher/ApprovalPage.vue`

- [ ] **Step: Implementation**

Rewrite with 3 tabs (待审批/已通过/已拒绝):
- Auto-load AI analysis for each pending item when tab loads
- Display AI suggestion (green/red tag)
- Show history for approved/rejected tabs with approver info

---

### Task 8: 前端 — 学生端消息组件

**Files:**
- Create: `frontend/src/components/chat/StudentContactPanel.vue`
- Modify: `frontend/src/components/layout/StudentLayout.vue`

- [ ] **Step 1: Create StudentContactPanel.vue**

A message drawer component for students to contact their tutor.

- [ ] **Step 2: Update StudentLayout.vue**

Add message icon with unread badge in header, opens a drawer/modal with StudentContactPanel.

---

### Task 9: 数据迁移 — 创建 messages 表

Run the seed script or create tables:
```bash
cd mianyang-campus/backend && python -c "from app.core.database import engine, Base; from app.models.message import Message; Base.metadata.create_all(bind=engine)"
```
