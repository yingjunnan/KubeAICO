import { createRouter, createWebHistory } from 'vue-router'
import AIView from '../views/AIView.vue'
import AlertsView from '../views/AlertsView.vue'
import DashboardView from '../views/DashboardView.vue'
import LoginView from '../views/LoginView.vue'
import WorkloadsView from '../views/WorkloadsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/workloads', name: 'workloads', component: WorkloadsView, meta: { requiresAuth: true } },
    { path: '/alerts', name: 'alerts', component: AlertsView, meta: { requiresAuth: true } },
    { path: '/ai', name: 'ai', component: AIView, meta: { requiresAuth: true } },
  ],
})

router.beforeEach((to) => {
  const token = localStorage.getItem('kubeaico_token')
  if (to.meta.requiresAuth && !token) {
    return { name: 'login' }
  }
  if (to.name === 'login' && token) {
    return { name: 'dashboard' }
  }
  return true
})

export default router
