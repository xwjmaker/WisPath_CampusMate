<template>
  <div class="agent-page">
    <ChatShell />
  </div>
</template>

<script setup lang="ts">
import ChatShell from '@/components/agent/ChatShell.vue'
</script>

<style scoped>
.agent-page { height: calc(100vh - 48px); }
</style>
