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
            :class="['msg-bubble', m.sender_id === userId ? 'mine' : 'theirs']">
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
import { getConversations, getMessages, sendMessage, markRead } from '@/api/messages'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const userId = auth.user?.id ?? 0
const conversations = ref<any[]>([])
const activeUserId = ref<number | null>(null)
const messages = ref<any[]>([])
const newMsg = ref('')
const msgListRef = ref<HTMLDivElement>()

async function loadConversations() {
  try { conversations.value = await getConversations() } catch {}
}

async function selectConversation(uid: number) {
  activeUserId.value = uid
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
