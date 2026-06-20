import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/monitoring'
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: () => import('@/views/Monitoring.vue'),
    meta: { title: '实时监测' }
  },
  {
    path: '/thresholds',
    name: 'Thresholds',
    component: () => import('@/views/Thresholds.vue'),
    meta: { title: '阈值设置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 鱼塘水质监控系统` : '鱼塘水质监控系统'
  next()
})

export default router
