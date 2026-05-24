<template>
  <div class="teacher-shell">
    <aside class="t-sidebar">
      <div class="t-logo">
        <img src="/images/校徽.png" class="t-badge" />
        <span class="t-motto">博学、笃行<br/>严谨、创新</span>
      </div>
      <el-menu :router="true" :default-active="route.path" class="t-menu">
        <el-menu-item index="/teacher">
          <el-icon><HomeFilled /></el-icon><span>首页</span>
        </el-menu-item>
        <el-menu-item index="/teacher/agent">
          <el-icon><ChatDotSquare /></el-icon><span>智能助手</span>
        </el-menu-item>
        <el-menu-item index="/teacher/approval">
          <el-icon><CircleCheck /></el-icon><span>审批管理</span>
        </el-menu-item>
        <el-menu-item index="/teacher/students">
          <el-icon><User /></el-icon><span>学生成长</span>
        </el-menu-item>
        <el-menu-item index="/teacher/messages">
          <el-icon><Message /></el-icon>
          <span>消息</span>
          <el-badge v-if="unreadCount" :value="unreadCount" class="msg-badge" />
        </el-menu-item>
      </el-menu>
      <div class="t-user">
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="t-user-btn">
            <el-avatar :size="32">{{ auth.userName?.[0] }}</el-avatar>
            <span class="t-user-name">{{ auth.userName }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-item command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </template>
        </el-dropdown>
      </div>
    </aside>
    <main class="t-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getConversations } from '@/api/messages'
import { HomeFilled, ChatDotSquare, CircleCheck, User, Message, ArrowDown, SwitchButton } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const unreadCount = ref(0)
let pollTimer: any = null

function handleCommand(cmd: string) {
  if (cmd === 'logout') { auth.logout(); router.push('/login') }
}

async function pollUnread() {
  if (auth.role !== 'teacher' && auth.role !== 'admin') return
  try {
    const convs: any[] = await getConversations()
    unreadCount.value = convs.reduce((sum: number, c: any) => sum + c.unread_count, 0)
  } catch {}
}

onMounted(() => { pollUnread(); pollTimer = setInterval(pollUnread, 5000) })
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer) })
</script>

<style scoped>
.teacher-shell { display: flex; height: 100vh; background: #f5f7fa; }
.t-sidebar {
  width: 220px; flex-shrink: 0; display: flex; flex-direction: column;
  background: rgba(255,255,255,.85); backdrop-filter: blur(20px);
  border-right: 1px solid rgba(0,0,0,.06); box-shadow: 2px 0 12px rgba(0,0,0,.03);
}
.t-logo {
  display: flex; align-items: center; gap: 10px; padding: 20px 16px;
  border-bottom: 1px solid #f0f0f0;
}
.t-badge { height: 36px; width: auto; }
.t-motto {
  font-size: 14px; font-weight: 700; line-height: 1.4;
  background: linear-gradient(135deg, #c41d7f, #e8a020);
  background-clip: text; -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; letter-spacing: 3px;
}
.t-menu { flex: 1; border-right: none; --el-menu-bg-color: transparent; }
.t-menu .el-menu-item { margin: 2px 8px; border-radius: 8px; }
.t-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, #409eff, #337ecc);
  color: #fff; font-weight: 600;
}
.t-menu .el-menu-item.is-active .el-icon { color: #fff; }
.msg-badge { margin-left: auto; }
.t-user { padding: 12px 16px; border-top: 1px solid #f0f0f0; }
.t-user-btn {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 4px 8px; border-radius: 8px; transition: background .2s;
}
.t-user-btn:hover { background: #f0f4f9; }
.t-user-name { font-size: 14px; color: #333; flex: 1; }
.t-main { flex: 1; overflow-y: auto; padding: 24px; }
</style>
