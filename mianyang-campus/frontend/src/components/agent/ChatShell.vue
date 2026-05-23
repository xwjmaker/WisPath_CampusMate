<template>
  <div class="chat-shell-layout">
    <Sidebar @select="onSelect" />
    <div class="chat-panel-wrap">
      <ChatPanel
        :key="chatKey"
        :conversation-id="store.activeId"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import Sidebar from './Sidebar.vue'
import ChatPanel from './ChatPanel.vue'
import { useConversationStore, type Conversation } from '@/stores/conversation'
import { useAgentStore } from '@/stores/agent'

const store = useConversationStore()
const agentStore = useAgentStore()
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

// Re-create ChatPanel when activeId changes (after first message creates a conversation)
watch(() => store.activeId, () => { chatKey.value++ })

onMounted(() => {
  store.setActive(null)
  agentStore.clearMessages()
  store.fetchList()
})
</script>

<style scoped>
.chat-shell-layout { display: flex; height: 100%; }
.chat-panel-wrap { flex: 1; min-width: 0; display: flex; flex-direction: column; }
</style>
