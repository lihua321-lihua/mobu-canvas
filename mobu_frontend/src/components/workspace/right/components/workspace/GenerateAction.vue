<template>
  <div class="generate-section">
    <button class="mega-generate-btn" :disabled="store.isAIGenerating" @click="handleMegaGenerate">
      <span v-if="!store.isAIGenerating">生成 AI 画作</span>
      <span v-else class="loading-text">
        <el-icon class="is-loading"><Loading /></el-icon> 
        生图中... {{ store.generateProgress || 0 }}%
      </span>
    </button>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
import { useBoardStore } from '../../../../../stores/boardStore'
import { useAIGeneration } from '../../composables/useAIGeneration'

const store = useBoardStore()
const { handleMegaGenerate } = useAIGeneration()
</script>

<style scoped>
.mega-generate-btn { 
  width: 100%; height: 48px; border-radius: 8px; border: none; background: #111827; 
  color: white; font-size: 15px; font-weight: bold; letter-spacing: 1px; cursor: pointer; 
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); display: flex; align-items: center; 
  justify-content: center; box-shadow: 0 4px 12px rgba(17, 24, 39, 0.15); 
}
.mega-generate-btn:hover:not(:disabled) { background: #374151; transform: translateY(-2px); box-shadow: 0 6px 16px rgba(17, 24, 39, 0.2); }
.mega-generate-btn:disabled { background: #F3F4F6; color: #9CA3AF; cursor: not-allowed; box-shadow: none; }
.loading-text { display: flex; align-items: center; gap: 8px; font-weight: normal; }
</style>