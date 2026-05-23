import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { ChatMessage } from '@/types'

const STORAGE_KEY = 'campus_teacher_chat_messages'

function loadMessages(): ChatMessage[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export const useTeacherAgentStore = defineStore('teacherAgent', () => {
  const messages = ref<ChatMessage[]>(loadMessages())
  const loading = ref(false)

  watch(messages, (val) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(val.slice(-100)))
  }, { deep: true })

  function addMessage(msg: ChatMessage) {
    messages.value.push(msg)
  }

  function replaceMessages(msgs: ChatMessage[]) {
    messages.value = msgs
    localStorage.setItem(STORAGE_KEY, JSON.stringify(msgs.slice(-100)))
  }

  function clearMessages() {
    messages.value = []
    localStorage.removeItem(STORAGE_KEY)
  }

  return { messages, loading, addMessage, replaceMessages, clearMessages }
})
