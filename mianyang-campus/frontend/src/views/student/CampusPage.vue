<template>
  <div class="campus-page">
    <aside class="campus-sidebar">
      <button v-for="t in tabItems" :key="t.key"
        :class="['side-btn', { active: activeTab === t.key }]"
        @click="activeTab = t.key">
        <span class="side-icon">{{ t.icon }}</span>
        <span class="side-label">{{ t.label }}</span>
      </button>
    </aside>

    <div class="campus-main">
      <Transition name="fade-slide" mode="out-in">
        <div :key="activeTab" class="tab-content">
        <template v-if="activeTab === 'figures'">
          <div class="figure-grid">
            <FigureCard v-for="f in figures" :key="f.id" :figure="f" />
            <div class="figure-card teacher-card" @click="openLink('https://www.mycc.edu.cn/mcyx/msfc.htm')">
              <div class="teacher-badge">师</div>
              <h3>名师风采</h3>
              <span class="card-hint">了解更多 →</span>
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'sceneries'">
          <div class="video-section">
            <video ref="videoRef" src="/video/校园宣传片.mp4" class="campus-video"
              autoplay muted loop playsinline @loadedmetadata="onVideoReady"></video>
            <div class="video-controls">
              <span class="video-title">绵阳城市学院宣传片</span>
              <div class="video-actions">
                <span class="speed-badge">1.5x</span>
                <button class="mute-btn" @click="toggleMute">
                  <el-icon :size="20"><Mute v-if="videoMuted" /><Microphone v-else /></el-icon>
                </button>
              </div>
            </div>
          </div>
          <div class="gallery-filter">
            <button v-for="f in galleryFilters" :key="f.key"
              :class="['filter-btn', { active: galleryActive === f.key }]"
              @click="galleryActive = f.key">{{ f.label }}</button>
          </div>
          <div v-if="galleryImages.length" class="gallery-grid">
            <div v-for="img in filteredGallery" :key="img.image_url" class="gallery-card" @click="openPreview(img)">
              <img :src="img.image_url" class="gallery-img" loading="lazy" />
              <div class="gallery-overlay">
                <span class="gallery-label">{{ img.title }}</span>
                <span class="gallery-campus">{{ img.campus }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无校园风光图片" />
          <Teleport to="body">
            <div v-if="previewVisible" class="preview-mask" @click.self="previewVisible = false">
              <div class="preview-container">
                <img :src="previewUrl" class="preview-img" />
                <div class="preview-bar">
                  <button class="preview-nav" :disabled="previewIndex <= 0" @click="previewPrev">‹</button>
                  <span class="preview-counter">{{ previewIndex + 1 }} / {{ filteredGallery.length }}</span>
                  <button class="preview-nav" :disabled="previewIndex >= filteredGallery.length - 1" @click="previewNext">›</button>
                  <button class="preview-close" @click="previewVisible = false">✕</button>
                </div>
              </div>
            </div>
          </Teleport>
        </template>

        <template v-else-if="activeTab === 'impression'">
          <div class="link-section">
            <h3 class="sec-title"><span class="sec-dot"></span> 绵城印象</h3>
            <div class="link-grid">
              <div v-for="item in impressionItems" :key="item.title" class="link-card" @click="openLink(item.url)">
                <span class="link-icon">{{ item.icon }}</span>
                <div class="link-text">
                  <strong>{{ item.title }}</strong>
                  <small>了解更多 →</small>
                </div>
              </div>
            </div>
          </div>
          <div class="link-section">
            <h3 class="sec-title"><span class="sec-dot"></span> 专业分院</h3>
            <div class="link-grid">
              <div v-for="item in collegeItems" :key="item.name" class="link-card" @click="openLink(item.url)">
                <span class="link-icon">{{ item.icon }}</span>
                <div class="link-text">
                  <strong>{{ item.name }}</strong>
                  <small>进入官网 →</small>
                </div>
              </div>
            </div>
          </div>
          <div class="link-section">
            <h3 class="sec-title"><span class="sec-dot"></span> 走进城市学院</h3>
            <div class="link-grid">
              <div v-for="item in campusLifeItems" :key="item.title" class="link-card" @click="openLink(item.url)">
                <span class="link-icon">{{ item.icon }}</span>
                <div class="link-text">
                  <strong>{{ item.title }}</strong>
                  <small>了解更多 →</small>
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="activeTab === 'announcements'">
          <div v-if="announcements.length" class="announce-list">
            <a v-for="a in announcements" :key="a.url ?? ''" :href="a.url ?? '#'" target="_blank" class="announce-item">
              <span class="announce-dot"></span>
              <span class="announce-title">{{ a.title }}</span>
              <span class="announce-date">{{ a.date ?? '' }}</span>
            </a>
          </div>
          <el-empty v-else description="暂无公告或获取失败" />
        </template>

        <template v-else-if="activeTab === 'teacher-announcements'">
          <div v-if="tutorAnnouncements.length" class="announce-list">
            <div v-for="a in tutorAnnouncements" :key="a.id" class="tutor-card" @click="showAnnounceDetail(a)">
              <div class="tutor-card-top">
                <el-tag :type="urgencyTag(a.urgency)" size="small" effect="dark" round>{{ urgencyLabel(a.urgency) }}</el-tag>
                <span class="tutor-teacher">{{ a.teacher_name }}</span>
                <span class="tutor-date">{{ new Date(a.created_at).toLocaleString('zh-CN') }}</span>
              </div>
              <div class="tutor-title">{{ a.title }}</div>
              <div class="tutor-content">{{ a.content.slice(0, 120) }}{{ a.content.length > 120 ? '...' : '' }}</div>
              <div v-if="a.attachment_url" class="tutor-attach">
                <a :href="a.attachment_url" target="_blank" @click.stop>📎 下载附件</a>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无班级公告" />
        </template>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getFigures, getAnnouncements } from '@/api/campus'
