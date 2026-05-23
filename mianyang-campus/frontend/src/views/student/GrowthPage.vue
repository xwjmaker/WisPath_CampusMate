<template>
  <div class="growth-page">
    <div class="score-header">
      <div class="score-ring">
        <svg viewBox="0 0 120 120" class="score-svg">
          <circle cx="60" cy="60" r="52" fill="none" stroke="#f0f2f5" stroke-width="8" />
          <circle cx="60" cy="60" r="52" fill="none" stroke="url(#scoreGrad)" stroke-width="8"
            :stroke-dasharray="circleLen" :stroke-dashoffset="circleOffset" stroke-linecap="round"
            transform="rotate(-90, 60, 60)" />
          <defs><linearGradient id="scoreGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#409eff" /><stop offset="100%" stop-color="#67c23a" />
          </linearGradient></defs>
        </svg>
        <div class="score-value">{{ profile?.total_score ?? '--' }}</div>
        <div class="score-label">综合评分</div>
      </div>
      <div class="score-stats">
        <div class="stat-item" v-for="s in statsCards" :key="s.label">
          <span class="stat-num">{{ s.value }}</span>
          <span class="stat-label">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header><span class="card-title">综合能力雷达</span></template>
          <v-chart :option="radarOption" class="chart" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header><span class="card-title">成长类型分布</span></template>
          <v-chart :option="barOption" class="chart" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="chart-card" style="margin-top:20px">
      <template #header><span class="card-title">成长趋势</span></template>
      <v-chart :option="lineOption" class="chart chart-tall" autoresize />
    </el-card>

    <el-card shadow="hover" class="chart-card" style="margin-top:20px">
      <template #header><span class="card-title">学习绩点轨迹</span></template>
      <v-chart :option="gpaOption" class="chart chart-tall" autoresize />
    </el-card>

    <el-row :gutter="20" style="margin-top:20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">技能标签</span></template>
          <div v-if="profile?.skills.length" class="tag-cloud">
            <el-tag v-for="s in profile.skills" :key="s" class="skill-tag" type="primary">{{ s }}</el-tag>
          </div>
          <el-empty v-else description="暂无技能数据" :image-size="60" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">兴趣领域</span></template>
          <div v-if="profile?.interests.length" class="tag-cloud">
            <el-tag v-for="s in profile.interests" :key="s" class="skill-tag" type="success">{{ s }}</el-tag>
          </div>
          <el-empty v-else description="暂无兴趣数据" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <div class="records-section">
      <div class="records-header">
        <span class="card-title">成长记录</span>
        <el-button type="primary" size="small" @click="openDialog">添加记录</el-button>
      </div>
      <div v-if="records.length" class="records-list">
        <el-card v-for="r in records" :key="r.id" shadow="hover" class="record-card">
          <div class="record-type-tag">
            <el-tag :type="typeTagType(r.type)" size="small">{{ typeLabel(r.type) }}</el-tag>
          </div>
          <div class="record-body">
            <div class="record-title">{{ r.title }}</div>
            <div class="record-meta" v-if="r.description">{{ r.description }}</div>
            <div class="record-details" v-if="r.type === 'honor' && r.honor_level">
              <el-tag size="small" hit effect="plain">{{ r.honor_level }}</el-tag>
            </div>
            <div class="record-details" v-else-if="r.type === 'competition'">
              <span v-if="r.organizer" class="detail-item">主办方: {{ r.organizer }}</span>
              <span v-if="r.competition_level" class="detail-item">等级: {{ r.competition_level }}</span>
            </div>
            <div class="record-details" v-else-if="r.type === 'practice' && r.practice_type">
              <span class="detail-item">{{ r.practice_type }}</span>
            </div>
            <div class="record-details" v-else-if="r.type === 'paper'">
              <span v-if="r.paper_name" class="detail-item">{{ r.paper_name }}</span>
              <span v-if="r.paper_type" class="detail-item">[{{ r.paper_type }}]</span>
            </div>
            <div class="record-details" v-else-if="r.type === 'achievement'">
              <span v-if="r.achievement_name" class="detail-item">{{ r.achievement_name }}</span>
              <span v-if="r.achievement_type" class="detail-item">[{{ r.achievement_type }}]</span>
            </div>
            <div class="record-date">{{ formatDate(r.date) }}</div>
          </div>
        </el-card>
      </div>
      <el-empty v-else description="暂无成长记录" />
    </div>

    <el-dialog v-model="dialogVisible" :title="'添加成长记录 — ' + typeLabel(form.type)" width="600px" class="growth-dialog">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="form.type" @change="onTypeChange">
                <el-option label="荣誉" value="honor" />
                <el-option label="竞赛" value="competition" />
                <el-option label="实践" value="practice" />
                <el-option label="论文" value="paper" />
                <el-option label="成果" value="achievement" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="日期">
              <el-date-picker v-model="form.date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 荣誉 -->
        <template v-if="form.type === 'honor'">
          <el-form-item label="荣誉等级">
            <el-select v-model="form.honor_level" style="width:100%">
              <el-option label="校级" value="校级" />
              <el-option label="省级" value="省级" />
              <el-option label="国家级" value="国家级" />
              <el-option label="国际级" value="国际级" />
            </el-select>
          </el-form-item>
          <el-form-item label="荣誉名称">
            <el-input v-model="form.title" placeholder="例如：国家奖学金" />
          </el-form-item>
          <el-form-item label="荣誉描述">
            <el-input v-model="form.description" type="textarea" :rows="2" placeholder="颁发单位、获奖时间等" />
          </el-form-item>
          <el-form-item label="证明材料">
            <UploadBtn v-model="form.attachment_url" />
          </el-form-item>
        </template>

        <!-- 竞赛 -->
        <template v-if="form.type === 'competition'">
          <el-form-item label="竞赛名称">
            <el-input v-model="form.title" placeholder="例如：ACM-ICPC国际大学生程序设计竞赛" />
          </el-form-item>
          <el-form-item label="主办方">
            <el-input v-model="form.organizer" placeholder="例如：ACM/ICPC组委会" />
          </el-form-item>
          <el-form-item label="竞赛等级">
            <el-select v-model="form.competition_level" style="width:100%">
              <el-option label="校级" value="校级" />
              <el-option label="省级" value="省级" />
              <el-option label="国家级" value="国家级" />
              <el-option label="国际级" value="国际级" />
            </el-select>
          </el-form-item>
          <el-form-item label="获奖情况">
            <el-input v-model="form.description" type="textarea" :rows="2" placeholder="金奖/银奖/铜奖/一等奖等" />
          </el-form-item>
          <el-form-item label="证明材料">
            <UploadBtn v-model="form.attachment_url" />
          </el-form-item>
        </template>

        <!-- 实践 -->
        <template v-if="form.type === 'practice'">
          <el-form-item label="实践类型">
            <el-select v-model="form.practice_type" style="width:100%">
              <el-option label="社会志愿活动" value="社会志愿活动" />
              <el-option label="三下乡" value="三下乡" />
              <el-option label="支教" value="支教" />
              <el-option label="西部计划" value="西部计划" />
              <el-option label="筑梦扬帆计划" value="筑梦扬帆计划" />
              <el-option label="其他社会实践" value="其他社会实践" />
            </el-select>
          </el-form-item>
          <el-form-item label="实践名称">
            <el-input v-model="form.title" placeholder="例如：暑期三下乡支教活动" />
          </el-form-item>
          <el-form-item label="实践描述">
            <el-input v-model="form.description" type="textarea" :rows="2" placeholder="实践内容、服务时长等" />
          </el-form-item>
          <el-form-item label="荣誉证明">
            <el-input v-model="form.practice_certificate" type="textarea" :rows="2" placeholder="优秀志愿者证书/表彰文件等" />
          </el-form-item>
          <el-form-item label="证明材料">
            <UploadBtn v-model="form.attachment_url" />
          </el-form-item>
        </template>

        <!-- 论文 -->
        <template v-if="form.type === 'paper'">
          <el-form-item label="论文题目">
            <el-input v-model="form.paper_name" placeholder="论文完整标题" />
          </el-form-item>
          <el-form-item label="期刊类型">
            <el-select v-model="form.paper_type" style="width:100%">
              <el-option label="普刊" value="普刊" />
              <el-option label="核心期刊" value="核心期刊" />
              <el-option label="SCI" value="SCI" />
              <el-option label="EI" value="EI" />
              <el-option label="顶刊" value="顶刊" />
              <el-option label="会议论文" value="会议论文" />
            </el-select>
          </el-form-item>
          <el-form-item label="第一作者">
            <el-input v-model="form.first_author" placeholder="姓名" />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="第二作者">
                <el-input v-model="form.second_author" placeholder="姓名（选填）" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="第三作者">
                <el-input v-model="form.third_author" placeholder="姓名（选填）" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注">
            <el-input v-model="form.description" type="textarea" :rows="2" placeholder="发表时间、期刊名称等" />
          </el-form-item>
          <el-form-item label="证明材料">
            <UploadBtn v-model="form.attachment_url" />
          </el-form-item>
        </template>

        <!-- 成果 -->
        <template v-if="form.type === 'achievement'">
          <el-form-item label="成果类型">
            <el-select v-model="form.achievement_type" style="width:100%">
              <el-option label="发明专利" value="发明专利" />
              <el-option label="实用新型专利" value="实用新型专利" />
              <el-option label="外观设计专利" value="外观设计专利" />
              <el-option label="软件著作权" value="软件著作权" />
              <el-option label="作品著作权" value="作品著作权" />
            </el-select>
          </el-form-item>
          <el-form-item label="成果名称">
            <el-input v-model="form.achievement_name" placeholder="专利/软著名称" />
          </el-form-item>
          <el-form-item label="成果标题">
            <el-input v-model="form.title" placeholder="简短标题（可选）" />
          </el-form-item>
          <el-form-item label="成果描述">
            <el-input v-model="form.description" type="textarea" :rows="2" placeholder="授权号、申请日等信息" />
          </el-form-item>
          <el-form-item label="证明材料">
            <UploadBtn v-model="form.attachment_url" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdd">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { RadarChart, BarChart, LineChart } from 'echarts/charts'
