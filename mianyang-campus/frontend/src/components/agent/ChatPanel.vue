<template>
  <div class="chat-modern">
    <div class="messages" ref="msgRef">
      <!-- Welcome Screen -->
      <div v-if="store.messages.length === 0" class="welcome">
        <div class="welcome-glow"></div>
        <div class="welcome-content">
          <div class="ai-character">
            <div class="ai-ring"></div>
            <div class="ai-avatar">绵</div>
          </div>
          <div class="welcome-greeting">
            <h1>你好，我是<span class="gradient-text">绵小城</span></h1>
            <p>你的校园智能管家，所有事情直接跟我聊，一站式办结</p>
          </div>

          <!-- Quick Action Cards -->
          <div class="quick-grid">
            <div class="quick-card" v-for="a in actions" :key="a.label" @click="quickSend(a.example)">
              <div class="qc-icon" :style="{ background: a.color + '12', color: a.color }">{{ a.icon }}</div>
              <div class="qc-body">
                <strong>{{ a.label }}</strong>
                <small>{{ a.desc }}</small>
              </div>
            </div>
          </div>

          <!-- Direct Links -->
          <div class="quick-links">
            <span class="ql-label">快捷入口</span>
            <div class="ql-chip-group">
              <template v-if="props.role === 'teacher'">
                <el-button size="small" round plain @click="quickLink('/teacher')">
                  <el-icon><WarningFilled /></el-icon> 预警雷达
                </el-button>
                <el-button size="small" round plain @click="quickLink('/teacher/students')">
                  <el-icon><User /></el-icon> 学生管理
                </el-button>
                <el-button size="small" round plain @click="quickLink('/teacher/approval')">
                  <el-icon><CircleCheck /></el-icon> 审批管理
                </el-button>
              </template>
              <template v-else>
                <el-button size="small" round plain @click="quickLink('/student/service')">
                  <el-icon><Calendar /></el-icon> 办事服务
                </el-button>
                <el-button size="small" round plain @click="quickLink('/student/growth')">
                  <el-icon><TrendCharts /></el-icon> 成长档案
                </el-button>
                <el-button size="small" round plain @click="quickLink('/student/schedule')">
                  <el-icon><Clock /></el-icon> 课表查询
                </el-button>
                <el-button size="small" round plain @click="quickLink('/student/grade')">
                  <el-icon><DataAnalysis /></el-icon> 成绩查询
                </el-button>
                <el-button size="small" round plain @click="quickLink('/student/campus')">
                  <el-icon><PictureFilled /></el-icon> 校园风采
                </el-button>
              </template>
            </div>
          </div>

          <!-- Hint Tags -->
          <div class="hint-tags">
            <span class="ql-label">试试这样问</span>
            <div class="hint-chip-group">
              <el-tag v-for="h in hints" :key="h" class="hint-chip" hit @click="quickSend(h)">{{ h }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <template v-for="(msg, _i) in store.messages" :key="msg.id">
        <div :class="['msg-row', msg.role]">
          <div v-if="msg.role === 'assistant'" class="msg-avatar-col">
            <div class="assistant-avatar">
              <div class="a-avatar-inner">绵</div>
            </div>
          </div>
          <div class="msg-bubble-col">
            <div :class="['bubble', msg.role]">
              <!-- Render images inline -->
              <div v-if="isImageMessage(msg)" class="bubble-image">
                <img :src="extractImageUrl(msg)" @click="previewImage = extractImageUrl(msg)" />
              </div>
              <div class="msg-text" v-html="renderMarkdown(msg.content)"></div>
              <div v-if="msg.suggestions?.length" class="suggestions">
                <el-tag
                  v-for="s in msg.suggestions"
                  :key="s.text"
                  class="suggestion-tag"
                  effect="plain"
                  @click="handleSuggestion(s)"
                >{{ s.text }}</el-tag>
              </div>
            </div>
            <div class="msg-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>
      </template>

      <!-- Loading -->
      <div v-if="loading" class="msg-row assistant">
        <div class="msg-avatar-col">
          <div class="assistant-avatar">
            <div class="a-avatar-inner">绵</div>
          </div>
        </div>
        <div class="msg-bubble-col">
          <div class="bubble assistant thinking-bubble">
            <span class="typing-dot" v-for="d in 3" :key="d" :style="{ animationDelay: (d * 0.2) + 's' }"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Preview Overlay -->
    <Teleport to="body">
      <div v-if="previewImage" class="image-overlay" @click="previewImage = ''">
        <img :src="previewImage" class="preview-img" />
      </div>
    </Teleport>

    <!-- Input Bar -->
    <div class="input-bar">
      <div class="input-container">
        <div class="input-field-wrap">
          <textarea
            v-model="input"
            :disabled="loading"
            placeholder="输入你的需求，比如「下周二比赛想请假」..."
            class="chat-textarea"
            rows="1"
            @keydown.enter.prevent="send"
          ></textarea>
        </div>
        <div class="input-actions">
          <el-tooltip content="上传文件" placement="top">
            <el-button text class="tool-btn" :disabled="loading" @click="triggerUpload">
              <el-icon><Paperclip /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="上传图片" placement="top">
            <el-button text class="tool-btn" :disabled="loading" @click="triggerImageUpload">
              <el-icon><Picture /></el-icon>
            </el-button>
          </el-tooltip>
          <input ref="fileInputRef" type="file" accept=".jpg,.jpeg,.png,.gif,.bmp,.pdf,.doc,.docx,.zip,.rar" style="display:none" @change="onFileSelected" />
          <input ref="imageInputRef" type="file" accept="image/*" style="display:none" @change="onImageSelected" />
          <el-tooltip :content="micTooltip" placement="top">
            <el-button
              text
              :class="['tool-btn', { 'mic-active': speech.isListening.value || recorder.isRecording.value }]"
              :disabled="loading || (!speech.isSupported.value && !recorder.isSupported.value)"
              @click="toggleMic"
            >
              <el-icon :size="18"><Microphone /></el-icon>
            </el-button>
          </el-tooltip>
          <el-button type="primary" :loading="loading" class="modern-send-btn" @click="send">
            <el-icon v-if="!loading"><Promotion /></el-icon>
          </el-button>
        </div>
      </div>
      <div v-if="pendingFile" class="file-preview-row">
        <el-tag closable :type="fileTypeTag" size="small" @close="pendingFile = null">
          <el-icon style="margin-right:4px;vertical-align:-2px"><Document /></el-icon>
          {{ pendingFile.name }}
        </el-tag>
      </div>
      <p class="input-footnote">绵小城 · 对话即办结</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAgentStore } from '@/stores/agent'
