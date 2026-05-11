<template>
  <div class="layer-panel">
    
    <div class="layer-header-ctrl" v-if="store.activeLayer" :key="'ctrl-' + store.activeLayerId">
      <el-select v-model="store.activeLayer.blendMode" size="small" class="light-select" style="width: 100px;">
        <el-option label="正常 (Normal)" value="source-over" />
        <el-option label="正片叠底" value="multiply" />
        <el-option label="屏幕" value="screen" />
        <el-option label="叠加" value="overlay" />
      </el-select>

      <div class="opacity-ctrl">
        <span class="opacity-label">N</span>
        <el-slider 
          v-model="store.activeLayer.opacity" 
          :min="1" :max="100" 
          :show-tooltip="false"
          class="light-slider slim-slider" 
        />
      </div>
    </div>

    <div class="layer-list-container" :key="'list-' + store.layers.length">
      <div 
        v-for="layer in reversedUiLayers" 
        :key="layer.id"
        class="layer-item"
        :class="{ 'is-active': store.activeLayerId === layer.id }"
        @click="store.activeLayerId = layer.id"
      >
        <div class="layer-eye" @click.stop="layer.visible = !layer.visible">
          <el-icon :size="16" :color="layer.visible ? '#4B5563' : '#D1D5DB'">
            <View v-if="layer.visible" />
            <Hide v-else />
          </el-icon>
        </div>

        <div class="layer-thumb" :class="{ 'is-hidden': !layer.visible }">
           <img v-if="layer.thumbnail" :src="layer.thumbnail" class="thumb-img" />
        </div>

        <div class="layer-info layer-name-container" :class="{ 'is-hidden': !layer.visible }" @dblclick="startRename(layer)">
          <span v-if="editingLayerId !== layer.id" class="layer-name">
            {{ layer.name || '图层 ' + layer.id }}
          </span>
          
          <el-input
            v-else
            v-model="tempLayerName"
            size="small"
            class="layer-name-input"
            ref="renameInputRef"
            @blur="commitRename(layer)"
            @keyup.enter="commitRename(layer)"
            @keyup.esc="cancelRename"
          />

          <el-icon v-if="layer.locked && editingLayerId !== layer.id" :size="12" color="#ef4444" class="lock-icon"><Lock /></el-icon>
        </div>
      </div>
    </div>

    <div class="layer-action-bar">
      <el-tooltip content="新建图层" placement="top" :show-after="300">
        <button class="action-btn" @click="store.addLayer()">
          <el-icon><Plus /></el-icon>
        </button>
      </el-tooltip>

      <el-tooltip content="复制当前图层" placement="top" :show-after="300">
        <button class="action-btn" @click="store.cloneLayer()">
          <el-icon><DocumentCopy /></el-icon>
        </button>
      </el-tooltip>

      <el-tooltip content="向下合并" placement="top" :show-after="300">
        <button class="action-btn" @click="store.mergeDownLayer()">
          <el-icon><Bottom /></el-icon>
        </button>
      </el-tooltip>

      <el-tooltip content="删除图层" placement="top" :show-after="300">
        <button class="action-btn danger-hover" @click="handleDelete" :disabled="store.uiLayers.length <= 1">
          <el-icon><Delete /></el-icon>
        </button>
      </el-tooltip>
    </div>

  </div>
</template>

<script setup>
import { computed, ref, nextTick } from 'vue' // 🌟 补充导入
import { useBoardStore } from '../../../../stores/boardStore'
import { View, Hide, Lock, Plus, DocumentCopy, Bottom, Delete } from '@element-plus/icons-vue'

const store = useBoardStore()

const reversedUiLayers = computed(() => {
  return [...store.uiLayers].reverse()
})

const handleDelete = () => {
  if (store.uiLayers.length > 1) {
    store.deleteLayer(store.activeLayerId)
  }
}

// ==========================================
// 🌟 图层重命名逻辑
// ==========================================
const editingLayerId = ref(null) 
const tempLayerName = ref('')    
const renameInputRef = ref(null) 

const startRename = async (layer) => {
  editingLayerId.value = layer.id
  tempLayerName.value = layer.name || '图层 ' + layer.id
  
  await nextTick()
  // Vue3 中 v-for 内的 ref 可能会返回数组，故做兼容处理
  const inputEl = Array.isArray(renameInputRef.value) ? renameInputRef.value[0] : renameInputRef.value
  if (inputEl) {
    inputEl.focus()
  }
}

