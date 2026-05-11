<template>
  <teleport to="body">
    <div class="lightbox-overlay" v-if="isOpen" @click="closeLightbox">
      
      <div class="lightbox-close" @click.stop="closeLightbox">
        <el-icon><Close /></el-icon>
      </div>

      <div class="lightbox-nav nav-left" @click.stop="prevLightbox">
        <el-icon><ArrowLeft /></el-icon>
      </div>

      <div class="lightbox-content" @click.stop>
        <img 
          v-if="currentImages && currentImages[activeIndex]" 
          :src="currentImages[activeIndex]" 
          class="real-image" 
          alt="高清结果图"
          draggable="false"
        />
        
        <div v-else class="big-placeholder">
          <el-icon color="#4b5563" :size="64"><Picture /></el-icon>
          <p style="margin-top: 16px;">高清结果图 {{ activeIndex + 1 }}</p>
        </div>
      </div>

      <div class="lightbox-nav nav-right" @click.stop="nextLightbox">
        <el-icon><ArrowRight /></el-icon>
      </div>

    </div>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'
import { Picture, Close, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
// 🚨 请确保这里的路径能正确指向你的 boardStore.js
import { useBoardStore } from '../../../../../stores/boardStore' 

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  activeIndex: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:isOpen', 'update:activeIndex'])
const store = useBoardStore()

// 🌟 动态获取图片数组
const currentImages = computed(() => store.latestResultImageUrls || [])

const closeLightbox = () => emit('update:isOpen', false)

// 🌟 优化轮播逻辑：根据实际获取到的图片张数取模，防止数组越界
const nextLightbox = () => {
  const len = currentImages.value.length || 2
  emit('update:activeIndex', (props.activeIndex + 1) % len)
}

const prevLightbox = () => {
  const len = currentImages.value.length || 2
  emit('update:activeIndex', (props.activeIndex - 1 + len) % len)
}
</script>

<style scoped>
.lightbox-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  z-index: 9999; display: flex; align-items: center; justify-content: center;
}
.lightbox-close {
  position: absolute; top: 32px; right: 32px; color: white;
  font-size: 32px; cursor: pointer; opacity: 0.7; transition: opacity 0.2s;
}
.lightbox-close:hover { opacity: 1; }
.lightbox-nav {
  position: absolute; top: 50%; transform: translateY(-50%); color: white;
  font-size: 48px; cursor: pointer; opacity: 0.4; transition: all 0.2s; padding: 20px;
}
.lightbox-nav:hover { opacity: 1; transform: translateY(-50%) scale(1.1); }
.nav-left { left: 40px; }
.nav-right { right: 40px; }
.lightbox-content { display: flex; flex-direction: column; align-items: center; gap: 32px; }

/* 🌟 新增的真实图片渲染样式 */
.real-image {
  max-width: 90vw; 
  max-height: 85vh; 
  object-fit: contain;
  border-radius: 12px; 
  box-shadow: 0 24px 48px rgba(0,0,0,0.5);
  animation: popIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.big-placeholder {
  width: 512px; height: 512px; background: #1f2937; border-radius: 12px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #6b7280; font-size: 16px; font-weight: bold; box-shadow: 0 24px 48px rgba(0,0,0,0.5);
}

@keyframes popIn {
  0% { opacity: 0; transform: scale(0.95); }
  100% { opacity: 1; transform: scale(1); }
}
</style>