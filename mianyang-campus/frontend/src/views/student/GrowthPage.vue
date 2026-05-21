<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center">
      <h2>我的成长轨迹</h2>
      <el-button type="primary" @click="dialogVisible = true">添加记录</el-button>
    </div>
    <div class="timeline" v-if="records.length">
      <MilestoneCard v-for="r in records" :key="r.id" :record="r" />
    </div>
    <el-empty v-else description="暂无成长记录" />

    <el-dialog v-model="dialogVisible" title="添加成长记录" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="类型">
          <el-select v-model="form.type">
            <el-option label="荣誉" value="honor" />
            <el-option label="竞赛" value="competition" />
            <el-option label="获奖" value="award" />
            <el-option label="实践" value="practice" />
          </el-select>
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="证明材料">
          <el-upload :auto-upload="false"><el-button>上传文件</el-button></el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getGrowthRecords, createGrowthRecord } from '@/api/growth'
import type { GrowthRecord } from '@/types'
import MilestoneCard from '@/components/growth/MilestoneCard.vue'

const records = ref<GrowthRecord[]>([])
const dialogVisible = ref(false)
const form = ref({ type: 'honor', title: '', description: '', date: '' })

onMounted(async () => { records.value = await getGrowthRecords() as any })

async function handleAdd() {
  await createGrowthRecord(form.value as any)
  ElMessage.success('添加成功')
  dialogVisible.value = false
  records.value = await getGrowthRecords() as any
}
</script>

<style scoped>
.timeline { margin-top: 20px; }
</style>
