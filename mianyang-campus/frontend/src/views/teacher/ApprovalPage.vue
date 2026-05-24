<template>
  <div>
    <h2>审批管理</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="待批请假" name="leave">
        <el-table :data="pendingLeaves" v-if="pendingLeaves.length" border style="width:100%">
          <el-table-column prop="student_name" label="学生" width="100" />
          <el-table-column prop="leave_type" label="类型" width="80">
            <template #default="{ row }">{{ typeLabel(row.leave_type) }}</template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始" width="110" />
          <el-table-column prop="end_date" label="结束" width="110" />
          <el-table-column prop="reason" label="原因" min-width="200" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" size="small" @click="showReject(row)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无待批请假" />
      </el-tab-pane>
      <el-tab-pane label="办事申请" name="service">
        <el-table :data="pendingTickets" v-if="pendingTickets.length" border style="width:100%">
          <el-table-column prop="type" label="类型" width="80">
            <template #default="{ row }">{{ row.type === 'leave' ? '请假' : '证明' }}</template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="content" label="内容" min-width="200" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleTicketApprove(row.id)">通过</el-button>
              <el-button type="danger" size="small" @click="handleTicketReject(row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无待办申请" />
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
import { getPendingLeaves, reviewLeave as reviewLeaveApi } from '@/api/leave'
import { getTickets, approveTicket as approveTicketApi } from '@/api/service'
import type { LeaveRequestOut, ServiceTicket } from '@/types'

const activeTab = ref('leave')
const pendingLeaves = ref<LeaveRequestOut[]>([])
const pendingTickets = ref<ServiceTicket[]>([])
const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectTarget = ref<LeaveRequestOut | null>(null)

function typeLabel(t: string) {
  const map: Record<string, string> = { competition: '比赛', sick: '病假', personal: '事假', other: '其他' }
  return map[t] || t
}

async function loadData() {
  try { pendingLeaves.value = await getPendingLeaves() } catch {}
  try { pendingTickets.value = (await getTickets()).filter((t: ServiceTicket) => t.status === 'pending') } catch {}
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
