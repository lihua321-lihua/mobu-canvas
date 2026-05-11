<template>
  <div class="hand-panel" @click="store.activeTool = 'hand'">
    
    <div class="param-row">
      <span class="param-label">旋转(度)</span>
      <el-slider 
        v-model="store.stageRotation" 
        :min="-180" 
        :max="180" 
        :show-tooltip="false"
        class="light-slider" 
      />
      <el-input-number 
        v-model="store.stageRotation" 
        :min="-180" 
        :max="180" 
        size="small" 
        controls-position="right"
        class="light-stepper param-input"
      />
    </div>

    <div class="action-row">
      <el-button size="small" class="light-btn" @click="resetView">
        复位视图 (Reset)
      </el-button>
    </div>

  </div>
</template>

<script setup>
import { useBoardStore } from '../../../../stores/boardStore'
const store = useBoardStore()

const resetView = () => {
  store.stageX = 0
  store.stageY = 0
  store.stageScale = 1
  store.stageRotation = 0
}
</script>

<style scoped>
.hand-panel { padding: 4px; display: flex; flex-direction: column; cursor: default; gap: 16px; }
.param-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.param-label { font-size: 12px; color: #6B7280; width: 50px; text-align: right; flex-shrink: 0; }
.param-input { width: 60px !important; flex-shrink: 0; }
.action-row { text-align: center; }

/* ✨ 复用亮色样式 */
:deep(.light-slider) { flex: 1; }
:deep(.light-slider .el-slider__runway) { background-color: #E5E7EB; height: 4px; }
:deep(.light-slider .el-slider__bar) { background-color: #14B8A6; height: 4px; }
:deep(.light-slider .el-slider__button) { border: 2px solid #14B8A6; background-color: #FFFFFF; width: 14px; height: 14px; }

:deep(.light-stepper .el-input__wrapper) { background-color: #F9FAFB; box-shadow: 0 0 0 1px #E5E7EB inset; padding: 0 24px 0 8px; }
:deep(.light-stepper .el-input__inner) { color: #374151; font-size: 12px; text-align: center; }
:deep(.light-stepper .el-input-number__increase), 
:deep(.light-stepper .el-input-number__decrease) { background-color: #F3F4F6; border-color: #E5E7EB; color: #6B7280; width: 20px; }
:deep(.light-stepper .el-input-number__increase:hover), 
:deep(.light-stepper .el-input-number__decrease:hover) { color: #14B8A6; }

.light-btn { background-color: #F9FAFB; border: 1px solid #E5E7EB; color: #4B5563; transition: all 0.2s; width: 100%; font-size: 13px; }
.light-btn:hover { background-color: #F3F4F6; color: #111827; border-color: #D1D5DB; }
</style>