import type { CampusFigure, Announcement } from '@/types'
import FigureCard from '@/components/campus/FigureCard.vue'
import {
  getStudentAnnouncements, markAnnouncementRead,
  type AnnouncementItem,
} from '@/api/announcement'
import { ElMessageBox } from 'element-plus'
import { Microphone, Mute } from '@element-plus/icons-vue'

interface GalleryImage {
  title: string
  image_url: string
  campus: string
}

const route = useRoute()
const activeTab = ref(route.query.tab === 'announcements' ? 'teacher-announcements' : 'figures')
const figures = ref<CampusFigure[]>([])
const announcements = ref<Announcement[]>([])
const tutorAnnouncements = ref<AnnouncementItem[]>([])
const galleryActive = ref('all')

const tabItems = [
  { key: 'figures', label: '人物风采', icon: '👤' },
  { key: 'sceneries', label: '校园风景', icon: '🏞️' },
  { key: 'impression', label: '绵城印象', icon: '🏛️' },
  { key: 'announcements', label: '校园公告', icon: '📢' },
  { key: 'teacher-announcements', label: '班级公告', icon: '📋' },
]

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

function urgencyTag(u: string) {
  const map: Record<string, string> = { urgent: 'danger', important: 'warning', normal: '' }
  return map[u] || ''
}
function urgencyLabel(u: string) {
  const map: Record<string, string> = { urgent: '紧急', important: '重要', normal: '普通' }
  return map[u] || u
}

async function loadTutorAnnouncements() {
  try {
    tutorAnnouncements.value = await getStudentAnnouncements()
    for (const a of tutorAnnouncements.value) {
      try { await markAnnouncementRead(a.id) } catch { /* ignore */ }
    }
  } catch { /* ignore */ }
}

function showAnnounceDetail(a: AnnouncementItem) {
  ElMessageBox.alert(a.content, a.title, {
    confirmButtonText: '关闭',
    type: a.urgency === 'urgent' ? 'warning' : 'info',
  })
}

