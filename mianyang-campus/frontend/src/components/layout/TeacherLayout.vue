<template>
  <el-container style="min-height:100vh">
    <el-aside width="200px">
      <el-menu :router="true" :default-active="route.path" style="height:100%">
        <div class="logo">教师中心</div>
        <el-menu-item index="/teacher">
          <el-icon><WarningFilled /></el-icon>预警雷达
        </el-menu-item>
        <el-menu-item index="/teacher/agent">
          <el-icon><ChatDotSquare /></el-icon>智能助手
        </el-menu-item>
        <el-menu-item index="/teacher/approval">
          <el-icon><CircleCheck /></el-icon>审批管理
        </el-menu-item>
        <el-menu-item index="/teacher/students">
          <el-icon><User /></el-icon>学生成长
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>{{ auth.userName }}，欢迎回来</span>
        <el-button text @click="logout">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { WarningFilled, ChatDotSquare, CircleCheck, User } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; font-weight: bold; color: #f56c6c; letter-spacing: 2px; }
.header { display: flex; justify-content: flex-end; align-items: center; border-bottom: 1px solid #eee; }
</style>
