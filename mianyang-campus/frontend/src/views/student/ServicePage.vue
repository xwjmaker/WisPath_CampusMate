<template>
  <div>
    <h2>办事服务</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="我的申请" name="list">
        <el-button type="primary" style="margin-bottom:16px" @click="showApply = true">新建申请</el-button>
        <el-table :data="tickets" border>
          <el-table-column prop="type" label="类型" width="100">
            <template #default="{ row }">{{ row.type === 'leave' ? '请假' : '证明' }}</template>
          </el-table-column>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'">
                {{ row.status === 'approved' ? '已通过' : row.status === 'rejected' ? '已拒绝' : '待审批' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="提交时间" width="180" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="快捷申请" name="apply">
        <el-card v-for="item in quickActions" :key="item.type" style="margin-bottom:16px;cursor:pointer" @click="openApply(item.type)">
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showApply" title="新建申请" width="500px">
      <el-form :model="applyForm" label-width="80px">
        <el-form-item label="类型">
          <el-radio-group v-model="applyForm.type">
            <el-radio value="leave">请假申请</el-radio>
            <el-radio value="certificate">证明申请</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="applyForm.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input v-model="applyForm.content" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApply = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTickets, createTicket } from '@/api/service'
import type { ServiceTicket } from '@/types'

const activeTab = ref('list')
const tickets = ref<ServiceTicket[]>([])
const showApply = ref(false)
const applyForm = ref({ type: 'leave', title: '', content: '' })
const quickActions = [
  { type: 'leave', title: '请假申请', desc: '提交请假申请，等待辅导员审批' },
  { type: 'certificate', title: '证明申请', desc: '申请在校证明、成绩单等' },
]

onMounted(async () => { tickets.value = await getTickets() as any })

function openApply(type: string) { applyForm.value.type = type; showApply.value = true }

async function handleSubmit() {
  await createTicket(applyForm.value)
  ElMessage.success('提交成功')
  showApply.value = false
  tickets.value = await getTickets() as any
}
</script>
