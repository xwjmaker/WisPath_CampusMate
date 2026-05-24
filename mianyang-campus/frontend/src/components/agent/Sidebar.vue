<template>
  <div :class="['sidebar', { collapsed }]">
    <div class="sidebar-header">
      <div v-if="!collapsed" class="sidebar-top">
        <el-input
          v-model="search"
          placeholder="搜索历史对话..."
          size="small"
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
        <div class="sidebar-actions">
          <el-button size="small" type="primary" plain @click="newNormal">
            <el-icon><Plus /></el-icon> 新对话
          </el-button>
          <el-dropdown trigger="click" @command="newProject">
            <el-button size="small" plain>
              <el-icon><FolderAdd /></el-icon> 新建项目
            </el-button>
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
      <div v-else class="sidebar-top-collapsed">
        <el-button text circle @click="store.sidebarCollapsed = false">
          <el-icon :size="20"><Expand /></el-icon>
        </el-button>
      </div>
    </div>

    <div v-if="!collapsed" class="sidebar-body">
      <div class="project-group">
        <div class="group-header" @click="projectExpanded = !projectExpanded">
          <el-icon><CaretRight v-if="!projectExpanded" /><CaretBottom v-else /></el-icon>
          <span>项目对话</span>
          <el-tag size="small" type="warning" round>{{ projects.length }}</el-tag>
        </div>
        <div v-if="projectExpanded" class="group-items">
          <div
            v-for="c in projects" :key="c.id"
            :class="['conv-item', { active: c.id === store.activeId }]"
            @click="selectConv(c)"
          >
            <el-icon class="conv-icon"><FolderOpened /></el-icon>
            <div class="conv-info">
              <div class="conv-title">{{ c.title }}</div>
              <div v-if="c.project_stage" class="conv-stage">
                <el-progress :percentage="stageProgress(c)" :stroke-width="4" :show-text="false" />
                <span class="stage-text">{{ c.project_stage }}</span>
              </div>
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

      <div class="history-group">
        <div class="group-header" @click="historyExpanded = !historyExpanded">
          <el-icon><CaretRight v-if="!historyExpanded" /><CaretBottom v-else /></el-icon>
          <span>历史对话</span>
          <el-tag size="small" round>{{ histories.length }}</el-tag>
        </div>
        <div v-if="historyExpanded" class="group-items">
          <div
            v-for="c in filteredHistories" :key="c.id"
            :class="['conv-item', { active: c.id === store.activeId }]"
            @click="selectConv(c)"
          >
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
    </div>

    <div v-if="collapsed" class="sidebar-collapsed-actions">
      <el-tooltip content="展开侧边栏" placement="right">
        <el-button text circle @click="store.sidebarCollapsed = false">
          <el-icon :size="20"><Expand /></el-icon>
        </el-button>
      </el-tooltip>
      <el-tooltip content="新对话" placement="right">
        <el-button text circle @click="newNormal">
          <el-icon :size="20"><Plus /></el-icon>
        </el-button>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  Search, Plus, FolderAdd, Expand, CaretRight, CaretBottom,
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

function stageProgress(c: Conversation): number {
  const stages: Record<string, string[]> = {
    competition: ['赛前准备', '方案设计', '实施优化', '答辩展示'],
    thesis: ['选题开题', '文献综述', '实验/调研', '撰写修改', '答辩'],
    practice: ['方案申报', '前期准备', '实施执行', '总结评优'],
    certificate: ['考情分析', '学习规划', '备考刷题', '考前冲刺'],
    student_work: ['活动策划', '审批协调', '执行落地', '复盘总结'],
  }
  const ss = stages[c.project_template || ''] || []
  const idx = ss.indexOf(c.project_stage || '')
  return idx >= 0 ? Math.round(((idx + 1) / ss.length) * 100) : 0
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
      if (!value) return
      title = value
    } catch { return }
  } else if (template === 'custom') {
    try {
      const { value } = await ElMessageBox.prompt('请输入项目名称', '自定义项目')
      if (!value) return
      title = value
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
      if (store.activeId === c.id) {
        store.setActive(null)
        agentStore.clearMessages()
      }
    } catch { /* cancelled */ }
  } else if (cmd === 'rename') {
    try {
      const { value } = await ElMessageBox.prompt('重命名', '', { inputValue: c.title })
      if (value) await store.updateConversation(c.id, { title: value })
    } catch { /* cancelled */ }
  }
}

onMounted(() => { store.fetchList() })
</script>

<style scoped>
.sidebar {
  width: 280px; height: 100%; background: #fafafa; border-right: 1px solid #e8e8e8;
  display: flex; flex-direction: column; flex-shrink: 0; transition: width .2s;
  overflow: hidden;
}
.sidebar.collapsed { width: 48px; }
.sidebar-header { flex-shrink: 0; padding: 12px; border-bottom: 1px solid #f0f0f0; }
.sidebar-top { display: flex; flex-direction: column; gap: 8px; }
.search-input { width: 100%; }
.sidebar-actions { display: flex; gap: 6px; }
.sidebar-actions .el-button { flex: 1; font-size: 12px; }
.sidebar-top-collapsed { text-align: center; padding: 8px 0; }
.sidebar-body { flex: 1; overflow-y: auto; padding: 8px 0; }
.sidebar-collapsed-actions { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 16px 0; }
.group-header {
  display: flex; align-items: center; gap: 4px; padding: 8px 12px;
  font-size: 13px; color: #666; cursor: pointer; user-select: none;
}
.group-header:hover { background: #f0f0f0; }
.group-header .el-icon { font-size: 14px; }
.group-items { margin-bottom: 4px; }
.conv-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  cursor: pointer; position: relative;
}
.conv-item:hover { background: #f0f2f5; }
.conv-item.active { background: #e6f0ff; }
.conv-icon { font-size: 18px; color: #909399; flex-shrink: 0; }
.conv-item.active .conv-icon { color: #409eff; }
.conv-info { flex: 1; min-width: 0; }
.conv-title { font-size: 13px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.conv-date { font-size: 11px; color: #bbb; margin-top: 2px; }
.conv-stage { margin-top: 4px; display: flex; align-items: center; gap: 6px; }
.conv-stage .el-progress { flex: 1; }
.stage-text { font-size: 11px; color: #999; white-space: nowrap; }
.conv-more { opacity: 0; flex-shrink: 0; }
.conv-item:hover .conv-more { opacity: 1; }
.empty-hint { text-align: center; font-size: 12px; color: #bbb; padding: 20px; }
</style>
