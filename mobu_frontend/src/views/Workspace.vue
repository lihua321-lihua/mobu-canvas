<template>
  <div class="workspace-layout">
    
    <header class="top-header">
      <div class="header-left">
        <div class="brand-wrapper">
          <img src="../assets/mobu_logo.png" alt="MoBu Logo" class="brand-logo" />
          <span class="brand-name">MoBu Canvas</span>
        </div>
        
        <div class="history-actions pill-container">
          <el-tooltip content="撤销" placement="bottom" :show-after="300">
            <button class="pill-btn" @click="handleUndo">
              <img src="../assets/undo.png" alt="撤销" class="action-icon" />
            </button>
          </el-tooltip>
          
          <el-tooltip content="重做" placement="bottom" :show-after="300">
            <button class="pill-btn" @click="handleRedo">
              <img src="../assets/redo.png" alt="重做" class="action-icon" />
            </button>
          </el-tooltip>

          <div class="pill-divider"></div>
          
          <el-tooltip content="清空图层" placement="bottom" :show-after="300">
            <button class="pill-btn" @click="handleClear">
              <img src="../assets/clear.png" alt="清空" class="action-icon" />
            </button>
          </el-tooltip>
        </div>
      </div>
      
      <div class="header-center">
        <Transition name="header-override" mode="out-in">
          
          <div v-if="!store.isPlacingImage" class="segmented-control">
            <div 
              class="segment-item" 
              :class="{ 'is-active': store.workMode === 'draft' }"
              @click="store.workMode = 'draft'"
            >
              构思线稿
            </div>
            <div 
              class="segment-item" 
              :class="{ 'is-active': store.workMode === 'color' }"
              @click="store.workMode = 'color'"
            >
              氛围铺色
            </div>
            <div 
              class="segment-item" 
              :class="{ 'is-active': store.workMode === 'refine' }"
              @click="store.workMode = 'refine'"
            >
              局部精修
            </div>
          </div>

          <div v-else class="placement-override-bar">
            <div class="pulsing-dot"></div>
            <span class="override-text">正在排版图片，请调整大小与位置</span>
            <button class="finish-btn" @click="store.confirmImagePlacement">
              <svg viewBox="0 0 24 24" class="check-icon"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
              完成
            </button>
          </div>
          
        </Transition>
      </div>

      <div class="header-right">
        <button class="dark-export-btn" @click="handleExport">
          <span>导出作品</span>
        </button>
        <el-tooltip content="设置" placement="bottom">
          <el-button circle size="default" class="light-ghost-btn">
            <el-icon><Setting /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </header>

    <main class="main-workspace">
      <div class="canvas-paper">
        <CanvasBoard ref="canvasBoardRef" />
      </div>

      <div class="floating-panel left-toolbar">
        <LeftToolbar />
      </div>

      <div class="floating-panel right-console" :class="{ 'is-collapsed': store.isAIConsoleCollapsed }">
        <RightPanelContainer /> 
      </div>  
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue' 
import { useBoardStore } from '../stores/boardStore'
import { RefreshLeft, RefreshRight, Delete, Setting } from '@element-plus/icons-vue'
import LeftToolbar from '../components/workspace/left/LeftToolbar.vue'
// import AIConsole from '../components/workspace/right/components/workspace/AIConsole.vue'
import RightPanelContainer from '../components/workspace/right/RightPanelContainer.vue'
import CanvasBoard from '../components/workspace/CanvasBoard.vue'

const store = useBoardStore()
const canvasBoardRef = ref(null)

const handleUndo = async () => {
  store.undo() 
  if (canvasBoardRef.value) {
    if (canvasBoardRef.value.redrawCanvas) {
      canvasBoardRef.value.redrawCanvas()
    }
    await nextTick() 
    if (canvasBoardRef.value.updateThumbnail) {
      canvasBoardRef.value.updateThumbnail() 
    }
  }
}

const handleRedo = async () => {
  store.redo() 
  if (canvasBoardRef.value) {
    if (canvasBoardRef.value.redrawCanvas) {
      canvasBoardRef.value.redrawCanvas()
    }
    await nextTick()
    if (canvasBoardRef.value.updateThumbnail) {
      canvasBoardRef.value.updateThumbnail()
    }
  }
}

const handleClear = async () => {
  store.clearCanvas()
  if (canvasBoardRef.value) {
    if (canvasBoardRef.value.redrawCanvas) {
      canvasBoardRef.value.redrawCanvas()
    }
    await nextTick() 
    if (canvasBoardRef.value.updateThumbnail) {
      canvasBoardRef.value.updateThumbnail()
    }
  }
}

const handleExport = () => {
  if (canvasBoardRef.value) canvasBoardRef.value.exportImage()
}
</script>

<style scoped>
/* ================== 全局画布底噪 ================== */
.workspace-layout { 
  width: 100vw; 
  height: 100vh; 
  overflow: hidden; 
  display: flex; 
  flex-direction: column; 
  background-color: #F8F9FA; 
  background-image: 
    linear-gradient(to right, rgba(17, 24, 39, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(17, 24, 39, 0.03) 1px, transparent 1px),
    linear-gradient(to right, rgba(17, 24, 39, 0.1) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(17, 24, 39, 0.1) 1px, transparent 1px);
  background-size: 128px 128px, 128px 128px, 32px 32px, 32px 32px;
  background-position: center center;
  color: #374151; 
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
}

/* ================== 顶部导航栏 (Header) ================== */
.top-header { 
  height: 64px; 
  flex-shrink: 0; 
  background-color: rgba(255, 255, 255, 0.85); 
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  padding: 0 24px; 
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.03); 
  z-index: 100; 
  border-bottom: 1px solid rgba(229, 231, 235, 0.5); 
}

