<template>
  <div class="eraser-panel" @click="store.activeTool = 'eraser'">
    <div class="param-row">
      <span class="param-label">大小</span>
      <el-slider 
        v-model="store.eraserSize" 
        :min="1" 
        :max="100" 
        :show-tooltip="false"
        class="light-slider custom-black-slider" 
      />
      <el-input-number 
        v-model="store.eraserSize" 
        :min="1" 
        :max="100" 
        size="small" 
        controls-position="right"
        class="light-stepper param-input custom-black-stepper"
      />
    </div>

    <div class="param-row" style="margin-top: 12px;" v-if="store.workMode !== 'refine'">
      <span class="param-label" style="letter-spacing: 0;">不透明度</span>
      <el-slider 
        v-model="store.eraserOpacity" 
        :min="1" 
        :max="100" 
        :show-tooltip="false"
        class="light-slider custom-black-slider" 
      />
      <el-input-number 
        v-model="store.eraserOpacity" 
        :min="1" 
        :max="100" 
        size="small" 
        controls-position="right"
        class="light-stepper param-input custom-black-stepper"
      />
    </div>
  </div>
</template>

<script setup>
import { useBoardStore } from '../../../../stores/boardStore'
const store = useBoardStore()
</script>

<style scoped>
.eraser-panel { padding: 4px; display: flex; flex-direction: column; cursor: default; }
.param-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.param-label { font-size: 12px; color: #6B7280; width: 50px; text-align: right; flex-shrink: 0; }
.param-input { width: 60px !important; flex-shrink: 0; }

/* ✨ 全面黑白灰化：抹除原有的水鸭青，替换为深岩黑 */
:deep(.light-slider) { flex: 1; }
:deep(.custom-black-slider .el-slider__runway) { background-color: #E5E7EB; height: 4px; }
:deep(.custom-black-slider .el-slider__bar) { background-color: #111827; height: 4px; }
:deep(.custom-black-slider .el-slider__button) { border: 2px solid #111827; background-color: #FFFFFF; width: 14px; height: 14px; transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
:deep(.custom-black-slider .el-slider__button:hover) { transform: scale(1.2); }

:deep(.light-stepper .el-input__wrapper) { background-color: #F9FAFB; box-shadow: 0 0 0 1px #E5E7EB inset; padding: 0 24px 0 8px; transition: all 0.2s; }
:deep(.light-stepper .el-input__wrapper.is-focus) { box-shadow: 0 0 0 1px #111827 inset; }
:deep(.light-stepper .el-input__inner) { color: #374151; font-size: 12px; text-align: center; }
:deep(.custom-black-stepper .el-input-number__increase), 
:deep(.custom-black-stepper .el-input-number__decrease) { background-color: #F3F4F6; border-color: #E5E7EB; color: #6B7280; width: 20px; transition: all 0.2s; }
:deep(.custom-black-stepper .el-input-number__increase:hover), 
:deep(.custom-black-stepper .el-input-number__decrease:hover) { color: #111827; background-color: #E5E7EB; }
</style>