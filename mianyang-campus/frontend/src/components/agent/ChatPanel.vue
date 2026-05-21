<template>
  <div class="chat-container">
    <div class="chat-body">
      <div class="character-side">
        <VirtualCharacter :state="charState" />
      </div>
      <div class="messages" ref="msgRef">
        <div v-if="store.messages.length === 0" class="welcome">
          <VirtualCharacter state="idle" />
          <h2>你好，我是绵小城</h2>
          <p class="welcome-desc">绵阳城市学院智慧校园AI助手，随时为你解答校园相关问题</p>
          <div class="welcome-hints">
            <el-tag v-for="h in hints" :key="h" class="hint-tag" @click="quickSend(h)">{{ h }}</el-tag>
          </div>
        </div>
        <div v-for="msg in store.messages" :key="msg.id" :class="['message', msg.role]">
          <div class="bubble">
            <div v-html="renderMarkdown(msg.content)" class="msg-content"></div>
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
          <div class="bubble thinking-bubble">
            <div class="thinking-text">绵小城正在思考</div>
          </div>
        </div>
      </div>
    </div>
    <div class="input-area">
      <el-input
        v-model="input"
        :disabled="loading"
        placeholder="输入你的问题..."
        @keyup.enter="send"
      />
      <el-button type="primary" :loading="loading" style="margin-left:12px" @click="send">
        发送
      </el-button>
      <el-button v-if="store.messages.length > 0" text size="small" style="margin-left:4px" @click="clear">
        清空
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentStore } from '@/stores/agent'
import { sendChatMessage } from '@/api/agent'
import type { ChatMessage, Suggestion } from '@/types'
import VirtualCharacter from './VirtualCharacter.vue'

const store = useAgentStore()
const router = useRouter()
const input = ref('')
const msgRef = ref<HTMLElement>()
const loading = ref(false)

const charState = computed(() => {
  if (loading.value) return 'thinking'
  if (store.messages.length === 0) return 'idle'
  return 'idle'
})

const hints = [
  '怎么请假？',
  '图书馆在哪里？',
  '如何申请在校证明？',
  '宿舍管理规定',
]

function renderMarkdown(text: string): string {
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
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
    const assistantMsg: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '抱歉，连接失败，请稍后再试。',
      timestamp: new Date().toISOString(),
    }
    store.addMessage(assistantMsg)
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

function clear() {
  store.clearMessages()
}

watch(() => store.messages.length, () => {
  nextTick(() => { msgRef.value?.scrollTo({ top: msgRef.value.scrollHeight, behavior: 'smooth' }) })
})
</script>

<style scoped>
.chat-container { display: flex; flex-direction: column; height: calc(100vh - 140px); }
.chat-body { display: flex; flex: 1; overflow: hidden; }
.character-side {
  width: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
  flex-shrink: 0;
}
.messages { flex: 1; overflow-y: auto; padding: 16px; }
.message { margin-bottom: 16px; }
.message.user { display: flex; justify-content: flex-end; }
.message.assistant { display: flex; justify-content: flex-start; }
.bubble { max-width: 80%; padding: 12px 16px; border-radius: 8px; background: #f0f0f0; line-height: 1.6; }
.message.user .bubble { background: #409eff; color: #fff; }
.suggestions { margin-top: 8px; }
.input-area { display: flex; align-items: center; padding: 16px; border-top: 1px solid #eee; flex-shrink: 0; }
.welcome { text-align: center; padding: 20px; }
.welcome :deep(.character) { transform: scale(1.4); margin-bottom: 8px; }
.welcome h2 { font-size: 24px; color: #333; margin-bottom: 8px; }
.welcome-desc { color: #999; font-size: 14px; margin-bottom: 24px; }
.welcome-hints { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
.hint-tag { cursor: pointer; }
.hint-tag:hover { opacity: 0.8; }
.thinking-bubble { display: flex; align-items: center; gap: 8px; }
.thinking-text { color: #999; font-size: 14px; }
.msg-content :deep(.msg-link) { color: #409eff; text-decoration: underline; }
.msg-content :deep(a) { color: #409eff; text-decoration: underline; }
.message.user .msg-content :deep(a) { color: #fff; text-decoration: underline; }
</style>
