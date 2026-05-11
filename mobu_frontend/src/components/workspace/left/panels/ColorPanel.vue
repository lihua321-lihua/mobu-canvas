<template>
  <div class="color-panel" @click="store.activeTool = 'brush'">
    
    <div class="color-picker-wrapper">
      <div class="current-color-preview" :style="{ backgroundColor: store.brushColor }"></div>
      <div class="picker-action">
        <span class="picker-hint">点击右侧开启高级色盘 ➔</span>
        <el-color-picker v-model="store.brushColor" color-format="hex" show-alpha />
      </div>
    </div>

    <div class="divider"></div>

    <div class="color-toolbar">
      <el-button size="small" class="light-btn eyedropper-btn" @click="pickColor" :disabled="!isEyeDropperSupported">
        <el-icon><Aim /></el-icon> 吸取颜色
      </el-button>
      
      <el-input 
        v-model="store.brushColor" 
        size="small" 
        class="hex-input light-input" 
        placeholder="#HEX" 
      />
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Aim } from '@element-plus/icons-vue'
import { useBoardStore } from '../../../../stores/boardStore'

const store = useBoardStore()

const isEyeDropperSupported = computed(() => 'EyeDropper' in window)

const pickColor = async () => {
  if (!isEyeDropperSupported.value) return
  
  try {
    const eyeDropper = new window.EyeDropper()
    const result = await eyeDropper.open()
    store.brushColor = result.sRGBHex 
    store.activeTool = 'brush'
  } catch (e) {
    console.log('吸取颜色已取消')
  }
}
</script>

<style scoped>
.color-panel { display: flex; flex-direction: column; padding: 4px; cursor: default; }
.color-picker-wrapper { display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px; }
.current-color-preview { width: 100%; height: 40px; border-radius: 6px; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.1); transition: background-color 0.2s; }
.picker-action { display: flex; justify-content: space-between; align-items: center; }
.picker-hint { font-size: 12px; color: #9CA3AF; }
.divider { height: 1px; background-color: #E5E7EB; margin: 0 0 12px 0; }
.color-toolbar { display: flex; justify-content: space-between; align-items: center; gap: 10px; }

/* ✨ 亮色按钮 */
.light-btn { background-color: #F9FAFB; border: 1px solid #E5E7EB; color: #4B5563; flex-shrink: 0; transition: all 0.2s; }
.light-btn:hover { background-color: #F3F4F6; color: #111827; border-color: #D1D5DB; }
.light-btn.is-disabled { opacity: 0.5; cursor: not-allowed; }
.hex-input { width: 90px; }

/* ✨ 亮色输入框 */
:deep(.light-input .el-input__wrapper) { background-color: #F9FAFB; box-shadow: 0 0 0 1px #E5E7EB inset; }
:deep(.light-input .el-input__inner) { color: #374151; font-size: 12px; text-transform: uppercase; font-family: monospace; }
</style>