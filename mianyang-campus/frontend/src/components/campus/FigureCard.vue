<template>
  <el-card shadow="hover">
    <el-avatar :size="80" :src="figure.avatar" style="margin:0 auto;display:block" />
    <h3 style="text-align:center">{{ figure.name }}</h3>
    <p style="text-align:center;color:#666">{{ figure.title }}</p>
    <p>{{ figure.description }}</p>
  </el-card>
</template>

<script setup lang="ts">
import type { CampusFigure } from '@/types'
defineProps<{ figure: CampusFigure }>()
</script>
