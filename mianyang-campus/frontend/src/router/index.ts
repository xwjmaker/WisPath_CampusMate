import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUser } from '@/utils/token'

const publicPaths = ['/login']

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'Login', component: () => import('@/views/login/LoginPage.vue') },

    {
      path: '/student',
      component: () => import('@/components/layout/StudentLayout.vue'),
      meta: { role: 'student' },
      children: [
        { path: '', component: () => import('@/views/student/HomePage.vue') },
        { path: 'agent', component: () => import('@/views/student/AgentPage.vue') },
        { path: 'campus', component: () => import('@/views/student/CampusPage.vue') },
        { path: 'growth', component: () => import('@/views/student/GrowthPage.vue') },
        { path: 'schedule', component: () => import('@/views/student/SchedulePage.vue') },
        { path: 'grade', redirect: '/student/schedule' },
        { path: 'service', component: () => import('@/views/student/ServicePage.vue') },
      ],
    },
    {
      path: '/teacher',
      component: () => import('@/components/layout/TeacherLayout.vue'),
      meta: { role: 'teacher' },
      children: [
        { path: '', component: () => import('@/views/teacher/HomePage.vue') },
        { path: 'agent', component: () => import('@/views/teacher/AgentPage.vue') },
        { path: 'students', component: () => import('@/views/teacher/StudentsPage.vue') },
        { path: 'approval', component: () => import('@/views/teacher/ApprovalPage.vue') },
        { path: 'messages', component: () => import('@/views/teacher/MessagesPage.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  const token = getToken()
  const user = getUser()
  
  // 未登录跳转登录页
  if (!token && !publicPaths.includes(to.path)) return '/login'
  
  // 已登录但访问登录页，根据角色重定向
  if (token && to.path === '/login') {
    return user?.role === 'teacher' ? '/teacher' : '/student'
  }
  
  // 角色检查
  if (token && user && to.meta.role) {
    // 管理员可访问所有路由
    if (user.role === 'admin') return
    
    // 学生不能访问教师端
    if (user.role === 'student' && to.meta.role === 'teacher') return '/student'
    
    // 教师不能访问学生端
    if (user.role === 'teacher' && to.meta.role === 'student') return '/teacher'
  }
})

export default router
