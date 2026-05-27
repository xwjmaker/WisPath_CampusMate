<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-left" style="cursor:pointer" @click="goTo('/student')">
        <img src="/images/校徽.png" class="topbar-badge" />
        <span class="logo">绵小城</span>
        <span class="logo-divider"></span>
        <span class="motto">博学、笃行、严谨、创新</span>
      </div>
      <div class="topbar-right">
        <el-tooltip content="AI 对话" placement="bottom">
          <el-button text circle @click="goTo('/student')">
            <el-icon :size="18"><ChatDotRound /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="校园风采" placement="bottom">
          <el-button text circle @click="goTo('/student/campus')">
            <el-icon :size="18"><PictureFilled /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="成长轨迹" placement="bottom">
          <el-button text circle @click="goTo('/student/growth')">
            <el-icon :size="18"><TrendCharts /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="课表查询" placement="bottom">
          <el-button text circle @click="goTo('/student/schedule')">
            <el-icon :size="18"><Calendar /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="办事服务" placement="bottom">
          <el-button text circle @click="goTo('/student/service')">
            <el-icon :size="18"><Service /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="联系辅导员" placement="bottom">
          <el-button text circle @click="showContact = true" style="position:relative">
            <el-icon :size="18"><Message /></el-icon>
            <el-badge v-if="unreadCount" :value="unreadCount" :hidden="!unreadCount" class="contact-badge" />
          </el-button>
        </el-tooltip>
        <el-divider direction="vertical" />
        <el-dropdown trigger="click">
          <span class="user-btn">
            <el-avatar :size="28" :src="auth.user?.avatar || ''">{{ auth.userName?.[0] }}</el-avatar>
            <span class="user-name">{{ auth.userName }}</span>
          </span>
          <template #dropdown>
            <el-dropdown-item @click="openProfile">
              <el-icon style="margin-right:6px"><User /></el-icon>个人资料
            </el-dropdown-item>
            <el-dropdown-item divided @click="logout">
              <el-icon style="margin-right:6px"><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </template>
        </el-dropdown>
      </div>
    </header>
    <main class="main-area">
      <router-view />
    </main>

    <el-dialog v-model="showProfile" title="个人资料" width="560px" :close-on-click-modal="false">
      <div class="profile-layout">
        <div class="profile-avatar-col">
          <div class="avatar-upload-wrap" @click="triggerFileInput">
            <el-avatar :size="120" :src="profileForm.avatar" shape="square" class="profile-avatar">
              {{ profileForm.name?.[0] || '?' }}
            </el-avatar>
            <div class="avatar-overlay">
              <el-icon :size="24"><CameraFilled /></el-icon>
              <span>更换头像</span>
            </div>
          </div>
          <input ref="fileInputRef" type="file" accept="image/*" style="display:none" @change="onFileSelect" />
        </div>
        <div class="profile-form-col">
          <el-form :model="profileForm" label-width="90px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="学号"><el-input v-model="profileForm.username" disabled /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="姓名"><el-input v-model="profileForm.name" disabled /></el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="性别">
                  <el-select v-model="profileForm.gender" placeholder="请选择" style="width:100%">
                    <el-option label="男" value="男" />
                    <el-option label="女" value="女" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="年龄">
                  <el-input-number v-model="profileForm.age" :min="1" :max="120" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="学院"><el-input v-model="profileForm.college" disabled /></el-form-item>
            <el-form-item label="政治面貌">
              <el-select v-model="profileForm.political_status" placeholder="请选择" style="width:100%">
                <el-option label="中共党员" value="dangyuan" />
                <el-option label="中共预备党员" value="yubei" />
                <el-option label="共青团员" value="tuanyuan" />
                <el-option label="群众" value="qunzhong" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="职称"><el-input v-model="profileForm.title" placeholder="职称/职务" /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="所属单位"><el-input v-model="profileForm.department" placeholder="所属单位" /></el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="籍贯"><el-input v-model="profileForm.hometown" placeholder="籍贯" /></el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系电话"><el-input v-model="profileForm.phone" placeholder="手机号" /></el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="辅导员">
              <div v-if="profileForm.tutor_id && tutorName" class="tutor-display">
                <el-tag type="success" size="large">{{ tutorName }}</el-tag>
                <span class="tutor-hint">辅导员已绑定，如需变更请联系管理员</span>
              </div>
              <el-select v-else v-model="profileForm.tutor_id" placeholder="搜索选择辅导员" filterable style="width:100%">
                <el-option v-for="t in teachers" :key="t.id" :label="`${t.name}（${t.username}）`" :value="t.id" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <el-button @click="showProfile = false">取消</el-button>
        <el-button type="primary" @click="handleSaveProfile" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCrop" title="裁剪头像" width="420px" :close-on-click-modal="false" @opened="onCropDialogOpened">
      <div class="crop-container">
        <img ref="cropImgRef" style="max-width:100%;display:block" />
      </div>
      <template #footer>
        <el-button @click="cancelCrop">取消</el-button>
        <el-button type="primary" @click="handleCropConfirm">确认裁剪</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="showContact" title="联系辅导员" size="400px" @open="onContactOpen">
      <StudentContactPanel :key="contactKey" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { updateProfile, getTeachers } from '@/api/user'
