<template>
  <div class="chat-shell">
    <div class="messages" ref="msgRef">
      <div v-if="store.messages.length === 0" class="welcome">
        <div class="welcome-avatar">
          <img src="/images/06.png" alt="绵小城" class="welcome-img" />
        </div>
        <h1 class="welcome-title">你好，我是绵小城</h1>
        <p class="welcome-desc">你的校园智能管家。不需要切换各个APP，所有事情直接跟我聊</p>
        <div class="welcome-actions">
          <el-card v-for="a in actions" :key="a.label" shadow="hover" class="action-card" @click="quickSend(a.example)">
            <div class="action-icon" :style="{ background: a.color + '15', color: a.color }">{{ a.icon }}</div>
            <div class="action-text">
              <strong>{{ a.label }}</strong>
              <small>{{ a.desc }}</small>
            </div>
          </el-card>
        </div>
        <div class="welcome-hints">
          <el-tag v-for="h in hints" :key="h" class="hint-tag" @click="quickSend(h)">{{ h }}</el-tag>
        </div>
      </div>
      <div v-for="(msg, i) in store.messages" :key="msg.id" :class="['msg-row', msg.role]">
        <div v-if="msg.role === 'assistant'" class="msg-avatar">
          <img src="/images/06.png" alt="绵小城" class="mini-avatar" />
        </div>
        <div :class="['bubble', msg.role]">
          <div class="msg-text" v-html="renderMarkdown(msg.content)"></div>
          <div v-if="msg.suggestions?.length" class="suggestions">
            <el-tag v-for="s in msg.suggestions" :key="s.text" class="suggestion-tag" @click="handleSuggestion(s)">{{ s.text }}</el-tag>
          </div>
        </div>
      </div>
      <div v-if="loading" class="msg-row assistant">
        <div class="msg-avatar"><img src="/images/06.png" alt="绵小城" class="mini-avatar" /></div>
        <div class="bubble assistant thinking">
          <span class="dot-pulse"></span>
        </div>
      </div>
    </div>
    <div class="input-bar">
      <div class="input-wrap">
        <el-input
          v-model="input"
          :disabled="loading"
          placeholder="输入你的需求，比如「下周二比赛想请假」..."
          class="chat-input"
          @keyup.enter="send"
        />
        <el-button type="primary" :loading="loading" class="send-btn" @click="send">
          <el-icon><Promotion /></el-icon>
        </el-button>
      </div>
      <p class="input-foot">绵小城·智慧校园AI助手 — 对话即办结</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentStore } from '@/stores/agent'
import { useTeacherAgentStore } from '@/stores/teacherAgent'
import { sendChatMessage } from '@/api/agent'
import type { ChatMessage, Suggestion } from '@/types'
import { Promotion } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{ role?: 'student' | 'teacher' }>(), { role: 'student' })
const store = props.role === 'teacher' ? useTeacherAgentStore() : useAgentStore()
const router = useRouter()
const input = ref('')
const msgRef = ref<HTMLElement>()
const loading = ref(false)

const actions = [
  { icon: '📅', label: '请假申请', desc: '比赛、病假、事假直接说', color: '#409eff', example: '下周二参加ACM比赛想请假一天' },
  { icon: '📝', label: '记录成长', desc: '获奖/比赛自动写入档案', color: '#67c23a', example: '我获得了挑战杯省赛二等奖' },
  { icon: '📚', label: '查课表', desc: '看看今天上什么课', color: '#e6a23c', example: '查一下今天的课表' },
  { icon: '📊', label: '查成绩', desc: '查看各科成绩和GPA', color: '#f56c6c', example: '帮我查一下成绩' },
  { icon: '📢', label: '官网通知', desc: '教务处最新公告', color: '#b37feb', example: '查一下教务处的最新通知' },
  { icon: '🏫', label: '校园知识', desc: '办事流程、规章制度', color: '#909399', example: '怎么申请在校证明？' },
]

const hints = [
  '图书馆在哪里？', '宿舍管理规定', '考试安排', '有哪些校园风景？'
]

