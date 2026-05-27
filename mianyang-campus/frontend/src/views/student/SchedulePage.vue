<template>
  <div class="schedule-page">
    <div class="page-tabs">
      <div :class="['tab-item', { active: activeTab === 'schedule' }]" @click="activeTab = 'schedule'">课程表</div>
      <div :class="['tab-item', { active: activeTab === 'grades' }]" @click="activeTab = 'grades'">考试成绩</div>
    </div>

    <!-- ===== 课程表 ===== -->
    <template v-if="activeTab === 'schedule'">
      <div class="schedule-toolbar">
        <div class="week-info">
          <el-button size="small" circle @click="goPrevWeek" :disabled="currentWeek <= 1">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <span class="week-label">第{{ currentWeek }}周</span>
          <el-button size="small" circle @click="goNextWeek">
            <el-icon><ArrowRight /></el-icon>
          </el-button>
          <el-button size="small" text type="primary" @click="resetWeek" style="margin-left:4px">回到本周</el-button>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <el-tag v-if="todayCourses.length" type="success" effect="light" size="small">
            今日 {{ todayCourses.length }} 节课
          </el-tag>
          <el-tag type="info" effect="plain" size="small">{{ currentWeekCourses.length }} 门课程</el-tag>
        </div>
      </div>

      <div class="schedule-grid">
        <div class="sg-header">
          <div class="sg-corner">节次</div>
          <div v-for="d in days" :key="d" class="sg-day">{{ d }}</div>
        </div>
        <div v-for="row in courseGrid" :key="row.period" class="sg-row">
          <div class="sg-period" v-html="periodLabels[row.period - 1]"></div>
          <div v-for="cell in row.cells" :key="cell.day" class="sg-cell">
            <div v-for="c in cell.courses" :key="c.id" class="sg-course"
              :style="{ background: courseColor(c.name) }">
              <div class="sgc-name">{{ c.name }}</div>
              <div class="sgc-meta">{{ c.location }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="todayCourses.length" class="today-section">
        <div class="today-header"><el-icon><Sunny /></el-icon> {{ isCurrentRealWeek ? '今日' : todayLabel }}课程</div>
        <div class="today-list">
          <div v-for="c in todayCourses" :key="c.id" class="today-card"
            :style="{ borderLeftColor: courseColor(c.name).slice(0, 7) }">
            <div class="tc-time">第{{ c.start_period }}-{{ c.end_period }}节</div>
            <div class="tc-body">
              <div class="tc-name">{{ c.name }}</div>
              <div class="tc-meta">{{ c.teacher }} · {{ c.location }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="course-list-section">
        <div class="cl-header">全部课程（第{{ currentWeek }}周）</div>
        <div class="course-list">
          <div v-for="c in currentWeekCourses" :key="c.id" class="cl-card" :style="{ borderLeftColor: courseColor(c.name).slice(0, 7) }">
            <div class="cl-top">
              <span class="cl-name">{{ c.name }}</span>
              <span class="cl-teacher">{{ c.teacher }}</span>
            </div>
            <div class="cl-meta">
              <span>{{ c.location }}</span>
              <span>第{{ c.week_start }}-{{ c.week_end }}周</span>
              <span>{{ dayLabel(c.day_of_week) }} 第{{ c.start_period }}-{{ c.end_period }}节</span>
            </div>
          </div>
          <el-empty v-if="!currentWeekCourses.length" description="本周无课" :image-size="48" />
        </div>
      </div>
    </template>

    <!-- ===== 考试成绩 ===== -->
    <template v-if="activeTab === 'grades'">
      <!-- GPA 趋势 -->
      <div class="trend-section">
        <div class="section-title"><el-icon><TrendCharts /></el-icon> 学期绩点趋势</div>
        <v-chart v-if="trendOption" :option="trendOption" class="trend-chart" autoresize />
        <el-empty v-else description="暂无成绩数据" :image-size="48" />
      </div>

      <!-- 目标计划 -->
      <div class="goal-section">
        <div class="section-title"><el-icon><Aim /></el-icon> 目标计划</div>
        <div class="goal-list">
          <div v-for="(sem, idx) in semesters" :key="sem" class="goal-item" :class="{ 'is-current': idx === 0 }">
            <div class="goal-item-header">
              <span class="goal-sem-name">{{ sem }}</span>
              <el-tag v-if="idx === 0" type="success" size="small" effect="light">当前学期</el-tag>
              <el-tag v-else type="info" size="small" effect="plain">已完成</el-tag>
            </div>
            <div class="goal-item-body">
              <div class="goal-item-left">
                <span class="goal-label">目标绩点</span>
                <template v-if="idx === 0">
                  <div class="goal-input-wrap">
                    <el-input-number v-model="goalInputs[sem]" :min="0" :max="4" :step="0.1" :precision="2"
                      size="small" controls-position="right" style="width:110px" />
                    <el-button type="primary" size="small" @click="saveGoalForSem(sem)" style="margin-left:6px">保存</el-button>
                  </div>
                </template>
                <template v-else>
                  <div class="goal-locked">
                    <el-icon><Lock /></el-icon>
                    <span>{{ goals[sem] != null ? goals[sem].toFixed(2) : '未设置' }}</span>
                  </div>
                </template>
              </div>
              <div class="goal-item-right">
                <span>实际 <b :style="{ color: avgColor(semStats[sem]?.avg) }">{{ semStats[sem]?.gpa || '--' }}</b></span>
                <span v-if="goals[sem] != null" class="goal-achieve">
                  <template v-if="parseFloat(semStats[sem]?.gpa || '0') >= goals[sem]">
                    <el-icon color="#67c23a"><CircleCheckFilled /></el-icon> 已达成
                  </template>
                  <template v-else>
                    <el-icon color="#f56c6c"><WarningFilled /></el-icon> 差 {{ (goals[sem] - parseFloat(semStats[sem]?.gpa || '0')).toFixed(2) }}
                  </template>
                </span>
              </div>
            </div>
            <div v-if="goals[sem] != null" class="goal-item-bar">
              <div class="goal-bar-outer">
                <div class="goal-bar-inner" :style="{
                  width: Math.min(100, (parseFloat(semStats[sem]?.gpa || '0') / goals[sem]) * 100) + '%',
                  background: parseFloat(semStats[sem]?.gpa || '0') >= goals[sem] ? '#67c23a' : '#409eff'
                }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 学期选择 -->
      <div class="sem-selector">
        <el-select v-model="selectedSem" placeholder="选择学期" style="width:200px">
          <el-option v-for="s in semesters" :key="s" :label="s" :value="s" />
        </el-select>
        <div v-if="selectedSem" class="sem-stats-inline">
          <span>{{ semStats[selectedSem]?.count }} 门</span>
          <span>均分 <b :style="{ color: avgColor(semStats[selectedSem]?.avg) }">{{ semStats[selectedSem]?.avg }}</b></span>
          <span>均绩 <b>{{ semStats[selectedSem]?.gpa }}</b></span>
          <span>学分 <b>{{ semStats[selectedSem]?.credits }}</b></span>
        </div>
      </div>

      <!-- 该学期成绩 -->
      <div v-if="selectedSem" class="selected-sem-grades">
        <div class="grade-grid">
          <div v-for="g in gradesBySem[selectedSem]" :key="g.id" class="grade-card" :class="scoreLevel(g.score)">
            <div class="gc-top">
              <span class="gc-name">{{ g.course_name }}</span>
              <span class="gc-score">{{ g.score }}</span>
            </div>
            <div class="gc-meta">
              <span>绩点 {{ g.gpa }}</span>
              <span>学分 {{ g.credit }}</span>
            </div>
          </div>
        </div>
        <el-empty v-if="!gradesBySem[selectedSem]?.length" description="该学期暂无成绩" :image-size="48" />
      </div>

      <!-- 即将考试 -->
      <div v-if="upcomingExams.length" class="exam-section">
        <div class="section-title"><el-icon><WarningFilled /></el-icon> 即将考试</div>
        <div v-for="e in upcomingExams" :key="e.id" class="exam-card">
          <div class="ec-left">
            <div class="ec-date">{{ formatDate(e.exam_date) }}</div>
            <div class="ec-time">{{ e.start_time?.slice(0, 5) }} - {{ e.end_time?.slice(0, 5) }}</div>
          </div>
          <div class="ec-body">
            <div class="ec-name">{{ e.course_name }}</div>
            <div class="ec-location"><el-icon><Location /></el-icon> {{ e.location }}</div>
          </div>
        </div>
      </div>

      <el-empty v-if="!grades.length && !upcomingExams.length" description="暂无考试成绩数据" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { getCourses as fetchCourses, getGrades, getExams } from '@/api/academic'
import { ArrowLeft, ArrowRight, Sunny, WarningFilled, Location, TrendCharts, Aim, CircleCheckFilled, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, MarkLineComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { Course, Grade, Exam } from '@/types'

use([LineChart, GridComponent, TooltipComponent, MarkLineComponent, CanvasRenderer])

const activeTab = ref('schedule')

// ===== 课程表 =====
const days = ['周一', '周二', '周三', '周四', '周五']
const periodLabels = ['第1节<br>08:00', '第2节<br>08:55', '第3节<br>10:00', '第4节<br>10:55', '第5节<br>14:00', '第6节<br>14:55']
const courses = ref<Course[]>([])

const weekOffset = ref(0)
const baseWeek = ref(1)

const currentWeek = computed(() => Math.max(1, baseWeek.value + weekOffset.value))

const currentWeekCourses = computed(() => {
  const wk = currentWeek.value
  return courses.value.filter(c => wk >= c.week_start && wk <= c.week_end)
})

const maxPeriod = computed(() => {
  const wk = currentWeek.value
  const wkCourses = courses.value.filter(c => wk >= c.week_start && wk <= c.week_end)
  return Math.max(...wkCourses.map(c => c.end_period), 6)
})

const dayMap: Record<string, number> = { '周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5 }

const courseGrid = computed(() => {
  const wk = currentWeek.value
  const rows = []
  for (let p = 1; p <= maxPeriod.value; p++) {
    const cells = days.map(day => ({
      day,
      courses: courses.value.filter(c =>
        c.day_of_week === dayMap[day] &&
        c.start_period === p &&
        wk >= c.week_start && wk <= c.week_end
      )
    }))
    rows.push({ period: p, cells })
  }
  return rows
})

const todayLabel = computed(() => {
  const d = new Date().getDay()
  return ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'][d] || ''
})

const todayCourses = computed(() => {
  const day = todayLabel.value
  if (!day) return []
  const wk = currentWeek.value
  return courses.value.filter(c =>
    c.day_of_week === dayMap[day] &&
    wk >= c.week_start && wk <= c.week_end
  ).sort((a, b) => a.start_period - b.start_period)
})

function calcCurrentRealWeek() {
  const now = new Date()
  const year = now.getFullYear()
  let semesterStart: Date
  if (now.getMonth() >= 8) {
    semesterStart = new Date(year, 8, 1)
  } else if (now.getMonth() >= 1) {
    semesterStart = new Date(year, 1, 24)
  } else {
    semesterStart = new Date(year - 1, 8, 1)
  }
  const diff = (now.getTime() - semesterStart.getTime()) / (7 * 24 * 60 * 60 * 1000)
  return Math.max(1, Math.floor(diff) + 1)
}

const isCurrentRealWeek = computed(() => currentWeek.value === calcCurrentRealWeek())

const palette = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#9b59b6', '#1abc9c', '#e67e22', '#2ecc71', '#3498db', '#e74c3c']
const colorMap: Record<string, string> = {}
let colorIdx = 0
function courseColor(name: string) {
  if (!colorMap[name]) {
    colorMap[name] = palette[colorIdx % palette.length] + '18'
    colorIdx++
  }
  return colorMap[name]
}

function dayLabel(d: number) {
  return ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'][d] || ''
}

function goPrevWeek() { if (currentWeek.value > 1) weekOffset.value-- }
function goNextWeek() { weekOffset.value++ }
function resetWeek() {
  if (courses.value.length) {
    baseWeek.value = Math.min(...courses.value.map(c => c.week_start))
    const realWeek = calcCurrentRealWeek()
    weekOffset.value = realWeek - baseWeek.value
  }
}

// ===== 考试成绩 =====
const grades = ref<Grade[]>([])
const exams = ref<Exam[]>([])
const selectedSem = ref('')
const goals = ref<Record<string, number>>({})
const goalInputs = ref<Record<string, number>>({})

const semesters = computed(() => [...new Set(grades.value.map(g => g.semester))].sort().reverse())

const gradesBySem = computed(() => {
  const map: Record<string, Grade[]> = {}
  for (const g of grades.value) {
    if (!map[g.semester]) map[g.semester] = []
    map[g.semester].push(g)
  }
  return map
})

const semStats = computed(() => {
  const stats: Record<string, { count: number; avg: number; gpa: string; credits: number }> = {}
  for (const [sem, gs] of Object.entries(gradesBySem.value)) {
    const scores = gs.filter(g => g.score != null).map(g => g.score)
    const avg = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0
    const gpa = gs.length ? (gs.reduce((s, g) => s + (g.gpa || 0), 0) / gs.length).toFixed(2) : '0.00'
    const credits = gs.reduce((s, g) => s + (g.credit || 0), 0)
    stats[sem] = { count: gs.length, avg, gpa, credits }
  }
  return stats
})

const trendOption = computed(() => {
  const sems = [...semesters.value].reverse()
  if (!sems.length) return null
  const gpaData = sems.map(s => parseFloat(semStats.value[s]?.gpa || '0'))
  const semLabels = sems.map(s => {
    const parts = s.split('-')
    return parts.length >= 3 ? parts.slice(0, 2).join('-') + (parts[2] === '1' ? '上' : '下') : s
  })
  return {
    tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].axisValue}<br/>绩点: ${p[0].value}` },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: semLabels, axisLabel: { color: '#666', fontSize: 12 } },
    yAxis: { type: 'value', min: 0, max: 4, axisLabel: { color: '#666' }, splitLine: { lineStyle: { color: '#f0f0f0' } } },
    series: [{
      type: 'line', data: gpaData, smooth: true,
      symbol: 'circle', symbolSize: 8,
      lineStyle: { color: '#409eff', width: 3 },
      itemStyle: { color: '#409eff' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#409eff40' }, { offset: 1, color: '#409eff05' }] } },
      markLine: { data: [{ yAxis: goals.value[semesters.value[0]] ?? 3.5, label: { formatter: '目标 ' + (goals.value[semesters.value[0]] ?? 3.5), color: '#e6a23c' } }], silent: true, lineStyle: { type: 'dashed', color: '#e6a23c' } },
    }],
  }
})

const upcomingExams = computed(() => {
  const now = new Date()
  return exams.value.filter(e => !e.exam_date || new Date(e.exam_date) >= now)
    .sort((a, b) => (a.exam_date || '').localeCompare(b.exam_date || ''))
})

function scoreLevel(s: number) {
  if (s >= 90) return 'level-a'
  if (s >= 80) return 'level-b'
  if (s >= 70) return 'level-c'
  if (s >= 60) return 'level-d'
  return 'level-f'
}

function avgColor(s?: number) {
  if (!s) return '#999'
  if (s >= 90) return '#67c23a'
  if (s >= 80) return '#409eff'
  if (s >= 70) return '#e6a23c'
  return '#f56c6c'
}

function formatDate(d: string) {
  if (!d) return ''
  const parts = d.split('-')
  return parts[1] + '/' + parts[2]
}

function loadGoals() {
  try {
    const raw = localStorage.getItem('student_sem_goals')
    if (raw) goals.value = JSON.parse(raw)
  } catch { goals.value = {} }
}

function saveGoalForSem(sem: string) {
  const val = goalInputs.value[sem]
  if (val == null) return
  goals.value[sem] = val
  localStorage.setItem('student_sem_goals', JSON.stringify(goals.value))
  ElMessage.success(`${sem} 目标已保存`)
}

onMounted(async () => {
  loadGoals()

  const coursePromise = fetchCourses().then(d => { courses.value = d as any }).catch(() => {})
  const gradesPromise = getGrades().then(d => { grades.value = d as any }).catch(() => {})
  const examsPromise = getExams().then(d => { exams.value = d as any }).catch(() => {})
  await Promise.all([coursePromise, gradesPromise, examsPromise])
  if (courses.value.length) {
    baseWeek.value = Math.min(...courses.value.map(c => c.week_start))
    const realWeek = calcCurrentRealWeek()
    weekOffset.value = realWeek - baseWeek.value
  }
  if (semesters.value.length) selectedSem.value = semesters.value[0]
  for (const sem of semesters.value) {
    if (goalInputs.value[sem] == null) {
      goalInputs.value[sem] = goals.value[sem] ?? 3.5
    }
  }
})

watch(semesters, (list) => {
  if (list.length && !list.includes(selectedSem.value)) {
    selectedSem.value = list[0]
  }
  for (const sem of list) {
    if (goalInputs.value[sem] == null) {
      goalInputs.value[sem] = goals.value[sem] ?? 3.5
    }
  }
})
</script>

<style scoped>
.schedule-page { max-width: 1100px; margin: 0 auto; padding: 12px 0 32px; }

/* ===== Page Tabs ===== */
.page-tabs { display: flex; gap: 4px; margin-bottom: 20px; background: #f5f7fa; border-radius: 10px; padding: 4px; }
.tab-item {
  flex: 1; text-align: center; padding: 8px 0; font-size: 14px; font-weight: 600;
  border-radius: 8px; cursor: pointer; transition: all .2s; color: #666;
}
.tab-item:hover { color: #333; }
.tab-item.active { background: #fff; color: #409eff; box-shadow: 0 1px 4px rgba(0,0,0,.08); }

/* ===== Toolbar ===== */
.schedule-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; padding: 0 4px; flex-wrap: wrap; gap: 10px;
}
.week-info { display: flex; align-items: center; gap: 10px; }
.week-label { font-size: 18px; font-weight: 700; color: #1a1a2e; min-width: 80px; text-align: center; letter-spacing: 1px; }

/* ===== Grid ===== */
.schedule-grid {
  display: flex; flex-direction: column; border-radius: 14px;
  border: 1px solid rgba(0,0,0,.06); overflow: hidden; background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,.04); margin-bottom: 28px;
}
.sg-header { display: flex; background: #f5f7fa; border-bottom: 1px solid #e8e8e8; }
.sg-corner { width: 76px; flex-shrink: 0; padding: 12px 4px; text-align: center; font-weight: 700; font-size: 13px; color: #666; }
.sg-day { flex: 1; padding: 12px 4px; text-align: center; font-weight: 700; font-size: 14px; color: #555; border-left: 1px solid #e8e8e8; letter-spacing: 2px; }
.sg-row { display: flex; border-bottom: 1px solid #f0f0f0; }
.sg-row:last-child { border-bottom: none; }
.sg-period {
  width: 76px; flex-shrink: 0; padding: 10px 4px; text-align: center;
  font-size: 12px; color: #888; background: #fafafa; display: flex;
  flex-direction: column; align-items: center; justify-content: center; line-height: 1.5; font-weight: 500;
}
.sg-cell { flex: 1; min-height: 80px; padding: 4px; border-left: 1px solid #f0f0f0; }
.sg-course {
  border-radius: 8px; padding: 6px 8px; margin-bottom: 3px;
  transition: transform .12s; cursor: default;
}
.sg-course:hover { transform: scale(1.04); }
.sgc-name { font-size: 13px; font-weight: 700; color: #1a1a2e; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sgc-meta { font-size: 11px; color: #666; margin-top: 1px; }

/* ===== Today Section ===== */
.today-section { margin-bottom: 28px; }
.today-header {
  font-size: 16px; font-weight: 700; color: #1a1a2e;
  padding-bottom: 14px; margin-bottom: 14px; border-bottom: 2px solid #67c23a;
  display: flex; align-items: center; gap: 6px;
}
.today-list { display: flex; flex-direction: column; gap: 10px; }
.today-card {
  display: flex; gap: 16px; align-items: center;
  background: #fff; border-radius: 12px; padding: 14px 18px;
  border: 1px solid rgba(0,0,0,.04); border-left: 5px solid #67c23a;
  box-shadow: 0 2px 8px rgba(0,0,0,.03); transition: transform .15s;
}
.today-card:hover { transform: translateY(-2px); }
.tc-time { font-size: 14px; font-weight: 700; color: #409eff; flex-shrink: 0; min-width: 76px; }
.tc-body { flex: 1; }
.tc-name { font-size: 15px; font-weight: 600; color: #1a1a2e; }
.tc-meta { font-size: 13px; color: #888; margin-top: 3px; }

/* ===== Course List ===== */
.course-list-section { }
.cl-header {
  font-size: 16px; font-weight: 700; color: #1a1a2e;
  padding-bottom: 14px; margin-bottom: 14px; border-bottom: 2px solid #409eff;
}
.course-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }
.cl-card {
  background: #fff; border-radius: 12px; padding: 16px 18px;
  border: 1px solid rgba(0,0,0,.04); border-left: 5px solid #409eff;
  box-shadow: 0 2px 8px rgba(0,0,0,.03); transition: transform .15s;
}
.cl-card:hover { transform: translateY(-2px); }
.cl-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.cl-name { font-size: 15px; font-weight: 600; color: #1a1a2e; }
.cl-teacher { font-size: 13px; color: #888; }
.cl-meta { display: flex; flex-wrap: wrap; gap: 10px; font-size: 13px; color: #999; }

/* ===== Trend Section ===== */
.trend-section { margin-bottom: 24px; }
.section-title {
  font-size: 16px; font-weight: 700; color: #1a1a2e;
  padding-bottom: 14px; margin-bottom: 14px; border-bottom: 2px solid #409eff;
  display: flex; align-items: center; gap: 6px;
}
.trend-chart { width: 100%; height: 240px; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.03); }

/* ===== Goal Section ===== */
.goal-section { margin-bottom: 24px; }
.section-title {
  font-size: 16px; font-weight: 700; color: #1a1a2e;
  padding-bottom: 14px; margin-bottom: 14px; border-bottom: 2px solid #409eff;
  display: flex; align-items: center; gap: 6px;
}
.goal-list { display: flex; flex-direction: column; gap: 10px; }
.goal-item {
  background: #fff; border-radius: 12px; padding: 16px 20px;
  border: 1px solid rgba(0,0,0,.04); box-shadow: 0 2px 8px rgba(0,0,0,.03);
  transition: transform .15s;
}
.goal-item:hover { transform: translateY(-1px); }
.goal-item.is-current { border-left: 4px solid #67c23a; }
.goal-item-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
}
.goal-sem-name { font-size: 14px; font-weight: 700; color: #1a1a2e; }
.goal-item-body { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.goal-item-left { display: flex; align-items: center; gap: 10px; }
.goal-item-right { display: flex; align-items: center; gap: 12px; font-size: 13px; color: #666; }
.goal-label { font-size: 13px; font-weight: 600; color: #333; white-space: nowrap; }
.goal-input-wrap { display: flex; align-items: center; }
.goal-locked {
  display: flex; align-items: center; gap: 4px;
  font-size: 13px; color: #999;
}
.goal-achieve { display: flex; align-items: center; gap: 3px; font-size: 13px; }
.goal-item-bar { margin-top: 10px; }
.goal-bar-outer {
  height: 8px; background: #f0f2f5; border-radius: 4px; overflow: hidden;
}
.goal-bar-inner { height: 100%; border-radius: 4px; transition: width .6s ease; }

/* ===== Semester Selector ===== */
.sem-selector {
  display: flex; align-items: center; gap: 16px; margin-bottom: 16px;
}
.sem-stats-inline { display: flex; gap: 14px; font-size: 13px; color: #999; }
.sem-stats-inline b { color: #1a1a2e; font-weight: 600; }

/* ===== Grade Grid ===== */
.grade-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 10px; margin-bottom: 20px; }
.grade-card {
  background: #fff; border-radius: 10px; padding: 14px 16px;
  border: 1px solid rgba(0,0,0,.04); box-shadow: 0 1px 6px rgba(0,0,0,.02);
  transition: transform .15s;
  border-left: 4px solid #ddd;
}
.grade-card:hover { transform: translateY(-2px); }
.grade-card.level-a { border-left-color: #67c23a; }
.grade-card.level-b { border-left-color: #409eff; }
.grade-card.level-c { border-left-color: #e6a23c; }
.grade-card.level-d { border-left-color: #f56c6c; }
.grade-card.level-f { border-left-color: #c03636; }
.gc-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.gc-name { font-size: 14px; font-weight: 600; color: #1a1a2e; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gc-score { font-size: 22px; font-weight: 700; flex-shrink: 0; margin-left: 8px; }
.level-a .gc-score { color: #67c23a; }
.level-b .gc-score { color: #409eff; }
.level-c .gc-score { color: #e6a23c; }
.level-d .gc-score { color: #f56c6c; }
.level-f .gc-score { color: #c03636; }
.gc-meta { display: flex; gap: 12px; font-size: 12px; color: #999; }

/* ===== Exam Section ===== */
.exam-section { margin-top: 24px; }
.exam-card {
  display: flex; gap: 16px; background: #fff; border-radius: 12px; padding: 14px 18px;
  border: 1px solid rgba(0,0,0,.04); box-shadow: 0 2px 8px rgba(0,0,0,.03);
  transition: transform .15s; margin-bottom: 8px;
}
.exam-card:hover { transform: translateY(-1px); }
.ec-left { text-align: center; flex-shrink: 0; width: 80px; padding: 4px 0; }
.ec-date { font-size: 20px; font-weight: 700; color: #409eff; }
.ec-time { font-size: 12px; color: #999; margin-top: 2px; }
.ec-body { flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 4px; }
.ec-name { font-size: 15px; font-weight: 600; color: #1a1a2e; }
.ec-location { font-size: 13px; color: #888; display: flex; align-items: center; gap: 4px; }
</style>
