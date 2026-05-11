<template>
  <div class="toolbar-container">
    
    <div class="tool-group" v-if="store.workMode !== 'refine'" key="normal-tools">
      <el-popover placement="right" :width="260" trigger="click" effect="light" :offset="20">
        <template #reference>
          <div class="btn-wrapper">
            <el-tooltip content="图形工具" placement="right" :show-after="200" :hide-after="0">
              <el-button circle size="large" class="glass-btn" :class="{ 'is-active': store.activeTool === 'shape' }" @click="store.activeTool = 'shape'">
                <el-icon :size="20"><Grid /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
        <ShapePanel />
      </el-popover>

      <el-popover placement="right" :width="280" trigger="click" effect="light" :offset="20">
        <template #reference>
          <div class="btn-wrapper">
            <el-tooltip content="画笔库" placement="right" :show-after="200" :hide-after="0">
              <el-button circle size="large" class="glass-btn" :class="{ 'is-active': store.activeTool === 'brush' }" @click="store.activeTool = 'brush'">
                <el-icon :size="20"><EditPen /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
        <BrushPanel />
      </el-popover>

      <el-popover placement="right" :width="280" trigger="click" effect="light" :offset="20">
        <template #reference>
          <div class="btn-wrapper">
            <el-tooltip content="调色盘" placement="right" :show-after="200" :hide-after="0">
              <el-button circle size="large" class="glass-btn">
                <el-icon :size="20"><Aim /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
        <ColorPanel />
      </el-popover>
    </div>

    <div class="tool-group" v-if="store.workMode === 'refine'" key="refine-tools">
      <InpaintTool />
    </div>

    <div class="tool-group" key="global-eraser">
      <el-popover placement="right" :width="240" trigger="click" effect="light" :offset="20">
        <template #reference>
          <div class="btn-wrapper">
            <el-tooltip content="橡皮擦" placement="right" :show-after="200" :hide-after="0">
              <el-button circle size="large" class="glass-btn" :class="{ 'is-active': store.activeTool === 'eraser' }" @click="store.activeTool = 'eraser'">
                <el-icon :size="20"><Scissor /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
        <EraserPanel />
      </el-popover>
    </div>

    <div class="toolbar-divider"></div>

    <div class="tool-group" key="bottom-tools">
      <el-popover placement="right" :width="240" trigger="click" effect="light" :offset="20" :teleported="false">
        <template #reference>
          <div class="btn-wrapper">
            <el-tooltip content="抓手与视图漫游" placement="right" :show-after="200" :hide-after="0">
              <el-button circle size="large" class="glass-btn" :class="{ 'is-active': store.activeTool === 'hand' }" @click="store.activeTool = 'hand'">
                <el-icon :size="20"><Rank /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
        <HandPanel />
      </el-popover>

      <el-popover placement="right" :width="260" trigger="click" effect="light" :offset="20" popper-style="padding: 0;" :teleported="false">
        <template #reference>
          <div class="btn-wrapper">
            <el-tooltip content="图层管理" placement="right" :show-after="200" :hide-after="0">
              <el-button circle size="large" class="glass-btn">
                <el-icon :size="20"><CopyDocument /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </template>
        <LayerPanel />
      </el-popover>
    </div>

  </div>
</template>

<script setup>
import { Grid, EditPen, Scissor, Aim, CopyDocument, Rank } from '@element-plus/icons-vue'
import { useBoardStore } from '../../../stores/boardStore'
import ShapePanel from './panels/ShapePanel.vue'
import BrushPanel from './panels/BrushPanel.vue'
import EraserPanel from './panels/EraserPanel.vue'
import HandPanel from './panels/HandPanel.vue' 
import ColorPanel from './panels/ColorPanel.vue'
import LayerPanel from './panels/LayerPanel.vue'
import InpaintTool from './panels/InpaintTool.vue'

const store = useBoardStore()
</script>

<style scoped>
.toolbar-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 0;
  align-items: center;
  width: 100%;
}

/* 独立隔离框，切断 Vue DOM Diff 关联 */
.tool-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
  width: 100%;
}

.btn-wrapper { display: inline-flex; }
.toolbar-divider { width: 24px; height: 2px; background-color: #E5E7EB; border-radius: 2px; margin: 4px 0; }
.glass-btn { background-color: transparent !important; border: 1px solid transparent !important; color: #9CA3AF !important; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.glass-btn:hover, .glass-btn:focus { background-color: #F3F4F6 !important; color: #374151 !important; border-color: transparent !important; }
.glass-btn.is-active { background-color: #E5E7EB !important; color: #111827 !important; border-color: transparent !important; box-shadow: none !important; }
</style>