<template>
  <div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="人物风采" name="figures">
        <el-row :gutter="20">
          <el-col :span="8" v-for="f in figures" :key="f.id" style="margin-bottom:20px">
            <FigureCard :figure="f" />
          </el-col>
          <el-col :span="8" style="margin-bottom:20px">
            <el-card shadow="hover" class="ext-card" @click="openLink('https://www.mycc.edu.cn/mcyx/msfc.htm')">
              <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#409eff,#67c23a);display:flex;align-items:center;justify-content:center;font-size:32px;color:#fff;font-weight:700;margin:0 auto">师</div>
              <h3 style="text-align:center">名师风采</h3>
              <p style="text-align:center;color:#666">了解更多 →</p>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>

      <el-tab-pane label="校园风景" name="sceneries">
        <div class="video-section">
          <video
            ref="videoRef"
            src="/video/校园宣传片.mp4"
            class="campus-video"
            autoplay
            muted
            loop
            playsinline
            @loadedmetadata="onVideoReady"
          ></video>
          <div class="video-controls">
            <span class="video-title">绵阳城市学院宣传片</span>
            <div class="video-actions">
              <span class="speed-badge">1.5x</span>
              <el-button text circle @click="toggleMute" class="control-btn">
                <el-icon :size="20"><Mute v-if="videoMuted" /><svg v-else viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 8.5v7a4.49 4.49 0 0 0 2.5-3.5zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <div class="gallery-filter">
          <el-button
            v-for="f in galleryFilters"
            :key="f.key"
            :type="galleryActive === f.key ? 'primary' : 'default'"
            :plain="galleryActive !== f.key"
            size="large"
            @click="galleryActive = f.key"
          >{{ f.label }}</el-button>
        </div>
        <div v-if="galleryImages.length" class="gallery-grid">
          <div v-for="img in filteredGallery" :key="img.image_url" class="gallery-card" @click="openPreview(img)">
            <img :src="img.image_url" class="gallery-img" />
            <div class="gallery-overlay">
              <span class="gallery-label">{{ img.title }}</span>
              <span class="gallery-badge">{{ img.campus }}</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无校园风光图片" />

        <el-dialog v-model="previewVisible" :title="previewTitle" width="80vw" top="5vh" destroy-on-close>
          <div class="preview-wrap">
            <img :src="previewUrl" class="preview-img" />
          </div>
          <template #footer>
            <el-button @click="previewPrev" :disabled="previewIndex <= 0">上一张</el-button>
            <span class="preview-counter">{{ previewIndex + 1 }} / {{ filteredGallery.length }}</span>
            <el-button @click="previewNext" :disabled="previewIndex >= filteredGallery.length - 1">下一张</el-button>
          </template>
        </el-dialog>
      </el-tab-pane>

      <el-tab-pane label="绵城印象" name="impression">
        <div class="impression-section">
          <h3 class="section-title">绵城印象</h3>
          <el-row :gutter="20">
            <el-col :span="8" v-for="item in impressionItems" :key="item.title" style="margin-bottom:20px">
              <el-card shadow="hover" class="ext-card" @click="openLink(item.url)">
                <div class="ext-icon">{{ item.icon }}</div>
                <h3 style="text-align:center">{{ item.title }}</h3>
                <p style="text-align:center;color:#999">了解更多 →</p>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div class="impression-section">
          <h3 class="section-title">专业分院</h3>
          <el-row :gutter="20">
            <el-col :span="8" v-for="item in collegeItems" :key="item.name" style="margin-bottom:20px">
              <el-card shadow="hover" class="ext-card" @click="openLink(item.url)">
                <div class="ext-icon">{{ item.icon }}</div>
                <h3 style="text-align:center">{{ item.name }}</h3>
                <p style="text-align:center;color:#999">进入官网 →</p>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div class="impression-section">
          <h3 class="section-title">走进城市学院</h3>
          <el-row :gutter="20">
            <el-col :span="8" v-for="item in campusLifeItems" :key="item.title" style="margin-bottom:20px">
              <el-card shadow="hover" class="ext-card" @click="openLink(item.url)">
                <div class="ext-icon">{{ item.icon }}</div>
                <h3 style="text-align:center">{{ item.title }}</h3>
                <p style="text-align:center;color:#999">了解更多 →</p>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane label="校园公告" name="announcements">
        <div v-if="announcements.length" class="announce-list">
          <a v-for="a in announcements" :key="a.url ?? ''" :href="a.url ?? '#'" target="_blank" class="announce-item">
            <span class="announce-title">{{ a.title }}</span>
            <span class="announce-date">{{ a.date ?? '' }}</span>
          </a>
        </div>
        <el-empty v-else description="暂无公告或获取失败" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getFigures, getAnnouncements } from '@/api/campus'
