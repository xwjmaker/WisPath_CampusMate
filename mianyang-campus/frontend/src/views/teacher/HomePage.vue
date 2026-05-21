<template>
  <div>
    <h2>教师首页</h2>
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
import { ChatDotSquare, User, CircleCheck } from '@element-plus/icons-vue'

const router = useRouter()
const cards = [
  { title: '智能助手', desc: '校园问答、事务咨询', icon: ChatDotSquare, color: '#409eff', link: '/teacher/agent' },
  { title: '学生成长', desc: '查看学生成长轨迹', icon: User, color: '#67c23a', link: '/teacher/students' },
  { title: '审批管理', desc: '请假、证明审批', icon: CircleCheck, color: '#e6a23c', link: '/teacher/approval' },
]
</script>