import { GridComponent, RadarComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getGrowthRecords, createGrowthRecord, getGrowthProfile } from '@/api/growth'
import type { GrowthProfile } from '@/api/growth'
import type { GrowthRecord } from '@/types'
import UploadBtn from '@/components/upload/UploadBtn.vue'

use([RadarChart, BarChart, LineChart, GridComponent, RadarComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const profile = ref<GrowthProfile | null>(null)
const records = ref<GrowthRecord[]>([])
const dialogVisible = ref(false)
const form = ref<Record<string, any>>({ type: 'honor', title: '', description: '', date: '' })

function typeLabel(t: string) {
  const labels: Record<string, string> = { honor: '荣誉', competition: '竞赛', practice: '实践', paper: '论文', achievement: '成果' }
  return labels[t] || t
}

function typeTagType(t: string) {
  const types: Record<string, string> = { honor: 'warning', competition: 'primary', practice: 'success', paper: 'danger', achievement: 'info' }
  return types[t] || 'default'
}

function formatDate(d: string) {
  if (!d) return ''
  return d.slice(0, 10)
}

function onTypeChange() {
  form.value.title = ''
  form.value.description = ''
  form.value.honor_level = ''
  form.value.organizer = ''
  form.value.competition_level = ''
  form.value.practice_type = ''
  form.value.practice_certificate = ''
  form.value.paper_type = ''
  form.value.paper_name = ''
  form.value.first_author = ''
  form.value.second_author = ''
  form.value.third_author = ''
  form.value.achievement_type = ''
  form.value.achievement_name = ''
}

function openDialog() {
  onTypeChange()
  dialogVisible.value = true
}

const circleLen = 2 * Math.PI * 52

const circleOffset = computed(() => {
  if (!profile.value) return circleLen
  return circleLen - (circleLen * Math.min(100, profile.value.total_score) / 100)
})

const statsCards = computed(() => [
  { label: '成长记录', value: profile.value?.total_records ?? 0 },
  { label: '技能数量', value: profile.value?.total_skills ?? 0 },
  { label: '荣誉', value: profile.value?.stats_by_type.find(s => s.name === '荣誉')?.value ?? 0 },
  { label: '竞赛', value: profile.value?.stats_by_type.find(s => s.name === '竞赛')?.value ?? 0 },
  { label: '论文', value: profile.value?.stats_by_type.find(s => s.name === '论文')?.value ?? 0 },
  { label: '成果', value: profile.value?.stats_by_type.find(s => s.name === '成果')?.value ?? 0 },
])

const radarOption = computed(() => ({
  radar: {
    indicator: (profile.value?.radar ?? []).map(d => ({ name: d.name, max: 100 })),
    shape: 'circle',
    center: ['50%', '50%'],
    radius: '65%',
    axisName: { color: '#333', fontSize: 12 },
    splitArea: { areaStyle: { color: ['rgba(64,158,255,.03)', 'rgba(64,158,255,.06)'] } },
  },
  series: [{
    type: 'radar',
    data: [{ value: profile.value?.radar.map(d => d.value) ?? [0, 0, 0, 0, 0] }],
    areaStyle: { color: 'rgba(64,158,255,.2)' },
    lineStyle: { color: '#409eff', width: 2 },
    itemStyle: { color: '#409eff' },
  }],
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 10, bottom: 30 },
  xAxis: {
    type: 'category',
    data: (profile.value?.stats_by_type ?? []).map(s => s.name),
    axisLabel: { color: '#666' },
  },
  yAxis: { type: 'value', axisLabel: { color: '#666' }, splitLine: { lineStyle: { color: '#f0f0f0' } } },
  series: [{
    type: 'bar',
    data: (profile.value?.stats_by_type ?? []).map(s => s.value),
    barWidth: '40%',
    itemStyle: {
      borderRadius: [6, 6, 0, 0],
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#409eff' }, { offset: 1, color: '#67c23a' }] },
    },
  }],
}))

const lineOption = computed(() => {
  const trend = profile.value?.monthly_trend ?? []
  const months = [...new Set(trend.map(t => t.month))].sort()
  const types = [...new Set(trend.map(t => t.type))]
  const colors: Record<string, string> = { honor: '#e6a23c', competition: '#409eff', practice: '#67c23a', paper: '#f56c6c', achievement: '#909399' }
  const typeLabels: Record<string, string> = { honor: '荣誉', competition: '竞赛', practice: '实践', paper: '论文', achievement: '成果' }

  return {
    tooltip: { trigger: 'axis' },
    legend: { data: types.map(t => typeLabels[t] || t), bottom: 0 },
    grid: { left: 40, right: 20, top: 10, bottom: 40 },
    xAxis: { type: 'category', data: months, axisLabel: { color: '#666' } },
    yAxis: { type: 'value', axisLabel: { color: '#666' }, splitLine: { lineStyle: { color: '#f0f0f0' } } },
    series: types.map(t => ({
      name: typeLabels[t] || t,
      type: 'line',
      smooth: true,
      data: months.map(m => trend.find(item => item.month === m && item.type === t)?.count ?? 0),
      itemStyle: { color: colors[t] || '#909399' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: (colors[t] || '#909399') + '40' }, { offset: 1, color: (colors[t] || '#909399') + '05' }] } },
    })),
  }
})

