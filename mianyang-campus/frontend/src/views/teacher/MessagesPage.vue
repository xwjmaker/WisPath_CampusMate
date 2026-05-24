<template>
  <div class="msg-page">
    <div class="msg-sidebar">
      <h3>消息</h3>
      <el-input v-model="search" placeholder="搜索学生姓名或学号" size="small" clearable
        style="margin:8px 12px;width:auto" @input="searchStudents" />
      <div class="sidebar-scroll">
        <!-- Search results -->
        <template v-if="searched">
          <div v-if="searchResults.length === 0" class="no-msg">未找到学生</div>
          <div v-for="s in searchResults" :key="s.id"
            :class="['conv-item', { active: activeUserId === s.id }]"
            @click="selectConversation(s.id, s.name)">
            <el-avatar :size="36" :src="s.avatar || undefined">{{ s.name[0] }}</el-avatar>
            <div class="conv-info">
              <strong>{{ s.name }}</strong>
              <small>{{ s.username }}</small>
            </div>
          </div>
        </template>
        <!-- Conversations -->
        <template v-else>
          <div v-if="conversations.length === 0" class="no-msg">暂无消息</div>
          <div v-for="c in conversations" :key="c.user_id"
            :class="['conv-item', { active: activeUserId === c.user_id }]"
            @click="selectConversation(c.user_id, c.user_name)">
            <el-badge :value="c.unread_count" :hidden="!c.unread_count" class="conv-badge">
              <el-avatar :size="36" :src="c.user_avatar || undefined">{{ c.user_name[0] }}</el-avatar>
            </el-badge>
            <div class="conv-info">
              <strong>{{ c.user_name }}</strong>
              <small>{{ c.last_message.slice(0, 25) }}{{ c.last_message.length > 25 ? '...' : '' }}</small>
            </div>
          </div>
        </template>
      </div>
    </div>
    <div class="msg-chat">
      <template v-if="activeUserId">
        <div class="chat-header">{{ activeUserName }}</div>
        <div class="msg-list" ref="msgListRef">
          <div v-for="m in messages" :key="m.id"
            :class="['msg-bubble', m.sender_id === userId ? 'mine' : 'theirs']">
            <div class="bubble-text">{{ m.content }}</div>
            <div class="bubble-time">{{ formatTime(m.created_at) }}</div>
          </div>
        </div>
        <div class="msg-input-bar">
          <el-input v-model="newMsg" type="textarea" :autosize="{ minRows: 1, maxRows: 5 }"
            placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
            @keydown.enter.exact.prevent="sendMsg" />
          <el-button type="primary" @click="sendMsg" :disabled="!newMsg.trim()">发送</el-button>
        </div>
      </template>
      <div v-else class="no-selection">选择一个学生开始聊天</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getConversations, getMessages, sendMessage, markRead } from '@/api/messages'
import { getStudents, type StudentSummary } from '@/api/teacher'
import { getToken } from '@/utils/token'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const userId = auth.user?.id ?? 0
const conversations = ref<any[]>([])
const activeUserId = ref<number | null>(null)
const activeUserName = ref('')
const messages = ref<any[]>([])
const newMsg = ref('')
const msgListRef = ref<HTMLDivElement>()
const search = ref('')
const searchResults = ref<StudentSummary[]>([])
const searched = ref(false)
let ws: WebSocket | null = null

function connectWs() {
  const token = getToken()
  if (!token) return
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  ws = new WebSocket(`${proto}//${window.location.host}/api/messages/ws?token=${token}`)
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data)
      if (data.type === 'new_message') {
        loadConversations()
        if (data.sender_id === activeUserId.value) {
          messages.value.push({
            id: data.id || Date.now(),
            sender_id: data.sender_id,
            content: data.content,
            created_at: data.created_at,
            read: true,
          })
          nextTick(() => msgListRef.value?.scrollTo({ top: msgListRef.value.scrollHeight, behavior: 'smooth' }))
        }
      }
    } catch {}
  }
  ws.onclose = () => { ws = null }
}

