<template>
  <div>
    <h2>审批管理</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="待审批" name="pending">
        <el-table :data="pendingTickets" border>
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">{{ row.type === 'leave' ? '请假' : '证明' }}</template>
          </el-table-column>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="content" label="内容" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="handleApprove(row.id)">通过</el-button>
              <el-button type="danger" size="small" @click="handleReject(row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="已处理" name="done">
        <el-table :data="doneTickets" border>
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="status" label="结果" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'approved' ? 'success' : 'danger'">
                {{ row.status === 'approved' ? '已通过' : '已拒绝' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTickets, approveTicket } from '@/api/service'
import type { ServiceTicket } from '@/types'

const activeTab = ref('pending')
const allTickets = ref<ServiceTicket[]>([])
const pendingTickets = computed(() => allTickets.value.filter(t => t.status === 'pending'))
const doneTickets = computed(() => allTickets.value.filter(t => t.status !== 'pending'))

onMounted(async () => { allTickets.value = await getTickets() as any })

async function handleApprove(id: number) {
  await approveTicket(id, 'approve')
  ElMessage.success('已通过')
  allTickets.value = await getTickets() as any
}
async function handleReject(id: number) {
  await approveTicket(id, 'reject')
  ElMessage.success('已拒绝')
  allTickets.value = await getTickets() as any
}
</script>
