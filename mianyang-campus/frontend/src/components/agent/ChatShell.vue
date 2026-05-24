<template>
  <div class="chat-shell-layout">
    <div class="sidebar-container" :class="{ collapsed }">
      <Sidebar :role="role" @select="onSelect" />
    </div>
    <div class="chat-panel-wrap">
      <ChatPanel
        :key="chatKey"
        :role="role"
        :conversation-id="store.activeId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import Sidebar from './Sidebar.vue'
import ChatPanel from './ChatPanel.vue'
import { useConversationStore, type Conversation } from '@/stores/conversation'
import { useTeacherConversationStore } from '@/stores/teacherConversation'
import { useAgentStore } from '@/stores/agent'
import { useTeacherAgentStore } from '@/stores/teacherAgent'

const props = withDefaults(defineProps<{ role?: 'student' | 'teacher' }>(), { role: 'student' })
const store = props.role === 'teacher' ? useTeacherConversationStore() : useConversationStore()
const agentStore = props.role === 'teacher' ? useTeacherAgentStore() : useAgentStore()
const collapsed = computed(() => store.sidebarCollapsed)
const chatKey = ref(0)

async function onSelect(conv: Conversation) {
  store.setActive(conv.id)
  await store.fetchMessages(conv.id)
  const msgs = store.messages.map(m => ({
    id: m.id.toString(),
    role: m.role as 'user' | 'assistant',
    content: m.content,
    timestamp: m.timestamp,
  }))
  agentStore.replaceMessages(msgs)
  chatKey.value++
}

watch(() => store.activeId, () => { chatKey.value++ })

onMounted(() => {
  store.setActive(null)
  agentStore.clearMessages()
  store.fetchList()
})
</script>

<style scoped>
.chat-shell-layout {
  display: flex; height: 100%;
  background: #f5f7fa; border-radius: 12px;
  overflow: hidden; box-shadow: 0 2px 16px rgba(0,0,0,.04);
}
.chat-panel-wrap {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column; background: #fff;
}
</style>