function renderMarkdown(text: string): string {
  let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  html = html
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" class="msg-link">$1</a>')
    .replace(/\n/g, '<br>')
  return html
}

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

  const assistantId = (Date.now() + 1).toString()
  const assistantMsg: ChatMessage = {
    id: assistantId,
    role: 'assistant',
    content: '',
    timestamp: new Date().toISOString(),
  }
  store.addMessage(assistantMsg)

  const history = store.messages.slice(0, -1).map(m => ({ role: m.role, content: m.content }))

  try {
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
  } catch {
    store.addMessage({
      id: (Date.now() + 2).toString(),
      role: 'assistant',
      content: '抱歉，连接失败，请稍后再试。',
      timestamp: new Date().toISOString(),
    })
    loading.value = false
  }
}

function quickSend(text: string) {
  input.value = text
  send()
}

function handleSuggestion(s: Suggestion) {
  if (s.link) router.push(s.link)
}

watch(() => store.messages.length, () => {
  nextTick(() => { msgRef.value?.scrollTo({ top: msgRef.value.scrollHeight, behavior: 'smooth' }) })
})
</script>

<style scoped>
.chat-shell { display: flex; flex-direction: column; height: 100%; background: #fff; }
.messages { flex: 1; overflow-y: auto; padding: 24px 16px 8px; scroll-behavior: smooth; }

/* Welcome */
.welcome { text-align: center; padding: 40px 20px 20px; max-width: 600px; margin: 0 auto; }
.welcome-avatar { margin-bottom: 16px; }
.welcome-img { width: 80px; height: auto; filter: drop-shadow(0 4px 16px rgba(64,158,255,0.3)); }
.welcome-title { font-size: 26px; font-weight: 700; color: #1a1a1a; margin-bottom: 8px; }
.welcome-desc { color: #888; font-size: 14px; margin-bottom: 28px; line-height: 1.5; }
.welcome-actions { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px; }
.action-card { cursor: pointer; transition: transform .15s, box-shadow .15s; border-radius: 12px; }
.action-card:hover { transform: translateY(-2px); }
.action-card :deep(.el-card__body) { display: flex; align-items: center; gap: 10px; padding: 14px; }
.action-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.action-text { text-align: left; }
.action-text strong { display: block; font-size: 14px; color: #333; }
.action-text small { display: block; font-size: 11px; color: #999; margin-top: 2px; }
.welcome-hints { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; }
.hint-tag { cursor: pointer; }

/* Messages */
.msg-row { display: flex; gap: 10px; margin-bottom: 16px; max-width: 720px; margin-left: auto; margin-right: auto; padding: 0 8px; }
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar { flex-shrink: 0; }
.mini-avatar { width: 32px; height: auto; border-radius: 50%; }
.bubble { padding: 12px 16px; border-radius: 16px; line-height: 1.6; font-size: 14px; max-width: 85%; }
.bubble.user { background: #409eff; color: #fff; border-bottom-right-radius: 4px; }
.bubble.assistant { background: #f0f2f5; color: #1a1a1a; border-bottom-left-radius: 4px; }
.msg-text :deep(.msg-link) { color: #409eff; text-decoration: underline; }
.bubble.user .msg-text :deep(a) { color: #fff; text-decoration: underline; }
.thinking { padding: 16px; }
.dot-pulse { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #409eff; animation: pulse 1.2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: .3; transform: scale(.8); } 50% { opacity: 1; transform: scale(1.2); } }
.suggestions { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
.suggestion-tag { cursor: pointer; }

/* Input */
.input-bar { flex-shrink: 0; padding: 12px 16px 16px; border-top: 1px solid #f0f0f0; }
.input-wrap { display: flex; gap: 8px; max-width: 720px; margin: 0 auto; }
.chat-input :deep(.el-input__wrapper) { border-radius: 24px; padding: 4px 16px; box-shadow: 0 2px 8px rgba(0,0,0,.06) !important; }
.chat-input :deep(.el-input__inner) { height: 44px; }
.send-btn { border-radius: 50%; width: 44px; height: 44px; padding: 0; flex-shrink: 0; }
.send-btn .el-icon { font-size: 20px; }
.input-foot { text-align: center; font-size: 11px; color: #bbb; margin-top: 8px; }
</style>
