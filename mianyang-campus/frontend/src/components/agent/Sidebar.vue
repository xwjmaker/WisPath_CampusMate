<template>
  <div :class="['sidebar', { collapsed }]">
    <!-- 统一 Header：始终显示切换按钮 -->
    <div class="sidebar-header">
      <div class="header-row">
        <el-tooltip :content="collapsed ? '展开侧边栏' : '收起侧边栏'" placement="right">
          <el-button text circle class="toggle-btn" @click="store.sidebarCollapsed = !store.sidebarCollapsed">
            <el-icon :size="18"><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
          </el-button>
        </el-tooltip>
        <div v-show="!collapsed" class="header-title">对话列表</div>
      </div>
      <div v-show="!collapsed" class="header-actions">
        <el-input v-model="search" placeholder="搜索..." size="small" clearable class="search-input" :prefix-icon="Search" />
        <div class="action-btns">
          <el-button size="small" type="primary" @click="newNormal"><el-icon><Plus /></el-icon> 新对话</el-button>
          <el-dropdown trigger="click" @command="newProject">
            <el-button size="small" plain><el-icon><FolderAdd /></el-icon> 项目</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="competition">学科竞赛</el-dropdown-item>
                <el-dropdown-item command="thesis">毕业论文</el-dropdown-item>
                <el-dropdown-item command="practice">社会实践</el-dropdown-item>
                <el-dropdown-item command="certificate">证书考取</el-dropdown-item>
                <el-dropdown-item command="student_work">学生工作</el-dropdown-item>
                <el-dropdown-item command="custom">自定义项目</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 项目对话 -->
    <div v-show="!collapsed" class="sidebar-section">
      <div class="section-header" @click="projectExpanded = !projectExpanded">
        <el-icon><CaretRight v-if="!projectExpanded" /><CaretBottom v-else /></el-icon>
        <span>项目</span>
        <el-tag size="small" round>{{ projects.length }}</el-tag>
      </div>
      <div v-if="projectExpanded" class="section-items">
        <div v-for="c in projects" :key="c.id"
          :class="['conv-item', { active: c.id === store.activeId }]"
          @click="selectConv(c)">
          <el-icon class="conv-icon"><FolderOpened /></el-icon>
          <div class="conv-info">
            <div class="conv-title">{{ c.title }}</div>
            <div v-if="c.project_stage" class="conv-stage"><span class="stage-text">{{ c.project_stage }}</span></div>
          </div>
          <el-dropdown trigger="click" @command="(cmd: string) => handleCmd(cmd, c)">
            <el-button text circle size="small" class="conv-more" @click.stop>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-item command="rename">重命名</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 历史对话 -->
    <div v-show="!collapsed" class="sidebar-section">
      <div class="section-header" @click="historyExpanded = !historyExpanded">
        <el-icon><CaretRight v-if="!historyExpanded" /><CaretBottom v-else /></el-icon>
        <span>历史</span>
        <el-tag size="small" round>{{ histories.length }}</el-tag>
      </div>
      <div v-if="historyExpanded" class="section-items">
        <div v-for="c in filteredHistories" :key="c.id"
          :class="['conv-item', { active: c.id === store.activeId }]"
          @click="selectConv(c)">
          <el-icon class="conv-icon"><ChatDotRound /></el-icon>
          <div class="conv-info">
            <div class="conv-title">{{ c.title }}</div>
            <div class="conv-date">{{ timeLabel(c.updated_at) }}</div>
          </div>
        </div>
        <div v-if="filteredHistories.length === 0" class="empty-hint">
          {{ search ? '无匹配对话' : '暂无历史对话' }}
        </div>
      </div>
    </div>

    <!-- 收起态快捷操作 -->
    <div v-show="collapsed" class="collapsed-actions">
      <el-tooltip content="新对话" placement="right">
        <el-button text circle @click="newNormal"><el-icon :size="18"><Plus /></el-icon></el-button>
      </el-tooltip>
      <el-tooltip content="项目" placement="right">
        <el-dropdown trigger="click" @command="newProject">
          <el-button text circle><el-icon :size="18"><FolderAdd /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="competition">学科竞赛</el-dropdown-item>
              <el-dropdown-item command="thesis">毕业论文</el-dropdown-item>
              <el-dropdown-item command="practice">社会实践</el-dropdown-item>
              <el-dropdown-item command="certificate">证书考取</el-dropdown-item>
              <el-dropdown-item command="student_work">学生工作</el-dropdown-item>
              <el-dropdown-item command="custom">自定义项目</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  Search, Plus, FolderAdd, Expand, Fold, CaretRight, CaretBottom,
  FolderOpened, ChatDotRound, MoreFilled,
} from '@element-plus/icons-vue'
import { useConversationStore, type Conversation } from '@/stores/conversation'
import { useTeacherConversationStore } from '@/stores/teacherConversation'
import { useAgentStore } from '@/stores/agent'
import { useTeacherAgentStore } from '@/stores/teacherAgent'

const props = withDefaults(defineProps<{ role?: 'student' | 'teacher' }>(), { role: 'student' })
const store = props.role === 'teacher' ? useTeacherConversationStore() : useConversationStore()
const agentStore = props.role === 'teacher' ? useTeacherAgentStore() : useAgentStore()
const search = ref('')
const projectExpanded = ref(false)
const historyExpanded = ref(true)
const emit = defineEmits<{ select: [conv: Conversation] }>()

