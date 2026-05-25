<template>
  <div class="agent-page">
    <ChatShell role="teacher" />
  </div>
</template>

<script setup lang="ts">
import ChatShell from '@/components/agent/ChatShell.vue'
</script>

<style scoped>
.agent-page { height: calc(100vh - 56px); }
</style>
