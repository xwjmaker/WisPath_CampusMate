<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-left" style="cursor:pointer" @click="goTo('/student')">
        <span class="logo">绵小城</span>
        <span class="logo-sub">智慧校园助手</span>
      </div>
      <div class="topbar-right">
        <el-tooltip content="AI 对话" placement="bottom">
          <el-button text circle @click="goTo('/student')">
            <el-icon :size="18"><ChatDotRound /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="校园风采" placement="bottom">
          <el-button text circle @click="goTo('/student/campus')">
            <el-icon :size="18"><PictureFilled /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="成长轨迹" placement="bottom">
          <el-button text circle @click="goTo('/student/growth')">
            <el-icon :size="18"><TrendCharts /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="课表查询" placement="bottom">
          <el-button text circle @click="goTo('/student/schedule')">
            <el-icon :size="18"><Calendar /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="成绩考试" placement="bottom">
          <el-button text circle @click="goTo('/student/grade')">
            <el-icon :size="18"><Document /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="办事服务" placement="bottom">
          <el-button text circle @click="goTo('/student/service')">
            <el-icon :size="18"><Service /></el-icon>
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-dropdown trigger="click">
          <span class="user-btn">
            <el-avatar :size="28">{{ auth.userName?.[0] }}</el-avatar>
            <span class="user-name">{{ auth.userName }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
          </template>
        </el-dropdown>
      </div>
    </header>
    <main class="main-area">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ChatDotRound, PictureFilled, TrendCharts, Calendar, Document, Service } from '@element-plus/icons-vue'

const router = useRouter()
const auth = useAuthStore()

function goTo(path: string) {
  router.push(path)
}

function logout() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
.app-shell { display: flex; flex-direction: column; height: 100vh; background: #fff; }
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 56px; border-bottom: 1px solid #e8e8e8;
  background: #fff; flex-shrink: 0; z-index: 100;
}
.topbar-left { display: flex; align-items: center; gap: 8px; }
.logo { font-size: 20px; font-weight: 700; color: #409eff; letter-spacing: 1px; }
.logo-sub { font-size: 12px; color: #999; }
.topbar-right { display: flex; align-items: center; gap: 4px; }
.user-btn { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 8px; border-radius: 8px; }
.user-btn:hover { background: #f5f5f5; }
.user-name { font-size: 14px; color: #333; }
.main-area { flex: 1; overflow: hidden; }
</style>
