<template>
  <div class="contact-panel">
    <div v-if="!tutor" class="no-tutor">暂无辅导员信息</div>
    <template v-else>
      <div class="tutor-info">
        <el-avatar :size="48">{{ tutor.name[0] }}</el-avatar>
        <div>
          <strong>{{ tutor.name }}</strong>
          <small>辅导员</small>
        </div>
      </div>
      <div class="msg-list" ref="msgListRef">
        <div v-for="m in messages" :key="m.id"
          :class="['msg-bubble', m.sender_id === userId ? 'mine' : 'theirs']">
          <div class="bubble-text">{{ m.content }}</div>
          <div class="bubble-time">{{ formatTime(m.created_at) }}</div>
        </div>
      </div>
      <div class="msg-input-bar">
        <el-input v-model="newMsg" placeholder="输入消息..." @keyup.enter="sendMsg" size="small" />
        <el-button type="primary" size="small" @click="sendMsg" :disabled="!newMsg.trim()">发送</el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getConversations, getMessages, sendMessage, markRead } from '@/api/messages'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const userId = auth.user?.id ?? 0
const tutor = ref<{ id: number; name: string; avatar?: string } | null>(null)
const messages = ref<any[]>([])
const newMsg = ref('')
const msgListRef = ref<HTMLDivElement>()

async function loadTutor() {
  if (auth.user?.tutor_id) {
    try {
      const convs: any[] = await getConversations()
      const t = convs.find((c: any) => c.user_id === auth.user!.tutor_id)
      if (t) {
        tutor.value = { id: t.user_id, name: t.user_name, avatar: t.user_avatar || undefined }
      } else {
        tutor.value = { id: auth.user!.tutor_id, name: '辅导员' }
      }
    } catch {
      tutor.value = { id: auth.user!.tutor_id!, name: '辅导员' }
    }
  }
}

async function loadMessages() {
  if (!tutor.value) return
  try {
    messages.value = await getMessages(tutor.value.id)
    await markRead(tutor.value.id)
    nextTick(() => msgListRef.value?.scrollTo({ top: msgListRef.value.scrollHeight, behavior: 'smooth' }))
  } catch {}
}

async function sendMsg() {
  if (!newMsg.value.trim() || !tutor.value) return
  try {
    await sendMessage(tutor.value.id, newMsg.value.trim())
    messages.value.push({
      id: Date.now(), sender_id: userId, receiver_id: tutor.value.id,
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
  await loadTutor()
  if (tutor.value) loadMessages()
})
</script>

<style scoped>
.contact-panel { display: flex; flex-direction: column; height: 100%; }
.tutor-info { display: flex; align-items: center; gap: 12px; padding: 16px; border-bottom: 1px solid #f0f0f0; }
.tutor-info div { display: flex; flex-direction: column; }
.tutor-info small { color: #999; font-size: 12px; }
.msg-list { flex: 1; overflow-y: auto; padding: 12px; }
.msg-bubble { margin-bottom: 10px; max-width: 80%; }
.msg-bubble.mine { margin-left: auto; }
.msg-bubble.theirs { margin-right: auto; }
.bubble-text { padding: 8px 12px; border-radius: 12px; font-size: 13px; line-height: 1.5; }
.mine .bubble-text { background: #409eff; color: #fff; border-bottom-right-radius: 3px; }
.theirs .bubble-text { background: #f0f4f9; color: #333; border-bottom-left-radius: 3px; }
.bubble-time { font-size: 10px; color: #bbb; margin-top: 2px; padding: 0 4px; }
.mine .bubble-time { text-align: right; }
.msg-input-bar { display: flex; gap: 6px; padding: 10px 12px; border-top: 1px solid #f0f0f0; }
.msg-input-bar .el-input { flex: 1; }
.no-tutor { padding: 40px; text-align: center; color: #999; }
</style>
