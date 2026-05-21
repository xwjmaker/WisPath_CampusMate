<template>
  <div>
    <h2>学生首页</h2>
    <el-row :gutter="20">
      <el-col :span="8" v-for="card in cards" :key="card.title">
        <el-card shadow="hover" style="margin-bottom:20px;cursor:pointer" @click="router.push(card.link)">
          <el-icon :size="32" :color="card.color"><component :is="card.icon" /></el-icon>
          <h3>{{ card.title }}</h3>
          <p>{{ card.desc }}</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ChatDotSquare, PictureFilled, TrendCharts, Calendar, Document, Service } from '@element-plus/icons-vue'

const router = useRouter()
const cards = [
  { title: '智能助手', desc: '校园问答、办事咨询', icon: ChatDotSquare, color: '#409eff', link: '/student/agent' },
  { title: '校园风采', desc: '人物风采、校园风景', icon: PictureFilled, color: '#67c23a', link: '/student/campus' },
  { title: '成长轨迹', desc: '荣誉、竞赛、实践', icon: TrendCharts, color: '#e6a23c', link: '/student/growth' },
  { title: '课表查询', desc: '查看课程安排', icon: Calendar, color: '#f56c6c', link: '/student/schedule' },
  { title: '成绩考试', desc: '成绩查询、考试安排', icon: Document, color: '#909399', link: '/student/grade' },
  { title: '办事服务', desc: '请假申请、证明打印', icon: Service, color: '#b37feb', link: '/student/service' },
]
</script>
