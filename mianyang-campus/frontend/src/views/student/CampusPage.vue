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
      <el-tab-pane label="校园公告" name="announcements">
        <div v-if="announcements.length" class="announce-list">
          <a v-for="a in announcements" :key="a.url" :href="a.url" target="_blank" class="announce-item">
            <span class="announce-title">{{ a.title }}</span>
            <span class="announce-date">{{ a.date }}</span>
          </a>
        </div>
        <el-empty v-else description="暂无公告或获取失败" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getFigures, getSceneries, getAnnouncements } from '@/api/campus'
import type { CampusFigure, CampusScenery, Announcement } from '@/types'

const activeTab = ref('figures')
const figures = ref<CampusFigure[]>([])
const sceneries = ref<CampusScenery[]>([])
const announcements = ref<Announcement[]>([])

onMounted(async () => {
  figures.value = await getFigures() as any
  sceneries.value = await getSceneries() as any
  announcements.value = await getAnnouncements() as any
})
</script>

<style scoped>
.announce-list { margin-top: 16px; }
.announce-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; border-bottom: 1px solid #f0f0f0;
  text-decoration: none; color: #333; transition: background 0.2s;
}
.announce-item:hover { background: #f5f7fa; }
.announce-title { font-size: 14px; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.announce-date { font-size: 12px; color: #999; flex-shrink: 0; margin-left: 16px; }
</style>
