<template>
  <div>
    <h2>课表查询</h2>
    <el-table :data="schedule" border>
      <el-table-column label="时间" width="120">
        <template #default="{ $index }">
          {{ periods[$index] }}
        </template>
      </el-table-column>
      <el-table-column v-for="day in days" :key="day" :label="day">
        <template #default="{ row }">
          <div v-for="c in getCourses(day, row.period)" :key="c.id" class="course-cell">
            <strong>{{ c.name }}</strong>
            <p>{{ c.teacher }}</p>
            <p>{{ c.location }}</p>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCourses as fetchCourses } from '@/api/academic'
import type { Course } from '@/types'

const days = ['周一', '周二', '周三', '周四', '周五']
const periods = ['第1节\n08:00-08:45', '第2节\n08:55-09:40', '第3节\n10:00-10:45', '第4节\n10:55-11:40', '第5节\n14:00-14:45', '第6节\n14:55-15:40']
const courses = ref<Course[]>([])
const schedule = ref(periods.map((label, i) => ({ label, period: i + 1 })))

onMounted(async () => { courses.value = await fetchCourses() as any })

function getCourses(day: string, period: number) {
  const dayMap: Record<string, number> = { '周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5 }
  return courses.value.filter(c => c.day_of_week === dayMap[day] && c.start_period <= period && c.end_period >= period)
}
</script>

<style scoped>
.course-cell { background: #ecf5ff; border-radius: 4px; padding: 4px; margin: 2px; font-size: 13px; }
.course-cell p { margin: 0; color: #666; }
</style>
