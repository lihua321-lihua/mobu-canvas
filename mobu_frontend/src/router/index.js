import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Home from '../views/Home.vue'
import Workspace from '../views/Workspace.vue'

const routes = [
  { 
    path: '/', 
    name: 'Landing', 
    component: HomeView,
    meta: { 
      title: '首页 - MoBu Canvas' 
    }
  },
  {
    // 🌟 新增：登录与注册通道
    path: '/login',
    name: 'Login',
    component: () => import('../views/SigninOrRegister.vue'), // 采用路由懒加载，不拖慢首页加载速度
    meta: {
      title: '登录 / 注册 - MoBu',
      requiresGuest: true // 标识：只有“访客”状态才能进入
    }
  },
  { 
    path: '/home', 
    name: 'SizeSelection', 
    component: Home,
    meta: {
      title: '选择画板尺寸 - MoBu',
      requiresAuth: true // 标识：必须登录才能进入
    }
  },
  { 
    path: '/workspace', 
    name: 'Workspace', 
    component: Workspace,
    meta: {
      title: '创作空间 - MoBu',
      requiresAuth: true // 标识：必须登录才能进入
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ==========================================
// 🛡️ 顶级工程师的防御塔：全局路由守卫
// ==========================================
router.beforeEach((to, from, next) => {
  // 1. 动态切换浏览器标签页的标题，提升交互细节
  if (to.meta.title) {
    document.title = to.meta.title
  }

  // 2. 从本地存储中探查 Token（在 SigninOrRegister 登录成功时存入的）
  const token = localStorage.getItem('mobu_token')

  // 3. 核心拦截逻辑
  if (to.meta.requiresAuth && !token) {
    // 🚨 场景 A：想白嫖进入核心区 (SizeSelection 或 Workspace)，但没登录
    console.warn('拦截：未授权访问，正在打回登录页！')
    next({ name: 'Login' })
  } 
  else if (to.meta.requiresGuest && token) {
    // 🛡️ 场景 B：已经登录了，却试图手动退回登录页面
    console.info('拦截：已登录用户无需再次登录，放行至首页。')
    next({ name: 'Landing' })
  } 
  else {
    // ✅ 场景 C：合法访问，直接放行
    next()
  }
})

export default router