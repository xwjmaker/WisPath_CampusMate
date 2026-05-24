<template>
  <div>
    <h2>审批管理</h2>
    <el-tabs v-model="activeTab" @tab-change="loadData">
      <el-tab-pane label="待审批" name="pending">
        <h4 style="margin:12px 0 8px">请假申请</h4>
        <el-table :data="pendingLeaves" v-if="pendingLeaves.length" border style="width:100%">
          <el-table-column prop="student_name" label="学生" width="90" />
          <el-table-column prop="leave_type" label="类型" width="70">
            <template #default="{ row }">{{ typeLabel(row.leave_type) }}</template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始" width="100" />
          <el-table-column prop="end_date" label="结束" width="100" />
          <el-table-column prop="reason" label="原因" min-width="160" />
          <el-table-column label="AI 分析" width="180">
            <template #default="{ row }">
              <div v-if="analysisMap[row.id]" class="ai-analyze">
                <el-tag :type="analysisMap[row.id].suggestion === 'approve' ? 'success' : 'danger'" size="small" effect="plain">
                  {{ analysisMap[row.id].suggestion === 'approve' ? '建议通过' : '建议拒绝' }}
                </el-tag>
                <el-tooltip :content="analysisMap[row.id].reason" placement="top">
                  <el-icon style="cursor:pointer;color:#909399;margin-left:4px"><InfoFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-tag v-else type="info" size="small" effect="plain">分析中...</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="170" fixed="right">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" size="small" @click="showReject(row)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无待批请假" />

        <h4 style="margin:20px 0 8px">办事申请</h4>
        <el-table :data="pendingTickets" v-if="pendingTickets.length" border style="width:100%">
          <el-table-column prop="type" label="类型" width="70">
            <template #default="{ row }">{{ row.type === 'leave' ? '请假' : '证明' }}</template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="180" />
          <el-table-column prop="content" label="内容" min-width="180" />
          <el-table-column label="操作" width="170">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleTicketApprove(row.id)">通过</el-button>
              <el-button type="danger" size="small" @click="handleTicketReject(row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无待办申请" />
      </el-tab-pane>

      <el-tab-pane label="已通过" name="approved">
        <h4 style="margin:12px 0 8px">已通过请假</h4>
        <el-table :data="approvedLeaves" v-if="approvedLeaves.length" border style="width:100%">
          <el-table-column prop="student_name" label="学生" width="90" />
          <el-table-column prop="leave_type" label="类型" width="70">
            <template #default="{ row }">{{ typeLabel(row.leave_type) }}</template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始" width="100" />
          <el-table-column prop="end_date" label="结束" width="100" />
          <el-table-column prop="reason" label="原因" min-width="160" />
          <el-table-column label="状态" width="80">
            <template #default>
              <el-tag type="success" size="small">已通过</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无已通过请假" />
      </el-tab-pane>

      <el-tab-pane label="已拒绝" name="rejected">
        <h4 style="margin:12px 0 8px">已拒绝请假</h4>
        <el-table :data="rejectedLeaves" v-if="rejectedLeaves.length" border style="width:100%">
          <el-table-column prop="student_name" label="学生" width="90" />
          <el-table-column prop="leave_type" label="类型" width="70">
            <template #default="{ row }">{{ typeLabel(row.leave_type) }}</template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始" width="100" />
          <el-table-column prop="end_date" label="结束" width="100" />
          <el-table-column prop="reason" label="原因" min-width="140" />
          <el-table-column prop="reject_reason" label="拒绝理由" min-width="140" />
          <el-table-column label="状态" width="80">
            <template #default>
              <el-tag type="danger" size="small">已拒绝</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无已拒绝请假" />
      </el-tab-pane>
    </el-tabs>

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
import { InfoFilled } from '@element-plus/icons-vue'
import { getPendingLeaves, reviewLeave as reviewLeaveApi, getAllLeaves, analyzeLeave } from '@/api/leave'
import { getTickets, approveTicket as approveTicketApi } from '@/api/service'
import type { LeaveRequestOut, ServiceTicket } from '@/types'

const activeTab = ref('pending')
const pendingLeaves = ref<LeaveRequestOut[]>([])
const pendingTickets = ref<ServiceTicket[]>([])
const approvedLeaves = ref<LeaveRequestOut[]>([])
const rejectedLeaves = ref<LeaveRequestOut[]>([])
const analysisMap = ref<Record<number, { suggestion: string; reason: string }>>({})
const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref<LeaveRequestOut | null>(null)

function typeLabel(t: string) {
  const map: Record<string, string> = { competition: '比赛', sick: '病假', personal: '事假', other: '其他' }
  return map[t] || t
}

async function loadData() {
  if (activeTab.value === 'pending') {
    try {
      pendingLeaves.value = await getPendingLeaves()
      loadAnalysis()
    } catch {}
    try { pendingTickets.value = (await getTickets()).filter((t: ServiceTicket) => t.status === 'pending') } catch {}
  } else if (activeTab.value === 'approved') {
    try { approvedLeaves.value = await getAllLeaves('approved') } catch {}
  } else if (activeTab.value === 'rejected') {
    try { rejectedLeaves.value = await getAllLeaves('rejected') } catch {}
  }
}

async function loadAnalysis() {
  for (const leave of pendingLeaves.value) {
    if (!analysisMap.value[leave.id]) {
      analysisMap.value[leave.id] = { suggestion: 'approve', reason: '分析中...' }
      try {
        const result = await analyzeLeave(leave.id)
        analysisMap.value[leave.id] = result
      } catch {
        analysisMap.value[leave.id] = { suggestion: 'approve', reason: 'AI分析暂时不可用' }
      }
    }
  }
}

async function handleApprove(row: LeaveRequestOut) {
  try {
    await reviewLeaveApi(row.id, 'approve')
    ElMessage.success('已通过')
    loadData()
  } catch { ElMessage.error('操作失败') }
}

function showReject(row: LeaveRequestOut) {
  rejectTarget.value = row
  rejectReason.value = ''
  rejectVisible.value = true
}

async function confirmReject() {
  if (!rejectTarget.value) return
  try {
    await reviewLeaveApi(rejectTarget.value.id, 'reject', rejectReason.value || undefined)
    ElMessage.success('已拒绝')
    rejectVisible.value = false
    loadData()
  } catch { ElMessage.error('操作失败') }
}

async function handleTicketApprove(id: number) {
  try {
    await approveTicketApi(id, 'approve')
    ElMessage.success('已通过')
    loadData()
  } catch { ElMessage.error('操作失败') }
}

async function handleTicketReject(id: number) {
  try {
    await approveTicketApi(id, 'reject')
    ElMessage.success('已拒绝')
    loadData()
  } catch { ElMessage.error('操作失败') }
}

onMounted(loadData)
</script>
