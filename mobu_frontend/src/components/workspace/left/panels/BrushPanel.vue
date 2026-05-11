<template>
  <div class="brush-panel" @click="store.activeTool = 'brush'">
    
    <div class="param-section">
      <div class="param-row">
        <span class="param-label">大小</span>
        <el-slider 
          v-model="store.brushSize" 
          :min="1" 
          :max="100" 
          :show-tooltip="false"
          class="light-slider" 
        />
        <el-input-number 
          v-model="store.brushSize" 
          :min="1" 
          :max="100" 
          size="small" 
          controls-position="right"
          class="light-stepper param-input"
        />
      </div>

      <div class="param-row">
        <span class="param-label" style="letter-spacing: 0;">不透明度</span>
        <el-slider 
          v-model="store.brushOpacity" 
          :min="1" 
          :max="100" 
          :show-tooltip="false"
          class="light-slider" 
        />
        <el-input-number 
          v-model="store.brushOpacity" 
          :min="1" 
          :max="100" 
          size="small" 
          controls-position="right"
          class="light-stepper param-input"
        />
      </div>
    </div>

    <div class="divider"></div>

    <div class="brush-grid">
      <div 
        v-for="brush in brushList" 
        :key="brush.id"
        class="brush-card"
        :class="{ 'is-active': store.activeBrush === brush.id }"
        @click="selectBrush(brush.id)"
      >
        <div class="brush-thumb">
          <div class="thumb-placeholder"></div>
        </div>
        <span class="brush-name">{{ brush.name }}</span>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useBoardStore } from '../../../../stores/boardStore'
import { ElMessage } from 'element-plus'

const store = useBoardStore()

const brushList = [
  { id: 'pencil', name: '铅笔' },
  { id: 'willow', name: '柳叶毛笔' }, 
  { id: 'airbrush', name: '喷笔' },
  { id: 'marker', name: '马克笔' },
  { id: 'watercolor', name: '水彩笔' },
  { id: 'crayon', name: '蜡笔' },
  { id: 'charcoal', name: '碳笔' },
  { id: 'brush', name: '毛刷' }
]

const selectBrush = (id) => {
  store.activeBrush = id
  store.activeTool = 'brush'
  
  if (id !== 'pencil' && id !== 'willow') {
    ElMessage({ message: `「${brushList.find(b=>b.id===id).name}」笔刷算法正在研发中，当前默认采用铅笔质感`, type: 'info', grouping: true })
  }
}
</script>

<style scoped>
.brush-panel { display: flex; flex-direction: column; padding: 4px; cursor: default; }
.param-section { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
.param-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.param-label { font-size: 12px; color: #6B7280; width: 50px; text-align: right; flex-shrink: 0; }
.param-input { width: 60px !important; flex-shrink: 0; }

/* ✨ 亮色滑块 */
:deep(.light-slider) { flex: 1; }
:deep(.light-slider .el-slider__runway) { background-color: #E5E7EB; height: 4px; }
:deep(.light-slider .el-slider__bar) { background-color: #14B8A6; height: 4px; }
:deep(.light-slider .el-slider__button) { border: 2px solid #14B8A6; background-color: #FFFFFF; width: 14px; height: 14px; }

/* ✨ 亮色步进器 */
:deep(.light-stepper .el-input__wrapper) { background-color: #F9FAFB; box-shadow: 0 0 0 1px #E5E7EB inset; padding: 0 24px 0 8px; }
:deep(.light-stepper .el-input__inner) { color: #374151; font-size: 12px; text-align: center; }
:deep(.light-stepper .el-input-number__increase), 
:deep(.light-stepper .el-input-number__decrease) { background-color: #F3F4F6; border-color: #E5E7EB; color: #6B7280; width: 20px; }
:deep(.light-stepper .el-input-number__increase:hover), 
:deep(.light-stepper .el-input-number__decrease:hover) { color: #14B8A6; }

.divider { height: 1px; background-color: #E5E7EB; margin: 0 0 16px 0; }
.brush-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }

/* ✨ 亮色卡片 */
.brush-card { display: flex; align-items: center; gap: 10px; padding: 6px 8px; border-radius: 6px; background-color: transparent; border: 1px solid transparent; cursor: pointer; transition: all 0.2s ease; }
.brush-card:hover { background-color: #F3F4F6; }
.brush-card.is-active { background-color: rgba(20, 184, 166, 0.1); border-color: #14B8A6; }
.brush-card.is-active .brush-name { color: #0F766E; font-weight: bold; }

.brush-thumb { width: 30px; height: 30px; flex-shrink: 0; border-radius: 4px; background-color: #F9FAFB; border: 1px dashed #D1D5DB; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.thumb-placeholder { width: 20px; height: 4px; background-color: #9CA3AF; border-radius: 2px; transform: rotate(-15deg); }
.brush-name { font-size: 13px; color: #4B5563; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; transition: color 0.2s; }
</style>