import { useTeacherAgentStore } from '@/stores/teacherAgent'
import { useConversationStore } from '@/stores/conversation'
import { sendChatMessage } from '@/api/agent'
import { getToken } from '@/utils/token'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'
import { useMediaRecorder } from '@/composables/useMediaRecorder'
import type { ChatMessage, Suggestion } from '@/types'
import {
  Promotion, Paperclip, Picture, Document, Calendar, Clock,
  DataAnalysis, TrendCharts, PictureFilled, WarningFilled, User, CircleCheck, Microphone,
} from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{ role?: 'student' | 'teacher'; conversationId?: number | null }>(), { role: 'student' })
const store = props.role === 'teacher' ? useTeacherAgentStore() : useAgentStore()
const convStore = useConversationStore()
const router = useRouter()
const input = ref('')
const msgRef = ref<HTMLElement>()
const loading = ref(false)
const previewImage = ref('')
const speech = useSpeechRecognition()
const recorder = useMediaRecorder()

watch(() => recorder.error.value, (val) => {
  if (val && val !== '转写失败' && val !== '网络错误' && val !== '无法访问麦克风' && val !== '录音失败') {
    input.value += val
  }
})

const micTooltip = computed(() => {
  if (!speech.isSupported.value && recorder.isSupported.value) {
    if (recorder.transcribing.value) return '转写中...'
    if (recorder.isRecording.value) return '录音中...'
    return '录音输入'
  }
  if (!speech.isSupported.value) return '当前浏览器不支持语音输入'
  if (speech.isListening.value) return '正在聆听...'
  return '语音输入'
})

