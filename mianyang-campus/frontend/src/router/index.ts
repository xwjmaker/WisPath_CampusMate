import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/token'

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
        { path: 'grade', component: () => import('@/views/student/GradePage.vue') },
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
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  if (!getToken() && !publicPaths.includes(to.path)) return '/login'
})

export default router
