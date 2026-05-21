<template>
  <div>
    <h2>成绩与考试</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="成绩查询" name="grades">
        <el-table :data="grades" border>
          <el-table-column prop="semester" label="学期" width="120" />
          <el-table-column prop="course_name" label="课程" />
          <el-table-column prop="credit" label="学分" width="80" />
          <el-table-column prop="score" label="成绩" width="80" />
          <el-table-column prop="gpa" label="绩点" width="80" />
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="考试安排" name="exams">
        <el-table :data="exams" border>
          <el-table-column prop="course_name" label="课程" />
          <el-table-column prop="exam_date" label="日期" width="120" />
          <el-table-column prop="start_time" label="开始时间" width="100" />
          <el-table-column prop="end_time" label="结束时间" width="100" />
          <el-table-column prop="location" label="地点" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getGrades, getExams } from '@/api/academic'
import type { Grade, Exam } from '@/types'

const activeTab = ref('grades')
const grades = ref<Grade[]>([])
const exams = ref<Exam[]>([])

onMounted(async () => {
  grades.value = await getGrades() as any
  exams.value = await getExams() as any
})
</script>