const actions = [
  { icon: '📅', label: '请假申请', desc: '比赛、病假、事假直接说', color: '#409eff', example: '下周二参加ACM区域赛需要请假三天，从5月26号到5月28号' },
  { icon: '📝', label: '记录成长', desc: '获奖/比赛自动写入档案', color: '#67c23a', example: '我获得了挑战杯省赛二等奖，主办方是教育厅，级别是省级' },
  { icon: '📚', label: '查课表', desc: '看看今天上什么课', color: '#e6a23c', example: '查一下这周一的课表' },
  { icon: '📊', label: '查成绩', desc: '查看各科成绩和GPA', color: '#f56c6c', example: '帮我查一下这个学期的成绩和绩点' },
  { icon: '📢', label: '官网通知', desc: '教务处最新公告', color: '#b37feb', example: '查一下教务处发布了哪些最新通知' },
  { icon: '🏫', label: '校园知识', desc: '办事流程、规章制度', color: '#909399', example: '怎么申请在校证明？需要准备哪些材料？' },
]

const hints = [
  '图书馆在哪里？', '宿舍管理规定有哪些？', '这个学期的考试安排是什么？', '我们学校有哪些校园风景？', '奖学金评定标准是什么？'
]

const fileInputRef = ref<HTMLInputElement>()
const imageInputRef = ref<HTMLInputElement>()
const pendingFile = ref<File | null>(null)
const pendingImagePreview = ref('')
let uploadedFileUrl = ''

const fileTypeTag = computed(() => {
  if (!pendingFile.value) return 'info'
  const name = pendingFile.value.name.toLowerCase()
  if (name.match(/\.(jpg|jpeg|png|gif|bmp)$/)) return 'success'
  if (name.match(/\.pdf$/)) return 'danger'
  if (name.match(/\.(doc|docx)$/)) return 'primary'
  return 'info'
})

function triggerUpload() { fileInputRef.value?.click() }
function triggerImageUpload() { imageInputRef.value?.click() }

function toggleMic() {
  if (!speech.isSupported.value && recorder.isSupported.value) {
    if (recorder.isRecording.value) {
      recorder.stop()
    } else {
      recorder.start()
    }
    return
  }
  if (speech.isListening.value) {
    speech.stop()
    if (speech.transcript.value) {
      input.value += speech.transcript.value
    }
  } else {
    speech.start()
  }
}

async function onFileSelected(e: Event) {
  const t = e.target as HTMLInputElement
  if (!t.files?.length) return
  const file = t.files[0]
  if (file.size > 10 * 1024 * 1024) { ElMessage.error('文件不能超过 10MB'); return }
  pendingFile.value = file
  t.value = ''
}

async function onImageSelected(e: Event) {
  const t = e.target as HTMLInputElement
  if (!t.files?.length) return
  const file = t.files[0]
  if (file.size > 10 * 1024 * 1024) { ElMessage.error('文件不能超过 10MB'); return }
  pendingFile.value = file
  pendingImagePreview.value = URL.createObjectURL(file)
  t.value = ''
}

function isImageMessage(msg: ChatMessage): boolean {
  return /\.(jpg|jpeg|png|gif|bmp)/i.test(msg.content) && !msg.content.includes('\n')
}

function extractImageUrl(msg: ChatMessage): string {
  const m = msg.content.match(/https?:\/\/[^\s]+\.(jpg|jpeg|png|gif|bmp)/i)
  return m ? m[0] : ''
}

function renderMarkdown(text: string): string {
  let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  html = html
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" class="msg-link">$1</a>')
    .replace(/\n/g, '<br>')
  return html
}

