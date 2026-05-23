import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import request from '@/utils/request'

export interface Conversation {
  id: number
  title: string
  type: 'normal' | 'project'
  project_template?: string
  project_stage?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export const useConversationStore = defineStore('conversation', () => {
  const list = ref<Conversation[]>([])
  const activeId = ref<number | null>(null)
  const messages = ref<ConversationMessage[]>([])
  const sidebarCollapsed = ref(localStorage.getItem('sidebar_collapsed') === 'true')

  watch(sidebarCollapsed, (v) => {
    localStorage.setItem('sidebar_collapsed', v ? 'true' : 'false')
  })

  async function fetchList() {
    try { list.value = await request.get('/agent/conversations') } catch { /* ignore */ }
  }

  async function createConversation(type: 'normal' | 'project' = 'normal', template?: string, title?: string): Promise<Conversation | null> {
    try {
      const conv = await request.post('/agent/conversations', { type, project_template: template, title })
      list.value.unshift(conv as any)
      return conv as any
    } catch { return null }
  }

  async function updateConversation(id: number, data: Partial<Conversation>) {
    try {
      await request.put(`/agent/conversations/${id}`, data)
      const idx = list.value.findIndex(c => c.id === id)
      if (idx >= 0) Object.assign(list.value[idx], data)
    } catch { /* ignore */ }
  }

  async function deleteConversation(id: number) {
    try {
      await request.delete(`/agent/conversations/${id}`)
      list.value = list.value.filter(c => c.id !== id)
      if (activeId.value === id) activeId.value = null
    } catch { /* ignore */ }
  }

  async function fetchMessages(convId: number) {
    try {
      const msgs = await request.get(`/agent/conversations/${convId}/messages`)
      messages.value = msgs as any
    } catch { messages.value = [] }
  }

  function setActive(convId: number | null) {
    activeId.value = convId
  }

  return {
    list, activeId, messages, sidebarCollapsed,
    fetchList, createConversation, updateConversation, deleteConversation,
    fetchMessages, setActive,
  }
})
