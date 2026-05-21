<template>
  <el-container style="min-height:100vh">
    <el-aside width="220px">
      <el-menu :router="true" :default-active="route.path" style="height:100%">
        <div class="logo">智慧校园</div>
        <el-menu-item index="/student">
          <el-icon><HomeFilled /></el-icon>首页
        </el-menu-item>
        <el-menu-item index="/student/agent">
          <el-icon><ChatDotSquare /></el-icon>智能助手
        </el-menu-item>
        <el-menu-item index="/student/campus">
          <el-icon><PictureFilled /></el-icon>校园风采
        </el-menu-item>
        <el-menu-item index="/student/growth">
          <el-icon><TrendCharts /></el-icon>成长轨迹
        </el-menu-item>
        <el-menu-item index="/student/schedule">
          <el-icon><Calendar /></el-icon>课表查询
        </el-menu-item>
        <el-menu-item index="/student/grade">
          <el-icon><Document /></el-icon>成绩考试
        </el-menu-item>
        <el-menu-item index="/student/service">
          <el-icon><Service /></el-icon>办事服务
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>欢迎，{{ auth.userName }}</span>
        <el-button text @click="logout">退出</el-button>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  HomeFilled, ChatDotSquare, PictureFilled, TrendCharts,
  Calendar, Document, Service
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
    router.push('/')
}
</script>

<style scoped>
.logo { height: 60px; line-height: 60px; text-align: center; font-size: 18px; font-weight: bold; color: #409eff; }
.header { display: flex; justify-content: flex-end; align-items: center; border-bottom: 1px solid #eee; }
</style>