function formatTime(ts: string): string {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function send() {
  if ((!input.value.trim() && !pendingFile.value) || loading.value) return

  // Get or create conversation
  let cid = props.conversationId
  if (!cid) {
    const conv = await convStore.createConversation('normal')
    if (conv) {
      convStore.setActive(conv.id)
      cid = conv.id
    } else { return }
  }

  if (pendingFile.value) {
    const formData = new FormData()
    formData.append('file', pendingFile.value)
    const token = getToken()
    try {
      const resp = await fetch('/api/upload', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      })
      if (resp.ok) {
        const data = await resp.json()
        uploadedFileUrl = data.url
      }
    } catch { /* silent */ }
  }

  const text = input.value || (uploadedFileUrl ? '请帮我识别这个证明材料并记录到成长档案' : '')
  const userContent = pendingFile.value
    ? `[上传文件: ${pendingFile.value.name}]\n${input.value || '请帮我识别并记录'}`
    : input.value

  const userMsg: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: userContent,
    timestamp: new Date().toISOString(),
  }
  store.addMessage(userMsg)
  input.value = ''
  pendingFile.value = null
  pendingImagePreview.value = ''
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
      uploadedFileUrl || undefined,
      cid,
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
  uploadedFileUrl = ''
}

function quickSend(text: string) {
  input.value = text
  send()
}

function quickLink(path: string) {
  router.push(path)
}

function handleSuggestion(s: Suggestion) {
  if (s.link) router.push(s.link)
}

watch(() => store.messages.length, () => {
  nextTick(() => { msgRef.value?.scrollTo({ top: msgRef.value.scrollHeight, behavior: 'smooth' }) })
})
</script>

