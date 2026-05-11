<template>
  <div class="btn-wrapper">
    <el-popover placement="right" :width="260" trigger="click" effect="light" :offset="20">
      
      <template #reference>
        <div> 
          <el-tooltip content="局部重绘涂抹区" placement="right" :show-after="200" :hide-after="0">
            <el-button 
              circle 
              size="large" 
              class="glass-btn"
              :class="{ 'is-active': store.activeTool === 'inpainting' }" 
              @click="store.activeTool = 'inpainting'"
            >
              <el-icon :size="20"><MagicStick /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </template>

      <div class="inpaint-panel">
        <div class="panel-header">
          <span class="panel-title">遮罩笔刷大小</span>
          <span class="panel-value">{{ store.maskBrushSize }}px</span>
        </div>
        
        <div class="slider-container">
          <el-slider 
            v-model="store.maskBrushSize" 
            :min="5" 
            :max="150" 
            :show-tooltip="false"
            class="custom-slider"
          />
        </div>

        <div class="preview-box">
          <div 
            class="brush-preview-circle"
            :style="{ 
              width: store.maskBrushSize + 'px', 
              height: store.maskBrushSize + 'px' 
            }"
          ></div>
        </div>
      </div>

    </el-popover>
  </div>
</template>

<script setup>
import { MagicStick } from '@element-plus/icons-vue'
import { useBoardStore } from '../../../../stores/boardStore'

const store = useBoardStore()
</script>

<style scoped>
.btn-wrapper { display: inline-flex; }
.glass-btn { background-color: transparent !important; border: 1px solid transparent !important; color: #9CA3AF !important; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.glass-btn:hover, .glass-btn:focus { background-color: #F3F4F6 !important; color: #374151 !important; border-color: transparent !important; }
.glass-btn.is-active { background-color: #E5E7EB !important; color: #111827 !important; border-color: transparent !important; box-shadow: none !important; }

.inpaint-panel { padding: 8px 4px; display: flex; flex-direction: column; gap: 16px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
.panel-title { color: #374151; font-weight: bold; }
.panel-value { color: #6B7280; font-variant-numeric: tabular-nums; }

:deep(.custom-slider) { --el-slider-main-bg-color: #111827; --el-slider-runway-bg-color: #E5E7EB; --el-slider-button-size: 16px; --el-slider-button-wrapper-size: 16px; }
:deep(.custom-slider .el-slider__button) { border: 2px solid #111827; background-color: #FFFFFF; transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
:deep(.custom-slider .el-slider__button:hover), :deep(.custom-slider .el-slider__button.hover) { transform: scale(1.2); cursor: grab; }
:deep(.custom-slider .el-slider__button:active) { cursor: grabbing; }

.preview-box { height: 160px; width: 100%; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; display: flex; align-items: center; justify-content: center; overflow: hidden; }
.brush-preview-circle { border-radius: 50%; background-color: rgba(255, 0, 0, 0.4); border: 1px solid rgba(255, 0, 0, 0.6); transition: width 0.1s, height 0.1s; pointer-events: none; }
</style>