const commitRename = (layer) => {
  if (editingLayerId.value === layer.id) {
    store.renameLayer(layer.id, tempLayerName.value)
    editingLayerId.value = null
  }
}

const cancelRename = () => {
  editingLayerId.value = null
}
</script>

<style scoped>
.layer-panel {
  display: flex;
  flex-direction: column;
  height: 320px;
  background-color: transparent;
  margin: -12px;
}

/* ==========================================
   顶部控制区：白昼化
========================================== */
.layer-header-ctrl {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid #E5E7EB;
  background-color: #F9FAFB;
  border-radius: 4px 4px 0 0;
}

.opacity-ctrl { display: flex; align-items: center; gap: 8px; flex: 1; margin-left: 12px; }
.opacity-label { font-size: 14px; font-weight: bold; color: #9CA3AF; font-family: serif; }

:deep(.light-select .el-input__wrapper) { background-color: #FFFFFF; box-shadow: 0 0 0 1px #E5E7EB inset; }
:deep(.light-select .el-input__inner) { color: #374151; font-size: 12px; }

:deep(.slim-slider) { flex: 1; }
:deep(.slim-slider .el-slider__runway) { height: 2px; background-color: #E5E7EB; }
:deep(.slim-slider .el-slider__bar) { height: 2px; background-color: #9CA3AF; }
:deep(.slim-slider .el-slider__button) { width: 10px; height: 10px; border: 2px solid #6B7280; background-color: #FFFFFF; }

/* ==========================================
   中部滚动列表：白昼化
========================================== */
.layer-list-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background-color: #FFFFFF;
}
.layer-list-container::-webkit-scrollbar { width: 4px; }
.layer-list-container::-webkit-scrollbar-thumb { background-color: #D1D5DB; border-radius: 4px; }

.layer-item {
  display: flex;
  align-items: center;
  height: 38px;
  padding: 0 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.1s;
}
.layer-item:hover { background-color: #F3F4F6; }

/* ✨ 选中层高亮：极其克制的浅靛蓝，不抢夺画纸的视觉焦点 */
.layer-item.is-active { background-color: #E0E7FF; }
.layer-item.is-active .layer-name { color: #312E81; font-weight: bold; }
.layer-item.is-active .layer-eye { color: #374151 !important; }

.layer-eye { width: 24px; display: flex; align-items: center; justify-content: flex-start; }

.layer-thumb {
  width: 32px;
  height: 24px;
  background-color: #ffffff;
  border-radius: 2px;
  margin-right: 10px;
  flex-shrink: 0;
  /* 透明网格底纹调浅 */
  background-image: linear-gradient(45deg, #eee 25%, transparent 25%), linear-gradient(-45deg, #eee 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #eee 75%), linear-gradient(-45deg, transparent 75%, #eee 75%);
  background-size: 6px 6px;
  background-position: 0 0, 0 3px, 3px -3px, -3px 0px;
  transition: opacity 0.2s;
  overflow: hidden;
  border: 1px solid #E5E7EB;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
}

/* 🌟 修改后的 layer-info，支持编辑态布局 */
.layer-info { 
  flex: 1; 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  overflow: hidden; 
  transition: opacity 0.2s; 
}
.layer-name-container {
  cursor: text;
  min-width: 0; /* 关键：允许 flex 子元素截断超长文本 */
}
.layer-name { 
  font-size: 13px; 
  color: #4B5563; 
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
  user-select: none;
}
.layer-name-input {
  width: 100%;
}
/* 微调 el-input 以适应行高 */
:deep(.layer-name-input .el-input__inner) {
  height: 24px;
  line-height: 24px;
  font-size: 13px;
  padding: 0 4px;
}

.is-hidden { opacity: 0.4; }

/* ==========================================
   底部四大动作栏：白昼化
========================================== */
.layer-action-bar {
  display: flex;
  height: 40px;
  border-top: 1px solid #E5E7EB;
  background-color: #F9FAFB;
  border-radius: 0 0 4px 4px;
}

.action-btn {
  flex: 1;
  background: transparent;
  border: none;
  border-right: 1px solid #E5E7EB;
  color: #6B7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s;
}
.action-btn:last-child { border-right: none; }
.action-btn:hover:not(:disabled) { background-color: #F3F4F6; color: #111827; }
.action-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.action-btn.danger-hover:hover:not(:disabled) { color: #ef4444; }
</style>