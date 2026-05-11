<template>
  <div class="shape-panel">
    
    <div class="shape-grid">
      <el-tooltip content="直线" placement="top" :show-after="300">
        <button class="shape-btn" :class="{ 'is-active': store.activeShape === 'line' }" @click="selectShape('line')">
          <svg viewBox="0 0 24 24" class="svg-icon"><line x1="4" y1="20" x2="20" y2="4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </el-tooltip>

      <el-tooltip content="圆形" placement="top" :show-after="300">
        <button class="shape-btn" :class="{ 'is-active': store.activeShape === 'circle' }" @click="selectShape('circle')">
          <svg viewBox="0 0 24 24" class="svg-icon"><circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="2" fill="none"/></svg>
        </button>
      </el-tooltip>

      <el-tooltip content="矩形" placement="top" :show-after="300">
        <button class="shape-btn" :class="{ 'is-active': store.activeShape === 'square' }" @click="selectShape('square')">
          <svg viewBox="0 0 24 24" class="svg-icon"><rect x="5" y="5" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" rx="1"/></svg>
        </button>
      </el-tooltip>

      <el-tooltip content="多边形" placement="top" :show-after="300">
        <button class="shape-btn" :class="{ 'is-active': store.activeShape === 'polygon' }" @click="selectShape('polygon')">
          <svg viewBox="0 0 24 24" class="svg-icon"><polygon points="12,3 20,7.5 20,16.5 12,21 4,16.5 4,7.5" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/></svg>
        </button>
      </el-tooltip>
    </div>

    <div class="polygon-ctrl" v-if="store.activeShape === 'polygon'">
      <span class="ctrl-label">边数：</span>
      <el-input-number 
        v-model="store.polygonSides" 
        :min="3" 
        :max="12" 
        size="small" 
        controls-position="right"
        class="light-stepper"
      />
    </div>

  </div>
</template>

<script setup>
import { useBoardStore } from '../../../../stores/boardStore'

const store = useBoardStore()

const selectShape = (shape) => {
  store.activeShape = shape
  store.activeTool = 'shape' 
}
</script>

<style scoped>
.shape-panel { display: flex; flex-direction: column; padding: 4px; }
.shape-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; } 

/* ✨ 亮色形状按钮 */
.shape-btn { aspect-ratio: 1 / 1; border-radius: 8px; background-color: #F9FAFB; border: 1px solid #E5E7EB; color: #6B7280; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); padding: 0; outline: none; }
.shape-btn:hover { background-color: #F3F4F6; color: #374151; }
.shape-btn.is-active { background-color: rgba(20, 184, 166, 0.1); border-color: #14B8A6; color: #0F766E; }

.svg-icon { width: 22px; height: 22px; }
.polygon-ctrl { margin-top: 14px; padding-top: 12px; border-top: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: space-between; animation: slideDown 0.2s ease-out; }
.ctrl-label { font-size: 12px; color: #6B7280; font-weight: bold; }

/* ✨ 亮色步进器 */
:deep(.light-stepper) { width: 90px; }
:deep(.light-stepper .el-input__wrapper) { background-color: #F9FAFB; box-shadow: 0 0 0 1px #E5E7EB inset; }
:deep(.light-stepper .el-input__inner) { color: #374151; font-size: 13px; }
:deep(.light-stepper .el-input-number__increase), :deep(.light-stepper .el-input-number__decrease) { background-color: #F3F4F6; border-color: #E5E7EB; color: #6B7280; }
:deep(.light-stepper .el-input-number__increase:hover), :deep(.light-stepper .el-input-number__decrease:hover) { color: #14B8A6; }

@keyframes slideDown { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
</style>