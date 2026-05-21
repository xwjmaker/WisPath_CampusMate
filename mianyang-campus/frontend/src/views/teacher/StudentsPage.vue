<template>
  <div>
    <h2>学生成长查看</h2>
    <el-input v-model="search" placeholder="搜索学生姓名或学号" style="width:300px;margin-bottom:20px" />
    <el-table :data="students" v-if="students.length">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="college" label="学院" />
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="viewGrowth(scope.row)">查看成长轨迹</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-else description="暂无学生数据" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const search = ref('')
const students = ref([])
function viewGrowth(_row: any) {}
</script>