import { Mute } from '@element-plus/icons-vue'
import type { CampusFigure, Announcement } from '@/types'
import FigureCard from '@/components/campus/FigureCard.vue'

interface GalleryImage {
  title: string
  image_url: string
  campus: string
}

const activeTab = ref('figures')
const figures = ref<CampusFigure[]>([])
const announcements = ref<Announcement[]>([])
const galleryActive = ref('all')

const videoRef = ref<HTMLVideoElement>()
const videoMuted = ref(true)

function onVideoReady() {
  if (videoRef.value) videoRef.value.playbackRate = 1.5
}

function toggleMute() {
  if (!videoRef.value) return
  videoMuted.value = !videoMuted.value
  videoRef.value.muted = videoMuted.value
}

const previewVisible = ref(false)
const previewIndex = ref(0)

const previewUrl = computed(() => {
  const list = filteredGallery.value
  return list[previewIndex.value]?.image_url || ''
})

const previewTitle = computed(() => {
  const list = filteredGallery.value
  return list[previewIndex.value]?.title || ''
})

function openPreview(img: GalleryImage) {
  previewIndex.value = filteredGallery.value.indexOf(img)
  previewVisible.value = true
}

function previewPrev() {
  if (previewIndex.value > 0) previewIndex.value--
}

function previewNext() {
  if (previewIndex.value < filteredGallery.value.length - 1) previewIndex.value++
}

const galleryFilters = [
  { key: 'all', label: '全部' },
  { key: '安州', label: '安州校区' },
  { key: '游仙', label: '游仙校区' },
]

const filteredGallery = computed(() => {
  if (galleryActive.value === 'all') return galleryImages
  return galleryImages.filter(i => i.campus === galleryActive.value)
})

const impressionItems = [
  { title: '仪器设备', url: 'https://www.mycc.edu.cn/mcyx/yqsb.htm', icon: '🔬' },
  { title: '生活条件', url: 'https://www.mycc.edu.cn/mcyx/shtj.htm', icon: '🏠' },
]

const collegeItems = [
  { name: '马克思主义学院', url: 'https://mksxy.mycc.edu.cn/', icon: '📖' },
  { name: '人工智能学院', url: 'https://xdjsxy.mycc.edu.cn/', icon: '🤖' },
  { name: '智能制造与工程学院', url: 'https://xdcsjsxy.mycc.edu.cn/', icon: '⚙️' },
  { name: '健康与教育学院', url: 'https://xdfw.mycc.edu.cn/', icon: '🏥' },
  { name: '商学院', url: 'https://jgxy.mycc.edu.cn/', icon: '📊' },
  { name: '创意设计学院', url: 'https://cysjxy.mycc.edu.cn/', icon: '🎨' },
  { name: '终身教育学院', url: 'https://jxjy.mycc.edu.cn/', icon: '📚' },
]

const galleryImages: GalleryImage[] = [
  { title: '安州校区博润楼', image_url: '/images/campus/安州校区博润楼.jpg', campus: '安州' },
  { title: '安州校区众立楼', image_url: '/images/campus/安州校区众立楼.jpg', campus: '安州' },
  { title: '安州校区博训楼', image_url: '/images/campus/安州校区博训楼.jpg', campus: '安州' },
  { title: '安州校区综合活动馆', image_url: '/images/campus/安州校区综合活动馆.jpg', campus: '安州' },
  { title: '安州校区体育馆', image_url: '/images/campus/安州校区体育馆.jpg', campus: '安州' },
  { title: '安州校区工程训练中心', image_url: '/images/campus/安州校区工程训练中心.jpg', campus: '安州' },
  { title: '安州校区田径运动场', image_url: '/images/campus/安州校区田径运动场.jpg', campus: '安州' },
  { title: '安州校区博文楼', image_url: '/images/campus/安州校区博文楼.jpg', campus: '安州' },
  { title: '安州校区博远楼', image_url: '/images/campus/安州校区博远楼.jpg', campus: '安州' },
  { title: '安州校区博雅楼', image_url: '/images/campus/安州校区博雅楼.jpg', campus: '安州' },
  { title: '游仙校区第一教学楼', image_url: '/images/campus/游仙校区第一教学楼.jpg', campus: '游仙' },
  { title: '游仙校区科技楼', image_url: '/images/campus/游仙校区科技楼.jpg', campus: '游仙' },
  { title: '游仙校区博采溪', image_url: '/images/campus/游仙校区博采溪.jpg', campus: '游仙' },
  { title: '游仙校区行政楼', image_url: '/images/campus/游仙校区行政楼.jpg', campus: '游仙' },
  { title: '游仙校区博识楼', image_url: '/images/campus/游仙校区博识楼.jpg', campus: '游仙' },
  { title: '游仙校区木桥', image_url: '/images/campus/游仙校区木桥.jpg', campus: '游仙' },
  { title: '游仙校区博识楼C区草坪', image_url: '/images/campus/游仙校区博识楼C区草坪.jpg', campus: '游仙' },
  { title: '游仙校区夜景', image_url: '/images/campus/游仙校区夜景.jpg', campus: '游仙' },
  { title: '游仙校区风雨操场', image_url: '/images/campus/游仙校区风雨操场.jpg', campus: '游仙' },
  { title: '游仙校区田径运动场', image_url: '/images/campus/游仙校区田径运动场.jpg', campus: '游仙' },
  { title: '游仙校区篮球场', image_url: '/images/campus/游仙校区篮球场.jpg', campus: '游仙' },
]