import { uploadFile } from '@/api/upload'
import { ElMessage } from 'element-plus'
import StudentContactPanel from '@/components/chat/StudentContactPanel.vue'
import { getConversations } from '@/api/messages'
import Cropper from 'cropperjs'
import { ChatDotRound, PictureFilled, TrendCharts, Calendar, Service, Message, User, SwitchButton, CameraFilled } from '@element-plus/icons-vue'

const router = useRouter()
const auth = useAuthStore()

const showProfile = ref(false)
const saving = ref(false)
const fileInputRef = ref<HTMLInputElement>()
const showCrop = ref(false)
const cropImgRef = ref<HTMLImageElement>()
let cropper: Cropper | null = null
let pendingImageSrc = ''
const teachers = ref<any[]>([])
const showContact = ref(false)
const contactKey = ref(0)
function onContactOpen() { contactKey.value++ }
const unreadCount = ref(0)

async function pollUnread() {
  try {
    const convs: any[] = await getConversations()
    unreadCount.value = convs.reduce((sum: number, c: any) => sum + (c.unread_count ?? 0), 0)
  } catch {}
}

const tutorName = computed(() => {
  const t = teachers.value.find(t => t.id === profileForm.tutor_id)
  return t ? `${t.name}（${t.username}）` : ''
})

const profileForm = reactive({
  username: '', name: '', college: '', role: '',
  avatar: '', gender: '', age: 18, political_status: '',
  title: '', hometown: '', phone: '', department: '',
  tutor_id: null as number | null,
})

onMounted(async () => {
  try {
    teachers.value = await getTeachers()
  } catch {}
  pollUnread()
  setInterval(pollUnread, 15000)
})

function goTo(path: string) { router.push(path) }

function logout() {
  auth.logout()
  router.push('/')
}

function openProfile() {
  const u = auth.user
  if (!u) return
  profileForm.username = u.username
  profileForm.name = u.name
  profileForm.college = u.college || ''
  profileForm.role = u.role
  profileForm.avatar = u.avatar || ''
  profileForm.gender = u.gender || ''
  profileForm.age = u.age ?? 18
  profileForm.political_status = u.political_status || ''
  profileForm.title = u.title || ''
  profileForm.hometown = u.hometown || ''
  profileForm.phone = u.phone || ''
  profileForm.department = u.department || ''
  profileForm.tutor_id = u.tutor_id ?? null
  showProfile.value = true
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input?.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    pendingImageSrc = ev.target?.result as string
    showCrop.value = true
  }
  reader.readAsDataURL(file)
  input.value = ''
}

