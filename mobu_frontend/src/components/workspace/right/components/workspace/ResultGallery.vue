<template>
  <div class="results-section">
    <div class="section-header">
      <div class="section-title">生成结果</div>
      <button 
        class="quick-add-btn" 
        :class="{ 'is-disabled': activeResultIndex === null || !store.latestResultImageUrls?.[activeResultIndex] }"
        :disabled="activeResultIndex === null || !store.latestResultImageUrls?.[activeResultIndex]"
        @click="handleAddToLayer"
      >
        ➕ 添加到图层
      </button>
    </div>

    <div class="result-grid">
      <div 
        class="result-box" 
        v-for="(_, index) in 2" 
        :key="index"
        :class="{ 'is-active': activeResultIndex === index }"
        @click="activeResultIndex = index"
        @dblclick="onDoubleclick(index)"
      >
        <img 
          v-if="store.latestResultImageUrls && store.latestResultImageUrls[index]" 
          :src="store.latestResultImageUrls[index]" 
          class="result-image"
          alt="AI 生成结果"
          draggable="false"
        />
        
        <div v-else class="empty-placeholder">
          <el-icon color="#E5E7EB" :size="24"><Picture /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import { useBoardStore } from '../../../../../stores/boardStore'
import { ElMessage } from 'element-plus'
import { injectAILayerFromUrl } from '../../../../../utils/aiLayerManager'

const store = useBoardStore()
const emit = defineEmits(['open-lightbox'])

// 默认选中第 1 张图 (index 0)
const activeResultIndex = ref(0) 

// ==========================================
// 🛡️ 核心黑科技：跨域安全的图片加载器
// ==========================================
const loadCorsSafeImage = (url) => {
  return new Promise((resolve, reject) => {
    const img = new window.Image()
    img.crossOrigin = 'anonymous' 
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('图片加载失败，可能是跨域策略限制或网络异常'))
    img.src = url
  })
}

const handleAddToLayer = async () => {
  const targetUrl = store.latestResultImageUrls?.[activeResultIndex.value]
  if (!targetUrl) return ElMessage.warning('请先选择一张要添加到画板的图片！')

  try {
    await injectAILayerFromUrl(targetUrl, store)

  } catch (error) {
    console.error('【控制台调用注入引擎失败】:', error)
  }
}
// 🌟 双击展示当前选中图片的大图
const onDoubleclick = (index) => {
  if (store.latestResultImageUrls && store.latestResultImageUrls[index]) {
    emit('open-lightbox', index)
  }
}
</script>

<style scoped>
/* 样式部分保持极致黑白灰不变，与上一步完全一致，此处省略赘述以保持版面清爽... */
.results-section { display: flex; flex-direction: column; gap: 12px; }
.section-header { display: flex; justify-content: space-between; align-items: center; }
.section-title { font-size: 12px; color: #6B7280; font-weight: bold; }
.quick-add-btn { background: #FFFFFF; color: #111827; border: 1px solid #E5E7EB; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; cursor: pointer; transition: all 0.2s; }
.quick-add-btn:hover:not(.is-disabled) { background: #F3F4F6; transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.quick-add-btn.is-disabled { background: #F9FAFB; color: #9CA3AF; cursor: not-allowed; border-color: #F3F4F6; }
/* 如果你希望这两张图是左右排布，此处保持 repeat(2, 1fr) 即可。如果想上下排布，可以改成 1fr */
.result-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.result-box { aspect-ratio: 1 / 1; background-color: #F9FAFB; border: 2px solid #F3F4F6; border-radius: 8px; display: flex; align-items: center; justify-content: center; transition: all 0.2s; cursor: pointer; overflow: hidden; }
.result-box.is-active { border-color: #111827; background-color: #FFFFFF; box-shadow: none; }
.result-box:hover:not(.is-active) { border-color: #D1D5DB; background-color: #FFFFFF; }
.empty-placeholder { display: flex; align-items: center; justify-content: center; }
.result-image { width: 100%; height: 100%; object-fit: cover; display: block; }
</style>