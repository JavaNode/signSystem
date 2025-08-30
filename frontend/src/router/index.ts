import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/admin'
  },
  // 1. 管理端界面 (PC端)
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/AdminDashboard.vue'),
    meta: { title: '管理端 - 联盟杯内训师大赛' }
  },
  // 2. 用户移动签到端 (手机端)
  {
    path: '/mobile/checkin',
    name: 'MobileCheckin',
    component: () => import('@/views/MobileCheckin.vue'),
    meta: { title: '参赛者签到' }
  },
  // 3. 评委移动打分端 (手机/平板端)
  {
    path: '/judge/score',
    name: 'JudgeScore',
    component: () => import('@/views/JudgeScore.vue'),
    meta: { title: '评委打分' }
  },
  // 4. 会议大屏签到展示端 (大屏幕)
  {
    path: '/display/checkin',
    name: 'DisplayCheckin',
    component: () => import('@/views/DisplayCheckin.vue'),
    meta: { title: '签到大屏展示' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  if (to.meta?.title) {
    document.title = to.meta.title as string
  }
  next()
})

export default router