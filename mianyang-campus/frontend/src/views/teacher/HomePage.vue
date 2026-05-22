<template>
  <div>
    <div class="dashboard-header">
      <h2>🚨 学生高危预警雷达</h2>
      <el-radio-group v-model="filterResolved" @change="loadAlerts">
        <el-radio-button :label="undefined">全部</el-radio-button>
        <el-radio-button :label="false">未处理</el-radio-button>
        <el-radio-button :label="true">已处理</el-radio-button>
      </el-radio-group>
    </div>

    <el-row :gutter="16">
      <el-col :span="6" v-for="s in studentAlerts" :key="s.student_id" style="margin-bottom:16px">
        <el-card
          :class="['student-card', `level-${s.level}`]"
          shadow="hover"
          @click="openDetail(s)"
        >
          <div class="card-header">
            <div class="status-dot" :class="`dot-${s.level}`"></div>
            <span class="student-name">{{ s.student_name }}</span>
          </div>
          <div class="level-badge">
            <el-tag :type="levelType(s.level)" size="small">
              {{ levelLabel(s.level) }}
            </el-tag>
            <el-tag v-if="!s.resolved" type="danger" size="small" effect="dark">未处理</el-tag>
          </div>
          <p class="summary-text">{{ s.summary.slice(0, 60) }}...</p>
          <div class="card-footer">
            <small>{{ formatTime(s.created_at) }}</small>
            <el-button text size="small" type="primary" @click.stop="openDetail(s)">详情</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-divider />

    <div class="section-header">
      <h3>📋 待审批请假</h3>
    </div>

    <el-table :data="pendingLeaves" v-if="pendingLeaves.length" style="width:100%">
      <el-table-column prop="student_name" label="学生" width="100" />
      <el-table-column prop="leave_type" label="类型" width="100">
        <template #default="{ row }">
          {{ typeLabel(row.leave_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="start_date" label="开始日期" width="120" />
      <el-table-column prop="end_date" label="结束日期" width="120" />
      <el-table-column prop="reason" label="原因" min-width="200" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="success" size="small" @click="approveLeave(row, 'approve')">通过</el-button>
          <el-button type="danger" size="small" @click="rejectDialog(row)">拒绝</el-button>
          <el-button text size="small" @click="genCareTemplate(row)">一键关怀</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无待审批请假" />

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" :title="detailStudent?.student_name || '详情'" width="600px">
      <template v-if="detailStudent">
        <el-alert
          v-if="detailStudent.level === 'severe'"
          title="高危预警"
          type="error"
          :description="detailStudent.summary"
          show-icon
          :closable="false"
          style="margin-bottom:16px"
        />
        <el-alert
          v-else-if="detailStudent.level === 'moderate'"
          title="中度预警"
          type="warning"
          :description="detailStudent.summary"
          show-icon
          :closable="false"
          style="margin-bottom:16px"
        />
        <el-alert
          v-else
          title="轻度关注"
          type="info"
          :description="detailStudent.summary"
          show-icon
          :closable="false"
          style="margin-bottom:16px"
        />
        <div class="detail-meta">
          <p><strong>匹配关键词：</strong>{{ detailStudent.keywords_matched || '无' }}</p>
          <p><strong>预警时间：</strong>{{ formatTime(detailStudent.created_at) }}</p>
        </div>
      </template>
      <template #footer>
        <el-button type="primary" @click="markResolved(detailStudent!)">
          {{ detailStudent?.resolved ? '标记为未处理' : '标记为已处理' }}
        </el-button>
        <el-button @click="genCareTemplate(detailStudent!)">生成关怀模板</el-button>
      </template>
    </el-dialog>

    <!-- Reject Dialog -->
    <el-dialog v-model="rejectVisible" title="拒绝理由" width="400px">
      <el-input v-model="rejectReason" type="textarea" :rows="3" placeholder="请输入拒绝理由" />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAlerts, resolveAlert } from '@/api/crisis'
import { getPendingLeaves, reviewLeave } from '@/api/leave'
import type { CrisisAlert, LeaveRequestOut } from '@/types'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const filterResolved = ref<boolean | undefined>(undefined)
const studentAlerts = ref<CrisisAlert[]>([])
const pendingLeaves = ref<LeaveRequestOut[]>([])
const detailVisible = ref(false)
const detailStudent = ref<CrisisAlert | null>(null)
const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref<LeaveRequestOut | null>(null)

function levelType(level: string) {
  const map: Record<string, string> = { severe: 'danger', moderate: 'warning', mild: 'info', normal: 'success' }
  return map[level] || 'info'
}

function levelLabel(level: string) {
  const map: Record<string, string> = { severe: '高危', moderate: '中度', mild: '轻度', normal: '正常' }
  return map[level] || '未知'
}

function typeLabel(t: string) {
  const map: Record<string, string> = { competition: '比赛', sick: '病假', personal: '事假', other: '其他' }
  return map[t] || t
}

function formatTime(t: string) {
  try { return new Date(t).toLocaleString('zh-CN') } catch { return t }
}

async function loadAlerts() {
  try {
    studentAlerts.value = await getAlerts(filterResolved.value)
  } catch { /* ignore */ }
}

async function loadLeaves() {
  try {
    pendingLeaves.value = await getPendingLeaves()
  } catch { /* ignore */ }
}

function openDetail(a: CrisisAlert) {
  detailStudent.value = a
  detailVisible.value = true
}

async function markResolved(a: CrisisAlert) {
  try {
    await resolveAlert(a.id, !a.resolved)
    a.resolved = !a.resolved
    ElMessage.success(a.resolved ? '已标记为已处理' : '已标记为未处理')
    loadAlerts()
  } catch { ElMessage.error('操作失败') }
}

function genCareTemplate(target: any) {
  const name = target.student_name || target.student_name || '该生'
  const templates = [
    `【一键关怀】${name}同学，最近注意到你可能遇到了一些困扰，学校的心理咨询中心随时为你提供支持。如果需要倾诉或帮助，欢迎来行政楼3楼找我聊聊。`,
    `【一键关怀】${name}你好，我是辅导员。最近学习生活还顺利吗？如果有任何困难或压力，记得随时联系我，我们一起想办法。`,
  ]
  const tpl = templates[Math.floor(Math.random() * templates.length)]
  navigator.clipboard.writeText(tpl).then(() => {
    ElMessage.success('关怀模板已复制到剪贴板')
  }).catch(() => {
    ElMessage.success(`关怀模板：${tpl}`)
  })
}

async function approveLeave(row: LeaveRequestOut, action: string) {
  try {
    await reviewLeave(row.id, action as any)
    ElMessage.success('已通过')
    loadLeaves()
  } catch { ElMessage.error('操作失败') }
}

function rejectDialog(row: LeaveRequestOut) {
  rejectTarget.value = row
  rejectReason.value = ''
  rejectVisible.value = true
}

async function confirmReject() {
  if (!rejectTarget.value) return
  try {
    await reviewLeave(rejectTarget.value.id, 'reject', rejectReason.value || undefined)
    ElMessage.success('已拒绝')
    rejectVisible.value = false
    loadLeaves()
  } catch { ElMessage.error('操作失败') }
}

onMounted(() => {
  loadAlerts()
  loadLeaves()
})
</script>

<style scoped>
.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.student-card { cursor: pointer; transition: transform .2s; }
.student-card:hover { transform: translateY(-2px); }
.card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.status-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.dot-severe { background: #f56c6c; box-shadow: 0 0 6px #f56c6c; }
.dot-moderate { background: #e6a23c; box-shadow: 0 0 6px #e6a23c; }
.dot-mild { background: #909399; }
.dot-normal { background: #67c23a; }
.level-severe { border-left: 3px solid #f56c6c; }
.level-moderate { border-left: 3px solid #e6a23c; }
.level-mild { border-left: 3px solid #909399; }
.level-normal { border-left: 3px solid #67c23a; }
.student-name { font-weight: bold; font-size: 15px; }
.level-badge { margin-bottom: 8px; display: flex; gap: 4px; }
.summary-text { color: #666; font-size: 13px; line-height: 1.4; margin-bottom: 8px; }
.card-footer { display: flex; justify-content: space-between; align-items: center; }
.section-header { margin-bottom: 12px; }
.detail-meta p { margin: 4px 0; font-size: 14px; }
</style>