function onCropDialogOpened() {
  const img = cropImgRef.value
  if (!img || !pendingImageSrc) return
  img.src = pendingImageSrc
  const start = () => {
    if (cropper) { cropper.destroy(); cropper = null }
    cropper = new Cropper(img, { aspectRatio: 1, viewMode: 1, dragMode: 'move', minCropBoxWidth: 100 })
  }
  if (img.complete) { start() } else { img.onload = start }
}

function cancelCrop() {
  showCrop.value = false
  if (cropper) { cropper.destroy(); cropper = null }
}

async function handleCropConfirm() {
  if (!cropper) return
  const canvas = cropper.getCroppedCanvas({ width: 200, height: 200 })
  if (!canvas) { ElMessage.error('裁剪失败'); return }
  const blob = await new Promise<Blob | null>((r) => canvas.toBlob((b) => r(b), 'image/jpeg', 0.9))
  if (!blob) { ElMessage.error('裁剪失败'); return }
  const file = new File([blob], 'avatar.jpg', { type: 'image/jpeg' })
  try {
    const result: any = await uploadFile(file)
    profileForm.avatar = result.url
    showCrop.value = false
    if (cropper) { cropper.destroy(); cropper = null }
    ElMessage.success('头像已上传')
  } catch {
    ElMessage.error('头像上传失败')
  }
}

async function handleSaveProfile() {
  saving.value = true
  try {
    const updated = await updateProfile({
      avatar: profileForm.avatar || null,
      gender: profileForm.gender || null,
      age: profileForm.age || null,
      political_status: profileForm.political_status || null,
      title: profileForm.title || null,
      hometown: profileForm.hometown || null,
      phone: profileForm.phone || null,
      department: profileForm.department || null,
      tutor_id: profileForm.tutor_id || null,
    })
    auth.updateUser(updated as any)
    ElMessage.success('保存成功')
    showProfile.value = false
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.app-shell { display: flex; flex-direction: column; height: 100vh; background: #fff; }
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; height: 56px; border-bottom: 1px solid #e8e8e8;
  background: #fff; flex-shrink: 0; z-index: 100;
}
.topbar-left { display: flex; align-items: center; gap: 8px; }
.topbar-badge { height: 32px; width: auto; border-radius: 4px; }
.logo { font-size: 20px; font-weight: 700; color: #409eff; letter-spacing: 1px; }
.logo-divider { width: 1px; height: 20px; background: #ddd; margin: 0 6px; }
.motto {
  font-size: 14px; font-weight: 600;
  background: linear-gradient(135deg, #c41d7f, #e8a020);
  background-clip: text; -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 4px;
}
.topbar-right { display: flex; align-items: center; gap: 4px; }
.user-btn { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 4px 8px; border-radius: 8px; }
.user-btn:hover { background: #f5f5f5; }
.user-name { font-size: 14px; color: #333; }
.main-area { flex: 1; overflow-y: auto; }

.profile-layout { display: flex; gap: 28px; }
.profile-avatar-col { display: flex; flex-direction: column; align-items: center; flex-shrink: 0; padding-top: 12px; }
.avatar-upload-wrap { position: relative; cursor: pointer; border-radius: 8px; overflow: hidden; width: 120px; height: 120px; }
.avatar-upload-wrap .profile-avatar { width: 120px !important; height: 120px !important; font-size: 40px; }
.avatar-overlay {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 6px;
  background: rgba(0,0,0,0.5); color: #fff; font-size: 13px;
  opacity: 0; transition: opacity 0.2s;
}
.avatar-upload-wrap:hover .avatar-overlay { opacity: 1; }
.crop-container { max-height: 360px; overflow: hidden; }
.tutor-display { display: flex; align-items: center; gap: 12px; }
.tutor-hint { font-size: 12px; color: #999; }
.contact-badge { position: absolute; top: 4px; right: 4px; }
</style>