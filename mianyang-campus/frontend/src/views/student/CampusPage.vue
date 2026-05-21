<template>
  <div>
    <h2>校园风采</h2>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="人物风采" name="figures">
        <el-row :gutter="20">
          <el-col :span="8" v-for="f in figures" :key="f.id" style="margin-bottom:20px">
            <FigureCard :figure="f" />
          </el-col>
        </el-row>
      </el-tab-pane>
      <el-tab-pane label="校园风景" name="sceneries">
        <el-row :gutter="20">
          <el-col :span="8" v-for="s in sceneries" :key="s.id" style="margin-bottom:20px">
            <SceneryCard :scenery="s" />
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFigures, getSceneries } from '@/api/campus'
import type { CampusFigure, CampusScenery } from '@/types'
import FigureCard from '@/components/campus/FigureCard.vue'
import SceneryCard from '@/components/campus/SceneryCard.vue'

const activeTab = ref('figures')
const figures = ref<CampusFigure[]>([])
const sceneries = ref<CampusScenery[]>([])

onMounted(async () => {
  figures.value = await getFigures() as any
  sceneries.value = await getSceneries() as any
})
</script>
