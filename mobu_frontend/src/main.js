import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router' // 引入路由
import ElementPlus from 'element-plus' // 引入 Element Plus
import 'element-plus/dist/index.css' // 引入 Element 样式
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // 引入图标
import VueKonva from 'vue-konva'

import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.use(VueKonva)
app.mount('#app')