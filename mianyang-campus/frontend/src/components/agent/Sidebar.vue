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
          <el-dropdown v-if="props.role !== 'teacher'" trigger="click" @command="newProject">
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

    <!-- 可滚动列表 -->
    <div v-show="!collapsed" class="sidebar-scroll">
      <!-- 项目对话（仅学生端） -->
      <div v-if="props.role !== 'teacher'" class="sidebar-section">
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
            <el-dropdown trigger="click" @command="(cmd: string) => handleConvCmd(cmd, c)" @click.stop>
              <el-button text circle size="small" class="conv-more">
                <el-icon :size="14"><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename"><el-icon><Edit /></el-icon> 重命名</el-dropdown-item>
                  <el-dropdown-item command="delete" divided><el-icon color="#f56c6c"><Delete /></el-icon> 删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- 历史对话 -->
      <div class="sidebar-section">
        <div class="section-header" @click="historyExpanded = !historyExpanded">
          <el-icon><CaretRight v-if="!historyExpanded" /><CaretBottom v-else /></el-icon>
          <span>历史</span>
          <el-tag size="small" round>{{ histories.length }}</el-tag>
          <div v-show="historyExpanded && histories.length > 0" class="header-actions" @click.stop>
            <template v-if="!batchMode">
              <span class="action-link" @click="enterBatchMode">批量管理</span>
            </template>
            <template v-else>
              <span class="action-link danger" :class="{ disabled: selectedIds.size === 0 }" @click="batchDelete">删除{{ selectedIds.size > 0 ? `(${selectedIds.size})` : '' }}</span>
              <span class="action-divider">|</span>
              <span class="action-link" @click="exitBatchMode">取消</span>
            </template>
          </div>
        </div>
        <div v-if="historyExpanded" class="section-items">
          <div v-for="c in filteredHistories" :key="c.id"
            :class="['conv-item', { active: c.id === store.activeId && !batchMode }]"
            @click="batchMode ? toggleSelect(c.id) : selectConv(c)">
            <el-checkbox v-if="batchMode" :model-value="selectedIds.has(c.id)" @click.stop @change="toggleSelect(c.id)" class="conv-check" />
            <el-icon class="conv-icon"><ChatDotRound /></el-icon>
            <div class="conv-info">
              <div class="conv-title">{{ c.title }}</div>
              <div class="conv-date">{{ timeLabel(c.updated_at) }}</div>
            </div>
            <el-dropdown v-if="!batchMode" trigger="click" @command="(cmd: string) => handleConvCmd(cmd, c)" @click.stop>
              <el-button text circle size="small" class="conv-more">
                <el-icon :size="14"><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename"><el-icon><Edit /></el-icon> 重命名</el-dropdown-item>
                  <el-dropdown-item command="delete" divided><el-icon color="#f56c6c"><Delete /></el-icon> 删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div v-if="filteredHistories.length === 0" class="empty-hint">
            {{ search ? '无匹配对话' : '暂无历史对话' }}
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  Search, Plus, FolderAdd, Expand, Fold, CaretRight, CaretBottom,
  FolderOpened, ChatDotRound, Delete, Edit, MoreFilled,
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
const batchMode = ref(false)
const selectedIds = ref(new Set<number>())
const emit = defineEmits<{ select: [conv: Conversation]; new: [] }>()

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
  if (agentStore.messages.length > 0 && !store.activeId) {
    await store.createConversation('normal')
  }
  store.setActive(null)
  agentStore.clearMessages()
  emit('new')
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
  else emit('new')
}

function handleConvCmd(cmd: string, c: Conversation) {
  if (cmd === 'delete') {
    deleteConv(c)
  } else if (cmd === 'rename') {
    renameConv(c)
  }
}

async function renameConv(c: Conversation) {
  try {
    const { value } = await ElMessageBox.prompt('重命名', '', { inputValue: c.title })
    if (value) await store.updateConversation(c.id, { title: value })
  } catch {}
}