const campusLifeItems = [
  { title: '校园文化', url: 'https://www.mycc.edu.cn/zjcsxy/xywh.htm', icon: '🎭' },
  { title: '学校动态', url: 'https://www.mycc.edu.cn/zjcsxy/xxdt.htm', icon: '📰' },
  { title: '校园服务', url: 'https://www.mycc.edu.cn/zjcsxy/xyfw.htm', icon: '🎯' },
]

function openLink(url: string) {
  window.open(url, '_blank')
}

onMounted(async () => {
  figures.value = await getFigures() as any
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

.ext-card { cursor: pointer; transition: transform .15s, box-shadow .15s; }
.ext-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(0,0,0,.1); }
.ext-icon { font-size: 40px; text-align: center; padding: 12px 0 8px; }

.video-section {
  position: relative; border-radius: 16px; overflow: hidden; margin-bottom: 28px;
  box-shadow: 0 8px 30px rgba(0,0,0,.12);
}
.campus-video { width: 100%; display: block; max-height: 480px; object-fit: cover; }
.video-controls {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 50px 20px 14px;
  background: linear-gradient(transparent, rgba(0,0,0,.7));
  display: flex; justify-content: space-between; align-items: flex-end;
}
.video-title { color: #fff; font-size: 18px; font-weight: 600; text-shadow: 0 2px 8px rgba(0,0,0,.5); }
.video-actions { display: flex; align-items: center; gap: 8px; }
.speed-badge {
  font-size: 11px; padding: 2px 10px; border-radius: 10px;
  background: rgba(255,255,255,.2); backdrop-filter: blur(4px);
  color: #fff; font-weight: 600; letter-spacing: 1px;
}
.control-btn { color: #fff !important; background: rgba(255,255,255,.15) !important; }
.control-btn:hover { background: rgba(255,255,255,.3) !important; }

.gallery-filter { display: flex; gap: 12px; margin-bottom: 24px; }
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.gallery-card {
  position: relative; border-radius: 12px; overflow: hidden; cursor: pointer;
  transition: transform .2s, box-shadow .2s; aspect-ratio: 16 / 10;
}
.gallery-card:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,.15); }
.gallery-img { width: 100%; height: 100%; object-fit: cover; }
.gallery-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 40px 16px 12px;
  background: linear-gradient(transparent, rgba(0,0,0,.65));
  display: flex; justify-content: space-between; align-items: flex-end;
  pointer-events: none;
}
.gallery-label { color: #fff; font-size: 15px; font-weight: 600; text-shadow: 0 1px 4px rgba(0,0,0,.4); }
.gallery-badge {
  font-size: 11px; padding: 2px 10px; border-radius: 10px;
  background: rgba(255,255,255,.2); backdrop-filter: blur(4px);
  color: #fff; font-weight: 500;
}
.gallery-loading { text-align: center; padding: 80px 0; color: #999; }
.gallery-loading p { margin-top: 12px; }

.preview-wrap { text-align: center; }
.preview-img { max-width: 100%; max-height: 70vh; border-radius: 8px; }
.preview-counter { color: #999; font-size: 14px; margin: 0 16px; }

.impression-section { margin-bottom: 32px; }
.section-title {
  font-size: 18px; font-weight: 600; color: #409eff;
  padding-left: 12px; border-left: 3px solid #409eff;
  margin-bottom: 16px; line-height: 1;
}
</style>