/* ================= 左侧：品牌与操作栏 ================= */
.header-left { display: flex; align-items: center; gap: 32px; width: 340px; }

.brand-wrapper { display: flex; align-items: center; gap: 10px; cursor: default; }
.brand-logo { width: 32px; height: 32px; object-fit: contain; }
.brand-name { font-size: 18px; font-weight: 800; color: #111827; letter-spacing: -0.5px; white-space: nowrap; }

.pill-container { display: flex; align-items: center; gap: 4px; }
.pill-btn { 
  width: 40px; 
  height: 40px; 
  background: transparent; 
  border: none; 
  border-radius: 12px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  cursor: pointer; 
  transition: all 0.2s ease; 
  outline: none; 
}
.pill-btn:hover { background-color: #F3F4F6; }
.action-icon { 
  width: 25px; 
  height: 25px; 
  object-fit: contain; 
  opacity: 0.65; 
  transition: opacity 0.2s; 
}
.pill-btn:hover .action-icon { opacity: 1; }
.pill-divider { width: 1px; height: 16px; background-color: #E5E7EB; margin: 0 4px; }

/* ================= 中间：模式切换器 & 劫持区 ================= */
.header-center { flex: 1; display: flex; justify-content: center; align-items: center; }

.segmented-control { 
  display: flex; 
  align-items: center; 
  background-color: #F3F4F6; 
  border-radius: 12px; 
  padding: 4px; 
  gap: 4px; 
  border: 1px solid #E5E7EB; 
}
.segment-item { 
  padding: 8px 24px; 
  font-size: 15px; 
  letter-spacing: 1px; 
  color: #6B7280; 
  border-radius: 8px; 
  cursor: pointer; 
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); 
  user-select: none; 
}
.segment-item:hover:not(.is-active) { color: #374151; background-color: rgba(229, 231, 235, 0.6); }
.segment-item.is-active { 
  background-color: #FFFFFF; 
  color: #111827; 
  font-weight: bold; 
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05), 0 0 1px rgba(0, 0, 0, 0.1); 
}

/* --- ✨ 排版劫持状态的极简 UI --- */
.placement-override-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background-color: #F9FAFB;
  border: 1px solid #E5E7EB;
  padding: 4px 6px 4px 16px;
  border-radius: 9999px;
  height: 44px; /* 保持与三大模式的高度一致感 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.pulsing-dot {
  width: 8px;
  height: 8px;
  background-color: #3B82F6; 
  border-radius: 50%;
  animation: pulse-dot 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.85); }
}

.override-text {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-right: 8px;
  letter-spacing: 0.5px;
}

.finish-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: #111827;
  color: #ffffff;
  border: none;
  border-radius: 9999px;
  padding: 6px 18px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.finish-btn:hover {
  background-color: #374151;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.finish-btn:active {
  transform: translateY(0);
}

.check-icon {
  width: 16px;
  height: 16px;
}

/* --- 丝滑替换的过渡动画 --- */
.header-override-enter-active,
.header-override-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.header-override-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

.header-override-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* ================= 右侧：导出与设置 ================= */
.header-right { display: flex; align-items: center; justify-content: flex-end; gap: 16px; width: 340px; }

.dark-export-btn { 
  background-color: #111827; 
  color: #FFFFFF; 
  border: none; 
  border-radius: 100px; 
  padding: 10px 24px; 
  font-size: 14px; 
  font-weight: 600; 
  letter-spacing: 1px; 
  cursor: pointer; 
  box-shadow: 0 4px 12px rgba(17, 24, 39, 0.15); 
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); 
}
.dark-export-btn:hover { 
  background-color: #1F2937; 
  transform: translateY(-1px); 
  box-shadow: 0 6px 16px rgba(17, 24, 39, 0.25); 
}
.dark-export-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(17, 24, 39, 0.15);
}

.light-ghost-btn { background-color: transparent !important; border: 1px solid transparent !important; color: #6B7280 !important; transition: all 0.2s; }
.light-ghost-btn:hover { background-color: #F3F4F6 !important; color: #374151 !important; border-color: #E5E7EB !important; }

/* ================== 下方主体面板 ================== */
.main-workspace { flex: 1; position: relative; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.canvas-paper { width: 100%; height: 100%; background-color:transparent ; display: flex; align-items: center; justify-content: center; overflow: hidden;}
.floating-panel { position: absolute; background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid #E5E7EB; border-radius: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04); display: flex; align-items: center; justify-content: center; z-index: 50; }

.left-toolbar { left: 20px; top: 50%; transform: translateY(-50%); width: 54px; flex-direction: column; }
.right-console { right: 20px; top: 20px; bottom: 20px; width: 320px; transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
.right-console.is-collapsed { transform: translateX(340px); }
</style>