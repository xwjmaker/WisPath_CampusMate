<template>
  <div>
    <div class="page-header">
      <h2>学生成长档案</h2>
      <el-input v-model="search" placeholder="搜索姓名/学号/学院" style="width:280px" clearable @input="loadStudents">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <el-empty v-if="!students.length && loaded" description="暂无学生记录">
      <el-icon :size="48" color="#ddd"><User /></el-icon>
      <p style="color:#999;margin-top:8px">当前名下暂无学生</p>
    </el-empty>

    <el-row :gutter="16" v-else>
      <el-col :span="6" v-for="s in students" :key="s.id" style="margin-bottom:16px">
        <el-card :class="['student-card', s.crisis_level ? `level-${s.crisis_level}` : '']" shadow="hover">
          <div class="card-head">
            <el-avatar :size="40">{{ s.name[0] }}</el-avatar>
            <div class="card-info">
              <strong>{{ s.name }}</strong>
              <small>{{ s.college || '未分配' }}</small>
            </div>
            <el-tag v-if="s.crisis_level" :type="crisisType(s.crisis_level)" size="small" effect="dark">
              {{ crisisLabel(s.crisis_level) }}
            </el-tag>
          </div>
          <div class="card-stats">
            <span>成果数量 <b>{{ s.growth_count }}</b></span>
            <span>请假 <b>{{ s.leave_count }}</b></span>
          </div>
          <div class="card-score" v-if="s.score !== undefined">
            <span class="score-label">综合评分</span>
            <span :class="['score-value', scoreClass(s.score)]">{{ s.score }}</span>
          </div>
          <div v-if="s.skills_json?.skills?.length" class="card-skills">
            <el-tag v-for="sk in s.skills_json.skills.slice(0, 3)" :key="sk.name" size="small" round>{{ sk.name }}</el-tag>
          </div>
          <div class="card-actions">
            <el-button size="small" type="primary" plain @click="openDetail(s)">查询详情</el-button>
            <el-button size="small" type="success" plain @click="openContact(s)">联系学生</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Detail Drawer -->
    <el-drawer v-model="detailVisible" :title="detail?.name || '详情'" size="600px">
      <template v-if="detail">
        <el-tabs v-model="detailTab">
          <el-tab-pane label="技能画像" name="skills">
            <div v-if="detail.skills_json?.skills?.length">
              <h4>技能</h4>
              <div class="skill-list">
                <div v-for="sk in detail.skills_json.skills" :key="sk.name" class="skill-item">
                  <el-tag>{{ sk.name }}</el-tag>
                  <small>{{ sk.context }}</small>
                </div>
              </div>
            </div>
            <div v-if="detail.skills_json?.interests?.length">
              <h4>兴趣</h4>
              <div>
                <el-tag v-for="i in detail.skills_json.interests" :key="i" round style="margin:4px">{{ i }}</el-tag>
              </div>
            </div>
            <el-empty v-if="!detail.skills_json?.skills?.length && !detail.skills_json?.interests?.length" description="暂无技能画像数据" />
          </el-tab-pane>
          <el-tab-pane label="成长记录" name="growth">
            <el-timeline>
              <el-timeline-item v-for="r in detail.growth_records" :key="r.id" :timestamp="r.date">
                <el-tag size="small" :type="growthType(r.type)">{{ growthLabel(r.type) }}</el-tag>
                <p style="margin:4px 0"><strong>{{ r.title }}</strong></p>
                <p v-if="r.description" style="color:#666;font-size:13px">{{ r.description }}</p>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-if="!detail.growth_records.length" description="暂无成长记录" />
          </el-tab-pane>
          <el-tab-pane label="危机预警" name="crisis">
            <el-timeline>
              <el-timeline-item v-for="a in detail.crisis_alerts" :key="a.id" :timestamp="formatTime(a.created_at)">
                <el-alert
                  :title="crisisLabel(a.level)"
                  :type="crisisType(a.level)"
                  :description="a.summary"
                  :closable="false"
                  show-icon
                />
                <small v-if="a.keywords_matched" style="color:#999">匹配关键词：{{ a.keywords_matched }}</small>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-if="!detail.crisis_alerts.length" description="暂无预警记录" />
          </el-tab-pane>
          <el-tab-pane label="请假记录" name="leave">
            <el-table :data="detail.leave_requests" size="small" style="width:100%">
              <el-table-column prop="start_date" label="日期" width="100" />
              <el-table-column prop="leave_type" label="类型" width="70">
                <template #default="{ row }">{{ leaveTypeLabel(row.leave_type) }}</template>
              </el-table-column>
              <el-table-column prop="reason" label="原因" min-width="140" />
              <el-table-column prop="status" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'" size="small">
                    {{ row.status === 'approved' ? '通过' : row.status === 'rejected' ? '拒绝' : '待批' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="!detail.leave_requests.length" description="无请假记录" />
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-drawer>

    <!-- Contact Dialog -->
    <el-dialog v-model="contactVisible" :title="`发送消息给 ${contactStudent?.name || ''}`" width="420px">
      <el-input v-model="contactMsg" type="textarea" :rows="4" placeholder="输入消息内容..." />
      <template #footer>
        <el-button @click="contactVisible = false">取消</el-button>
        <el-button type="primary" @click="sendContactMsg" :loading="sending">发送</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, User } from '@element-plus/icons-vue'
import { getStudents, getStudentDetail, type StudentSummary, type StudentDetail } from '@/api/teacher'
import { sendMessage } from '@/api/messages'
import { ElMessage } from 'element-plus'

const search = ref('')
const students = ref<(StudentSummary & { score?: number })[]>([])
const loaded = ref(false)
const detailVisible = ref(false)
const detail = ref<StudentDetail | null>(null)
const detailTab = ref('skills')

const contactVisible = ref(false)
const contactStudent = ref<StudentSummary | null>(null)
const contactMsg = ref('')
const sending = ref(false)

async function loadStudents() {
  try {
    students.value = await getStudents(search.value || undefined)
    loaded.value = true
  } catch {}
}

function crisisType(level: string) {
  const map: Record<string, string> = { severe: 'danger', moderate: 'warning', mild: 'info' }
  return map[level] || 'info'
}

function crisisLabel(level: string) {
  const map: Record<string, string> = { severe: '高危', moderate: '中度', mild: '轻度' }
  return map[level] || level
}

function growthType(t: string) {
  const map: Record<string, string> = { honor: 'primary', competition: 'success', award: 'warning', practice: 'info' }
  return map[t] || 'info'
}

function growthLabel(t: string) {
  const map: Record<string, string> = { honor: '荣誉', competition: '竞赛', award: '奖项', practice: '实践', paper: '论文', achievement: '成果' }
  return map[t] || t
}

function leaveTypeLabel(t: string) {
  const map: Record<string, string> = { competition: '比赛', sick: '病假', personal: '事假', other: '其他' }
  return map[t] || t
}

function formatTime(t: string) {
  try { return new Date(t).toLocaleString('zh-CN') } catch { return t }
}

function scoreClass(score: number) {
  if (score >= 90) return 'score-excellent'
  if (score >= 75) return 'score-good'
  if (score >= 60) return 'score-average'
  return 'score-poor'
}

async function openDetail(s: StudentSummary) {
  try {
    detail.value = await getStudentDetail(s.id)
    detailVisible.value = true
    detailTab.value = 'skills'
  } catch {}
}

function openContact(s: StudentSummary) {
  contactStudent.value = s
  contactMsg.value = ''
  contactVisible.value = true
}

async function sendContactMsg() {
  if (!contactMsg.value.trim() || !contactStudent.value) return
  sending.value = true
  try {
    await sendMessage(contactStudent.value.id, contactMsg.value.trim())
    ElMessage.success('消息已发送')
    contactVisible.value = false
  } catch {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

onMounted(loadStudents)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.student-card { transition: transform .2s; }
.student-card:hover { transform: translateY(-2px); }
.level-severe { border-left: 3px solid #f56c6c; }
.level-moderate { border-left: 3px solid #e6a23c; }
.level-mild { border-left: 3px solid #909399; }
.card-head { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.card-info { flex: 1; display: flex; flex-direction: column; }
.card-stats { display: flex; gap: 16px; margin-bottom: 6px; font-size: 13px; color: #666; }
.card-score { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.score-label { font-size: 12px; color: #999; }
.score-value { font-size: 18px; font-weight: 700; }
.score-excellent { color: #67c23a; }
.score-good { color: #409eff; }
.score-average { color: #e6a23c; }
.score-poor { color: #f56c6c; }
.card-skills { margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
.card-actions { display: flex; gap: 8px; }
.skill-list { display: flex; flex-direction: column; gap: 8px; }
.skill-item { display: flex; align-items: center; gap: 8px; }
</style>