const gpaOption = computed(() => {
  const data = profile.value?.gpa_trend ?? []
  if (!data.length) return {}
  const semLabels = data.map(d => d.semester.replace('2023-2024-1', '23-24 上').replace('2023-2024-2', '23-24 下').replace('2024-2025-1', '24-25 上').replace('2024-2025-2', '24-25 下'))
  const values = data.map(d => d.gpa)
  const minGpa = Math.max(0, Math.floor(Math.min(...values) * 10) / 10 - 0.3)
  return {
    tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].axisValue}<br/>平均绩点: ${p[0].value}` },
    grid: { left: 50, right: 30, top: 20, bottom: 30 },
    xAxis: { type: 'category', data: semLabels, axisLabel: { color: '#666', fontSize: 13 } },
    yAxis: { type: 'value', min: minGpa, max: 4.0, axisLabel: { color: '#666' }, splitLine: { lineStyle: { color: '#f0f0f0' } } },
    series: [{
      type: 'line', data: values, smooth: true,
      symbol: 'circle', symbolSize: 10,
      lineStyle: { color: '#e6a23c', width: 3 },
      itemStyle: { color: '#e6a23c' },
      areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#e6a23c40' }, { offset: 1, color: '#e6a23c05' }] } },
      markLine: { data: [{ yAxis: 3.5, label: { formatter: '优秀线 3.5', color: '#67c23a' } }, { yAxis: 2.5, label: { formatter: '警戒线 2.5', color: '#f56c6c' } }], silent: true, lineStyle: { type: 'dashed' } },
    }],
  }
})

onMounted(async () => {
  try { profile.value = await getGrowthProfile() as any } catch { /* ignore */ }
  records.value = await getGrowthRecords() as any
})

async function handleAdd() {
  const payload: Record<string, any> = {}
  for (const k of Object.keys(form.value)) {
    if (form.value[k] !== '' && form.value[k] !== undefined) {
      payload[k] = form.value[k]
    }
  }
  await createGrowthRecord(payload as any)
  ElMessage.success('添加成功')
  dialogVisible.value = false
  records.value = await getGrowthRecords() as any
  try { profile.value = await getGrowthProfile() as any } catch { /* ignore */ }
}
</script>

<style scoped>
.growth-page { max-width: 1100px; margin: 0 auto; padding: 8px 0; }

.score-header {
  display: flex; align-items: center; gap: 40px;
  padding: 24px 32px; margin-bottom: 24px;
  background: linear-gradient(135deg, #f0f8ff, #f6ffed);
  border-radius: 16px;
}
.score-ring { position: relative; width: 120px; height: 120px; flex-shrink: 0; }
.score-svg { width: 120px; height: 120px; }
.score-value {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -65%);
  font-size: 32px; font-weight: 700; color: #409eff;
}
.score-label {
  position: absolute; bottom: 12px; left: 0; right: 0; text-align: center;
  font-size: 11px; color: #999;
}
.score-stats { display: flex; gap: 32px; flex: 1; }
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-num { font-size: 28px; font-weight: 700; color: #333; }
.stat-label { font-size: 12px; color: #999; margin-top: 4px; }

.chart-card { margin-bottom: 0; }
.chart { width: 100%; height: 280px; }
.chart-tall { height: 220px; }
.card-title { font-size: 15px; font-weight: 600; color: #333; }

.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.skill-tag { font-size: 13px; padding: 4px 14px; border-radius: 20px; }

.records-section { margin-top: 24px; }
.records-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.timeline { margin-top: 0; }
</style>
