<template>
  <div class="immersive-home-layout">
    
    <aside class="control-panel">
      <div class="panel-header">
        <div class="header">
        <h1 class="brand-title">新建画布</h1>
        </div>
        <div class="header-actions">
          <button class="ghost-action" @click="handleCustomCanvas">
            <img src="../assets/icon-custom.svg" class="action-icon" alt="自定义尺寸" />
            自定义尺寸
          </button>
          <button class="ghost-action" @click="handleAction('导入图片')">
            <img src="../assets/icon-import.svg" class="action-icon" alt="导入图片" />
            导入图片
          </button>
        </div>
      </div>

      <div class="preset-menu">
        <h3 class="menu-subtitle">常用预设</h3>
        <ul class="menu-list">
          <li 
            v-for="preset in canvasPresets" 
            :key="preset.id" 
            class="menu-item"
            :class="{ 'is-active': activePreset.id === preset.id }"
            @mouseenter="activePreset = preset"
            @click="selectPreset(preset)"
          >
            <span class="item-label">{{ preset.label }}</span>
            <span class="item-dimension">{{ preset.width }} &times; {{ preset.height }}</span>
          </li>
        </ul>
      </div>
    </aside>

    <main class="dynamic-stage">
      
      <div 
        class="physical-paper" 
        :style="{ aspectRatio: activePreset.ratio }"
      ></div>
      
    </main>
    <ImageImportModal v-model="showImportModal" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBoardStore } from '../stores/boardStore'
import { ElMessage } from 'element-plus'
import ImageImportModal from '../components/common/ImageImportModal.vue'

const router = useRouter()
const store = useBoardStore()

// 预设数据，保持 100% 一致
const canvasPresets = [
  { id: '1:1', label: '1:1 正方', width: 1080, height: 1080, ratio: '1 / 1' },
  { id: '3:4', label: '3:4 社交', width: 1080, height: 1440, ratio: '3 / 4' },
  { id: '4:3', label: '4:3 经典', width: 1080, height: 810, ratio: '4 / 3' },
  { id: '9:16', label: '9:16 竖屏', width: 1080, height: 1920, ratio: '9 / 16' },
  { id: '16:9', label: '16:9 横屏', width: 1080, height: 607, ratio: '16 / 9' },
  { id: 'comic', label: '条漫长图', width: 1080, height: 4320, ratio: '1 / 3' }
]

const activePreset = ref(canvasPresets[3]) 

const selectPreset = (preset) => {
  store.canvasWidth = preset.width
  store.canvasHeight = preset.height
  router.push('/workspace')
}

const showImportModal = ref(false)

const handleCustomCanvas = () => {
  ElMessage.success('自定义画布功能即将上线，默认使用 1080x1920 进入')
  selectPreset({ width: 1080, height: 1920 }) 
}

const handleAction = (name) => {
  if (name === '导入图片') {
    showImportModal.value = true
  } else {
    ElMessage({ message: `${name} 功能正在开发中`, type: 'info', grouping: true })
  }
}
</script>

<style scoped>
/* ==========================================
   全局架构与左侧控制台
========================================== */
.immersive-home-layout {
  width: 100vw;
  height: 100vh;
  display: flex;
  overflow: hidden;
  font-family: 'Inter', 'PingFang SC', 'Helvetica Neue', sans-serif;
  background-color: #000; 
}

.control-panel {
  width: 380px;
  min-width: 320px;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  box-shadow: 12px 0 48px rgba(0, 0, 0, 0.04);
  z-index: 10;
}
/* 
.header{
  text-align:center;
} */

.panel-header {
  padding: 48px 40px 32px 40px;
  border-bottom: 1px solid #F3F4F6;
}

.brand-title {
  font-size: 28px;
  font-weight: 900;
  color: #111827;
  margin: 0 0 32px 0;
  letter-spacing: -0.5px;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ghost-action {
  width: 100%;
  background-color: transparent;
  border: 1.5px solid #111827;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.ghost-action:hover {
  background-color: #111827;
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.ghost-action:active {
  transform: translateY(0);
}

.action-icon {
  width: 20px;
  height: auto;
  transition: filter 0.2s ease;
}

.ghost-action:hover .action-icon {
  filter: brightness(0) invert(1);
}

.preset-menu {
  flex: 1;
  padding: 24px 0;
  overflow-y: auto;
}

.preset-menu::-webkit-scrollbar { width: 0; }

.menu-subtitle {
  font-size: 13px;
  font-weight: 700;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 0 40px;
  margin: 0 0 16px 0;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  position: relative;
  padding: 18px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  color: #6B7280;
  transition: all 0.2s ease;
}

.menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 0;
  background-color: #111827;
  border-radius: 0 4px 4px 0;
  transition: height 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.menu-item:hover {
  background-color: #F9FAFB;
  color: #374151;
}

.menu-item.is-active {
  color: #111827;
  background-color: #F9FAFB;
}

.menu-item.is-active::before {
  height: 60%;
}

.item-label {
  font-size: 15px;
  font-weight: 600;
  transition: font-weight 0.2s;
}

.menu-item.is-active .item-label {
  font-weight: 800;
}

.item-dimension {
  font-family: 'Roboto Mono', monospace;
  font-size: 13px;
  opacity: 0.8;
}

/* ==========================================
   右侧舞台
========================================== */
.dynamic-stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  
  background-color: #F8F9FA; 
  background-image: 
    linear-gradient(to right, rgba(17, 24, 39, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(17, 24, 39, 0.03) 1px, transparent 1px),
    linear-gradient(to right, rgba(17, 24, 39, 0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(17, 24, 39, 0.1) 1px, transparent 1px);
  background-size: 128px 128px, 128px 128px, 32px 32px, 32px 32px;
  background-position: center center;
  
  position: relative;
}

/* 核心画纸：没有任何 transition，绝对的瞬时响应 */
.physical-paper {
  height: 60vh;
  max-width: 80vw; 
  background-color: #ffffff;
  box-shadow: 
    0 48px 100px -24px rgba(17, 24, 39, 0.25), 
    0 16px 40px -12px rgba(17, 24, 39, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;
}
</style>