function enterBatchMode() {
  batchMode.value = true
  selectedIds.value = new Set()
}

function exitBatchMode() {
  batchMode.value = false
  selectedIds.value = new Set()
}

function toggleSelect(id: number) {
  const s = new Set(selectedIds.value)
  if (s.has(id)) s.delete(id)
  else s.add(id)
  selectedIds.value = s
}

async function batchDelete() {
  if (selectedIds.value.size === 0) return
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.size} 个对话？`)
    const ids = [...selectedIds.value]
    for (const id of ids) {
      await store.deleteConversation(id)
    }
    if (ids.includes(store.activeId ?? -1)) {
      const remaining = store.list.filter(x => !ids.includes(x.id))
      if (remaining.length > 0) {
        const next = remaining.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())[0]
        emit('select', next)
      } else {
        emit('new')
      }
    }
    exitBatchMode()
  } catch {}
}

async function deleteConv(c: Conversation) {
  try {
    await ElMessageBox.confirm(`确定删除「${c.title}」？`)
    const wasActive = store.activeId === c.id
    await store.deleteConversation(c.id)
    if (wasActive) {
      const remaining = store.list.filter(x => x.id !== c.id)
      if (remaining.length > 0) {
        const next = remaining.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())[0]
        emit('select', next)
      } else {
        emit('new')
      }
    }
  } catch {}
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

onMounted(() => {
  store.fetchList()
})
</script>

<style scoped>
.sidebar {
  width: 260px; height: 100%;
  background: #fafafa; border-right: 1px solid #f0f0f0;
  display: flex; flex-direction: column; flex-shrink: 0;
  transition: width .3s cubic-bezier(0.34, 1.56, 0.64, 1);
  overflow: hidden;
}
.sidebar.collapsed { width: 48px; }

/* Header */
.sidebar-header { 
  flex-shrink: 0; 
  padding: 12px 10px 8px;
  animation: fadeInDown 0.2s ease-out;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

.header-row { display: flex; align-items: center; gap: 2px; margin-bottom: 10px; }
.toggle-btn { 
  width: 28px; height: 28px; flex-shrink: 0; color: #999; border-radius: 6px;
  transition: all 0.15s ease;
}
.toggle-btn:hover { 
  color: #6366f1; 
  background: rgba(99,102,241,.06);
  transform: rotate(90deg);
}
.header-title { font-size: 13px; font-weight: 600; color: #333; letter-spacing: .5px; }
.search-input :deep(.el-input__wrapper) { border-radius: 8px; background: #f0f0f0; box-shadow: none; border: 1px solid transparent; transition: all 0.3s ease; }
.search-input :deep(.el-input__wrapper:hover) { border-color: #e0e0e0; }
.search-input :deep(.el-input__wrapper.is-focus) { border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99,102,241,.08); }
.action-btns { display: flex; gap: 4px; }
.action-btns .el-button { 
  flex: 1; font-size: 12px; border-radius: 8px; height: 30px;
  transition: all 0.2s ease;
}
.action-btns .el-button:hover {
  transform: translateY(-1px);
}
.action-btns .el-button--primary { background: #6366f1; border-color: #6366f1; }
.action-btns .el-button--primary:hover { background: #5558e6; border-color: #5558e6; }

/* Scrollable list */
.sidebar-scroll { 
  flex: 1; overflow-y: auto; min-height: 0; padding: 0 4px 8px; 
  scrollbar-width: none; -ms-overflow-style: none;
  animation: fadeIn 0.15s ease-out 0.05s both;
}
.sidebar-scroll::-webkit-scrollbar { display: none; }


/* Sections */
.sidebar-section { margin-bottom: 4px; }
.section-header {
  display: flex; align-items: center; gap: 4px; padding: 6px 8px;
  font-size: 11px; color: #999; cursor: pointer; user-select: none;
  border-radius: 6px; transition: all .2s ease; letter-spacing: .5px;
}
.section-header:hover { 
  background: rgba(0,0,0,.03); 
  color: #666;
  transform: translateX(4px);
}
.section-header .el-icon { font-size: 10px; transition: transform 0.2s ease; }
.section-header:hover .el-icon { transform: rotate(90deg); }
.section-header .el-tag { height: 16px; padding: 0 5px; font-size: 10px; border-radius: 8px; background: #f0f0f0; color: #999; border: none; }
.section-items { margin: 2px 0; }

.conv-item {
  display: flex; align-items: center; gap: 8px; padding: 7px 8px;
  cursor: pointer; border-radius: 8px; margin: 1px 4px;
  transition: all .2s ease;
  opacity: 0;
  animation: slideInLeft 0.2s ease-out forwards;
}
.conv-item:nth-child(1) { animation-delay: 0.01s; }
.conv-item:nth-child(2) { animation-delay: 0.02s; }
.conv-item:nth-child(3) { animation-delay: 0.03s; }
.conv-item:nth-child(4) { animation-delay: 0.04s; }
.conv-item:nth-child(5) { animation-delay: 0.05s; }
.conv-item:hover { 
  background: rgba(99,102,241,.05);
  transform: translateX(4px);
}
.conv-item.active { background: rgba(99,102,241,.08); }
.conv-icon { 
  font-size: 14px; color: #c0c4cc; flex-shrink: 0; 
  transition: all .2s ease;
}
.conv-item.active .conv-icon { color: #6366f1; }
.conv-item:hover .conv-icon { 
  color: #909399;
  transform: scale(1.1);
}
.conv-info { flex: 1; min-width: 0; }
.conv-title { 
  font-size: 12px; color: #444; overflow: hidden; 
  text-overflow: ellipsis; white-space: nowrap; line-height: 1.4;
  transition: color 0.2s ease;
}
.conv-item.active .conv-title { color: #6366f1; font-weight: 500; }
.conv-date { font-size: 10px; color: #bbb; margin-top: 1px; }
.conv-stage { margin-top: 2px; }
.stage-text { font-size: 10px; color: #aaa; }
.conv-more { 
  opacity: 0; flex-shrink: 0; color: #ccc;
  transition: all 0.2s ease;
}
.conv-more:hover { 
  color: #6366f1;
  transform: rotate(90deg);
}
.conv-item:hover .conv-more { opacity: 1; }
.empty-hint { 
  text-align: center; font-size: 11px; color: #ccc; padding: 20px 0;
  animation: fadeIn 0.3s ease-out;
}

/* Header actions */
.section-header { position: relative; }
.header-actions { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.action-link {
  font-size: 11px; color: #999; cursor: pointer; transition: all .2s ease;
  white-space: nowrap; user-select: none; padding: 4px 8px; border-radius: 6px;
}
.action-link:hover { 
  color: #6366f1; 
  background: rgba(99,102,241,.06);
}
.action-link.danger { color: #f56c6c; }
.action-link.danger:hover { 
  color: #e04848; 
  background: rgba(245,108,108,.06);
}
.action-link.disabled { opacity: .4; pointer-events: none; }
.action-divider { color: #ddd; font-size: 11px; user-select: none; }

/* Conv item checkbox */
.conv-check { margin-right: 4px; }
.conv-item.active .conv-check :deep(.el-checkbox__label) { color: #6366f1; }

/* Conv more button */
.conv-more { opacity: 0; flex-shrink: 0; color: #ccc; }
.conv-more:hover { color: #6366f1; }
.conv-item:hover .conv-more { opacity: 1; }

/* Mobile */
@media (max-width: 767px) {
  .sidebar { width: 100%; border-right: none; }
  .sidebar.collapsed { width: 100%; }
  .toggle-btn { display: none; }
  .conv-more { opacity: 1; }
}
</style>