onMounted(async () => {
  figures.value = await getFigures() as any
  announcements.value = await getAnnouncements() as any
  loadTutorAnnouncements()
})
</script>

<style scoped>
.campus-page { display: flex; gap: 20px; padding: 4px 0; height: 100%; overflow: hidden; }

/* ===== Sidebar ===== */
.campus-sidebar {
  width: 160px; flex-shrink: 0; display: flex; flex-direction: column; gap: 4px;
  background: #f5f7fa; border-radius: 14px; padding: 6px;
}
.side-btn {
  display: flex; align-items: center; gap: 8px; width: 100%;
  padding: 11px 14px; border: none; border-radius: 10px;
  background: transparent; color: #666; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all .2s; text-align: left;
}
.side-btn:hover { color: #409eff; background: rgba(64,158,255,.06); }
.side-btn.active { background: #fff; color: #409eff; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.side-icon { font-size: 18px; flex-shrink: 0; }

/* ===== Main Content ===== */
.campus-main { flex: 1; min-width: 0; overflow-y: auto; }

/* ===== Tab Transition ===== */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all .2s ease; }
.fade-slide-enter-from { opacity: 0; transform: translateY(8px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-4px); }
.tab-content { min-height: 200px; }

/* ===== Figure Grid ===== */
.figure-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.figure-card { position: relative; }
.teacher-card {
  background: linear-gradient(135deg, #f0f7ff, #e8f4fd);
  border-radius: 14px; padding: 28px 20px; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  border: 1px solid rgba(64,158,255,.1);
  transition: transform .2s, box-shadow .2s;
}
.teacher-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(64,158,255,.15); }
.teacher-card h3 { margin: 0; font-size: 16px; color: #1a1a2e; }
.teacher-badge {
  width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; color: #fff; font-weight: 700;
}
.card-hint { font-size: 12px; color: #409eff; }

/* ===== Video ===== */
.video-section {
  position: relative; border-radius: 16px; overflow: hidden; margin-bottom: 24px;
  box-shadow: 0 8px 30px rgba(0,0,0,.1);
}
.campus-video { width: 100%; display: block; max-height: 460px; object-fit: cover; }
.video-controls {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 50px 20px 14px;
  background: linear-gradient(transparent, rgba(0,0,0,.65));
  display: flex; justify-content: space-between; align-items: flex-end;
}
.video-title { color: #fff; font-size: 17px; font-weight: 600; text-shadow: 0 2px 8px rgba(0,0,0,.5); }
.video-actions { display: flex; align-items: center; gap: 8px; }
.speed-badge {
  font-size: 11px; padding: 2px 10px; border-radius: 10px;
  background: rgba(255,255,255,.2); backdrop-filter: blur(4px);
  color: #fff; font-weight: 600;
}
.mute-btn {
  width: 36px; height: 36px; border-radius: 50%; border: none;
  background: rgba(255,255,255,.15); color: #fff; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px); transition: background .2s;
}
.mute-btn:hover { background: rgba(255,255,255,.3); }

/* ===== Gallery ===== */
.gallery-filter { display: flex; gap: 8px; margin-bottom: 20px; }
.filter-btn {
  padding: 7px 18px; border: 1px solid #e8e8e8; border-radius: 20px;
  background: #fff; color: #666; font-size: 13px; cursor: pointer;
  transition: all .2s;
}
.filter-btn:hover { border-color: #409eff; color: #409eff; }
.filter-btn.active { background: #409eff; color: #fff; border-color: #409eff; }
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.gallery-card {
  position: relative; border-radius: 12px; overflow: hidden; cursor: pointer;
  transition: transform .25s, box-shadow .25s; aspect-ratio: 16 / 10;
}
.gallery-card:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(0,0,0,.15); }
.gallery-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.gallery-overlay {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 40px 14px 10px;
  background: linear-gradient(transparent, rgba(0,0,0,.6));
  display: flex; justify-content: space-between; align-items: flex-end;
  pointer-events: none;
}
.gallery-label { color: #fff; font-size: 14px; font-weight: 600; text-shadow: 0 1px 4px rgba(0,0,0,.4); }
.gallery-campus {
  font-size: 11px; padding: 2px 10px; border-radius: 10px;
  background: rgba(255,255,255,.2); backdrop-filter: blur(4px); color: #fff;
}

/* ===== Preview ===== */
.preview-mask {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,.85); display: flex; align-items: center; justify-content: center;
}
.preview-container { position: relative; display: flex; flex-direction: column; align-items: center; gap: 16px; }
.preview-img { max-width: 90vw; max-height: 78vh; border-radius: 8px; }
.preview-bar { display: flex; align-items: center; gap: 12px; }
.preview-nav {
  width: 40px; height: 40px; border-radius: 50%; border: none;
  background: rgba(255,255,255,.15); color: #fff; font-size: 22px;
  cursor: pointer; transition: background .2s;
}
.preview-nav:hover { background: rgba(255,255,255,.3); }
.preview-nav:disabled { opacity: .3; cursor: default; }
.preview-counter { color: rgba(255,255,255,.7); font-size: 14px; }
.preview-close {
  position: absolute; top: -40px; right: 0; width: 36px; height: 36px;
  border-radius: 50%; border: none; background: rgba(255,255,255,.15);
  color: #fff; font-size: 16px; cursor: pointer;
}

/* ===== Link Sections (impression) ===== */
.link-section { margin-bottom: 28px; }
.sec-title {
  font-size: 16px; font-weight: 600; color: #1a1a2e;
  display: flex; align-items: center; gap: 8px; margin-bottom: 14px;
}
.sec-dot { width: 4px; height: 16px; background: #409eff; border-radius: 2px; }
.link-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
.link-card {
  display: flex; align-items: center; gap: 14px; padding: 16px 18px;
  background: #fff; border-radius: 12px; cursor: pointer;
  border: 1px solid rgba(0,0,0,.04); box-shadow: 0 1px 6px rgba(0,0,0,.02);
  transition: transform .2s, box-shadow .2s;
}
.link-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,.06); }
.link-icon { font-size: 32px; flex-shrink: 0; }
.link-text { display: flex; flex-direction: column; min-width: 0; }
.link-text strong { font-size: 14px; color: #1a1a2e; }
.link-text small { font-size: 12px; color: #999; margin-top: 2px; }

/* ===== Announcements ===== */
.announce-list { display: flex; flex-direction: column; gap: 2px; }
.announce-item {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; text-decoration: none; color: #333;
  border-bottom: 1px solid #f5f5f5; transition: background .2s;
}
.announce-item:hover { background: #f8faff; }
.announce-dot { width: 6px; height: 6px; border-radius: 50%; background: #409eff; flex-shrink: 0; }
.announce-item .announce-title { flex: 1; font-size: 14px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.announce-item .announce-date { font-size: 12px; color: #bbb; flex-shrink: 0; margin-left: 12px; }

/* ===== Tutor Announcements ===== */
.tutor-card {
  padding: 18px 20px; border-radius: 12px; margin-bottom: 12px;
  border: 1px solid rgba(0,0,0,.04); box-shadow: 0 1px 6px rgba(0,0,0,.02);
  cursor: pointer; transition: transform .15s, box-shadow .15s;
}
.tutor-card:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,.06); }
.tutor-card-top { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.tutor-teacher { font-size: 12px; color: #888; }
.tutor-date { font-size: 11px; color: #bbb; margin-left: auto; }
.tutor-title { font-size: 15px; font-weight: 600; color: #1a1a2e; margin-bottom: 6px; }
.tutor-content { font-size: 13px; color: #666; line-height: 1.5; }
.tutor-attach { margin-top: 8px; }
.tutor-attach a { color: #409eff; font-size: 13px; text-decoration: none; }
</style>