const projects = computed(() => store.list.filter(c => c.type === 'project'))
const histories = computed(() => store.list.filter(c => c.type === 'normal'))
const filteredHistories = computed(() => {
  if (!search.value) return histories.value
  const q = search.value.toLowerCase()
  return histories.value.filter(c => c.title.toLowerCase().includes(q))
})
const collapsed = computed(() => store.sidebarCollapsed)

function selectConv(c: Conversation) {
  if (c.id === store.activeId) return
  emit('select', c)
}

async function newNormal() {
  if (agentStore.messages.length > 0) {
    const conv = await store.createConversation('normal')
    if (conv) emit('select', conv)
  } else {
    store.setActive(null)
    agentStore.clearMessages()
  }
}

async function newProject(template: string) {
  let title = ''
  if (template === 'competition') {
    try {
      const { value } = await ElMessageBox.prompt('请输入竞赛名称', '新建学科竞赛项目')
      if (!value) return; title = value
    } catch { return }
  } else if (template === 'custom') {
    try {
      const { value } = await ElMessageBox.prompt('请输入项目名称', '自定义项目')
      if (!value) return; title = value
    } catch { return }
  }
  const conv = await store.createConversation('project', template, title)
  if (conv) emit('select', conv)
}

async function handleCmd(cmd: string, c: Conversation) {
  if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm(`确定删除「${c.title}」？`)
      await store.deleteConversation(c.id)
      if (store.activeId === c.id) { store.setActive(null); agentStore.clearMessages() }
    } catch {}
  } else if (cmd === 'rename') {
    try {
      const { value } = await ElMessageBox.prompt('重命名', '', { inputValue: c.title })
      if (value) await store.updateConversation(c.id, { title: value })
    } catch {}
  }
}

function timeLabel(d: string): string {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const dayDiff = Math.floor((startOfToday.getTime() - date.getTime()) / 86400000)
  if (dayDiff < 0) return '刚刚'
  if (dayDiff === 0) return '今天'
  if (dayDiff === 1) return '昨天'
  if (dayDiff <= 3) return '三天前'
  if (dayDiff <= 7) return '一周前'
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

onMounted(() => { store.fetchList() })
</script>

<style scoped>
.sidebar {
  width: 280px; height: 100%;
  background: rgba(255,255,255,.92); backdrop-filter: blur(16px);
  border-right: 1px solid rgba(0,0,0,.06);
  display: flex; flex-direction: column; flex-shrink: 0;
  transition: width .25s cubic-bezier(.4,0,.2,1);
  overflow: hidden;
  box-shadow: 1px 0 8px rgba(0,0,0,.03);
}
.sidebar.collapsed { width: 52px; }

/* Header */
.sidebar-header { flex-shrink: 0; border-bottom: 1px solid rgba(0,0,0,.04); }
.header-row { display: flex; align-items: center; gap: 4px; padding: 10px 8px; }
.toggle-btn { width: 32px; height: 32px; flex-shrink: 0; color: #666; }
.toggle-btn:hover { color: #409eff; background: rgba(64,158,255,.08); }
.header-title { font-size: 14px; font-weight: 600; color: #333; white-space: nowrap; }
.header-actions { padding: 0 10px 10px; display: flex; flex-direction: column; gap: 8px; }
.search-input { width: 100%; }
.action-btns { display: flex; gap: 6px; }
.action-btns .el-button { flex: 1; font-size: 12px; }

/* Sections */
.sidebar-section { border-bottom: 1px solid rgba(0,0,0,.04); }
.section-header {
  display: flex; align-items: center; gap: 4px; padding: 8px 12px;
  font-size: 12px; color: #888; cursor: pointer; user-select: none;
  transition: background .15s;
}
.section-header:hover { background: rgba(0,0,0,.02); }
.section-header .el-icon { font-size: 12px; }
.section-items { margin-bottom: 4px; }

.conv-item {
  display: flex; align-items: center; gap: 8px; padding: 7px 12px;
  cursor: pointer; position: relative; border-radius: 6px; margin: 1px 6px;
  transition: background .15s;
}
.conv-item:hover { background: rgba(0,0,0,.04); }
.conv-item.active { background: rgba(64,158,255,.1); }
.conv-icon { font-size: 16px; color: #909399; flex-shrink: 0; }
.conv-item.active .conv-icon { color: #409eff; }
.conv-info { flex: 1; min-width: 0; }
.conv-title { font-size: 13px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.conv-date { font-size: 11px; color: #aaa; margin-top: 1px; }
.conv-stage { margin-top: 2px; }
.stage-text { font-size: 11px; color: #999; }
.conv-more { opacity: 0; flex-shrink: 0; }
.conv-item:hover .conv-more { opacity: 1; }
.empty-hint { text-align: center; font-size: 12px; color: #bbb; padding: 16px; }

/* Collapsed actions */
.collapsed-actions { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 16px 0; }
.collapsed-actions .el-button { color: #666; }
.collapsed-actions .el-button:hover { color: #409eff; background: rgba(64,158,255,.08); }
</style>