function disconnectWs() {
  if (ws) { ws.close(); ws = null }
}

async function loadConversations() {
  try { conversations.value = await getConversations() } catch {}
}

async function searchStudents() {
  if (!search.value.trim()) {
    searchResults.value = []
    searched.value = false
    return
  }
  try {
    searchResults.value = await getStudents(search.value.trim())
    searched.value = true
  } catch { searchResults.value = [] }
}

async function selectConversation(uid: number, uname: string) {
  activeUserId.value = uid
  activeUserName.value = uname
  search.value = ''
  searchResults.value = []
  searched.value = false
  try {
    messages.value = await getMessages(uid)
    await markRead(uid)
    loadConversations()
    nextTick(() => msgListRef.value?.scrollTo({ top: msgListRef.value.scrollHeight, behavior: 'smooth' }))
  } catch {}
}

async function sendMsg() {
  if (!newMsg.value.trim() || !activeUserId.value) return
  try {
    await sendMessage(activeUserId.value, newMsg.value.trim())
    messages.value.push({
      id: Date.now(), sender_id: userId, receiver_id: activeUserId.value,
      content: newMsg.value.trim(), read: true, created_at: new Date().toISOString()
    })
    newMsg.value = ''
    nextTick(() => msgListRef.value?.scrollTo({ top: msgListRef.value.scrollHeight, behavior: 'smooth' }))
  } catch { ElMessage.error('发送失败') }
}

function formatTime(t: string) {
  try { return new Date(t).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) } catch { return t }
}

onMounted(async () => {
  connectWs()
  await loadConversations()
  if (route.query.studentId) {
    const sid = Number(route.query.studentId)
    const sname = (route.query.studentName as string) || ''
    selectConversation(sid, sname)
    router.replace({ query: {} })
  }
})

onUnmounted(() => disconnectWs())
</script>

<style scoped>
.msg-page { display: flex; height: calc(100vh - 48px); background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,.04); }
.msg-sidebar { width: 280px; border-right: 1px solid #f0f0f0; display: flex; flex-direction: column; }
.msg-sidebar h3 { padding: 16px; margin: 0; font-size: 16px; border-bottom: 1px solid #f0f0f0; }
.sidebar-scroll { flex: 1; overflow-y: auto; min-height: 0; }
.conv-item { display: flex; align-items: center; gap: 10px; padding: 12px 16px; cursor: pointer; transition: background .15s; }
.conv-item:hover, .conv-item.active { background: #f0f7ff; }
.conv-info { flex: 1; min-width: 0; }
.conv-info strong { font-size: 14px; display: block; }
.conv-info small { font-size: 12px; color: #999; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conv-badge { --el-badge-bg-color: #f56c6c; }
.msg-chat { flex: 1; display: flex; flex-direction: column; }
.msg-list { flex: 1; overflow-y: auto; padding: 16px; }
.msg-bubble { margin-bottom: 12px; max-width: min(70%, 360px); width: fit-content; }
.msg-bubble.mine { margin-left: auto; }
.msg-bubble.theirs { margin-right: auto; }
.bubble-text { padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.5; }
.mine .bubble-text { background: #409eff; color: #fff; border-bottom-right-radius: 4px; }
.theirs .bubble-text { background: #f0f4f9; color: #333; border-bottom-left-radius: 4px; }
.bubble-time { font-size: 11px; color: #bbb; margin-top: 2px; padding: 0 4px; }
.mine .bubble-time { text-align: right; }
.msg-input-bar { display: flex; gap: 8px; padding: 8px 12px; border-top: 1px solid #f0f0f0; align-items: flex-end; }
.msg-input-bar .el-input { flex: 1; }
.msg-input-bar .el-textarea__inner { min-height: auto !important; padding: 6px 10px; line-height: 1.4; resize: none; }
.chat-header { padding: 12px 16px; font-size: 15px; font-weight: 600; border-bottom: 1px solid #f0f0f0; background: #fafafa; }
.no-msg, .no-selection { padding: 40px; text-align: center; color: #999; }
</style>