<style scoped>
.chat-modern { display: flex; flex-direction: column; height: 100%; background: #fff; }

/* ── Messages Area ── */
.messages { flex: 1; overflow-y: auto; padding: 0; scroll-behavior: smooth; }

/* ── Welcome Screen ── */
.welcome {
  position: relative; min-height: 100%; display: flex; align-items: center; justify-content: center;
  background: linear-gradient(180deg, #f0f8ff 0%, #fafcff 40%, #fff 100%);
  overflow: hidden;
}
.welcome-glow {
  position: absolute; top: -120px; left: 50%; transform: translateX(-50%);
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(64,158,255,.12) 0%, transparent 70%);
  pointer-events: none;
}
.welcome-content { position: relative; z-index: 1; text-align: center; padding: 40px 24px; max-width: 640px; margin: 0 auto; }

.ai-character { position: relative; width: 88px; height: 88px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; }
.ai-ring {
  position: absolute; width: 88px; height: 88px; border-radius: 50%;
  background: conic-gradient(from 0deg, #409eff, #67c23a, #e6a23c, #f56c6c, #409eff);
  animation: spin 4s linear infinite; padding: 3px;
  -webkit-mask: radial-gradient(circle at 50% 50%, transparent 38px, #000 38px);
  mask: radial-gradient(circle at 50% 50%, transparent 38px, #000 38px);
}
@keyframes spin { to { transform: rotate(360deg); } }
.ai-avatar {
  width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; font-weight: 700; color: #fff;
  box-shadow: 0 4px 20px rgba(64,158,255,0.3);
}

.gradient-text {
  background: linear-gradient(135deg, #409eff, #67c23a);
  background-clip: text; -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.welcome-greeting h1 { font-size: 28px; color: #1a1a1a; margin-bottom: 8px; }
.welcome-greeting p { color: #888; font-size: 14px; line-height: 1.6; margin-bottom: 28px; }

/* Quick Cards */
.quick-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 24px; }
.quick-card {
  background: #fff; border-radius: 14px; padding: 14px; cursor: pointer;
  border: 1px solid #f0f0f0; transition: all .2s; text-align: left;
  display: flex; gap: 10px; align-items: flex-start;
}
.quick-card:hover { border-color: #409eff; box-shadow: 0 4px 16px rgba(64,158,255,.12); transform: translateY(-2px); }
.qc-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.qc-body { min-width: 0; }
.qc-body strong { font-size: 13px; color: #333; display: block; }
.qc-body small { font-size: 11px; color: #999; display: block; margin-top: 2px; }

/* Quick Links */
.quick-links { margin-bottom: 16px; }
.ql-label { display: block; font-size: 12px; color: #bbb; margin-bottom: 8px; text-align: center; }
.ql-chip-group { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }

/* Hint Tags */
.hint-tags { }
.hint-chip-group { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; }
.hint-chip { cursor: pointer; border-radius: 20px; font-size: 12px; }

/* ── Message Bubbles ── */
.msg-row { display: flex; gap: 10px; padding: 0 20px; margin-bottom: 20px; max-width: 760px; margin-left: auto; margin-right: auto; width: 100%; box-sizing: border-box; }
.msg-row.user { flex-direction: row-reverse; }

.msg-avatar-col { flex-shrink: 0; }
.assistant-avatar { width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #409eff, #67c23a); display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(64,158,255,.25); }
.a-avatar-inner { font-size: 14px; font-weight: 700; color: #fff; }

.msg-bubble-col { max-width: 85%; min-width: 0; }
.msg-row.user .msg-bubble-col { display: flex; flex-direction: column; align-items: flex-end; }

.bubble { padding: 12px 16px; border-radius: 18px; line-height: 1.6; font-size: 14px; word-break: break-word; }
.bubble.assistant {
  background: #f0f4f9; color: #1a1a1a; border-bottom-left-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.bubble.user {
  background: linear-gradient(135deg, #409eff, #337ecc); color: #fff;
  border-bottom-right-radius: 4px; box-shadow: 0 2px 8px rgba(64,158,255,.2);
}
.bubble-image { margin-bottom: 8px; }
.bubble-image img { max-width: 240px; border-radius: 10px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,.1); transition: transform .2s; }
.bubble-image img:hover { transform: scale(1.02); }
.msg-text :deep(.msg-link) { color: #409eff; text-decoration: underline; }
.bubble.user .msg-text :deep(a) { color: #fff; text-decoration: underline; }

.msg-time { font-size: 11px; color: #bbb; margin-top: 4px; padding-left: 4px; }
.msg-row.user .msg-time { padding-right: 4px; }

/* Typing animation */
.thinking-bubble { padding: 14px 20px; display: flex; gap: 4px; align-items: center; }
.typing-dot { width: 8px; height: 8px; border-radius: 50%; background: #909399; animation: typingPulse 1.2s ease-in-out infinite; }
@keyframes typingPulse { 0%, 100% { opacity: .3; transform: scale(.8); } 50% { opacity: 1; transform: scale(1.2); } }

/* Suggestions */
.suggestions { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
.suggestion-tag { cursor: pointer; border-radius: 16px; }

/* ── Image Preview ── */
.image-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,.8); display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}
.preview-img { max-width: 90vw; max-height: 90vh; border-radius: 12px; box-shadow: 0 8px 40px rgba(0,0,0,.4); }

/* ── Input Bar ── */
.input-bar { flex-shrink: 0; padding: 8px 20px 12px; border-top: 1px solid #f0f0f0; background: #fff; }
.input-container {
  display: flex; align-items: flex-end; gap: 4px;
  max-width: 720px; margin: 0 auto;
  background: #f5f7fa; border-radius: 16px; padding: 6px 6px 6px 16px;
  border: 1px solid #e8e8e8; transition: border-color .2s, box-shadow .2s;
}
.input-container:focus-within { border-color: #409eff; box-shadow: 0 0 0 3px rgba(64,158,255,.1); }

.input-field-wrap { flex: 1; min-width: 0; }
.chat-textarea {
  width: 100%; border: none; background: transparent; outline: none;
  font-size: 14px; font-family: inherit; color: #333; resize: none;
  line-height: 1.5; padding: 6px 0; height: 44px; overflow-y: auto;
}
.chat-textarea::placeholder { color: #bbb; }

.input-actions { display: flex; align-items: center; gap: 2px; flex-shrink: 0; }
.tool-btn { font-size: 18px; color: #909399; border-radius: 8px; width: 32px; height: 32px; padding: 0; margin-bottom: 2px; }
.tool-btn:hover { color: #409eff; background: rgba(64,158,255,.08); }

.modern-send-btn {
  width: 40px; height: 40px; border-radius: 12px; padding: 0; flex-shrink: 0;
  font-size: 18px;
}

.file-preview-row { max-width: 720px; margin: 6px auto 0; }

.input-footnote { text-align: center; font-size: 11px; color: #ccc; margin-top: 6px; letter-spacing: .5px; }

.mic-active {
  color: #f56c6c !important;
  background: rgba(245, 108, 108, 0.1) !important;
  animation: mic-pulse 1.2s ease-in-out infinite;
}
@keyframes mic-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 108, 108, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(245, 108, 108, 0); }
}
</style>
