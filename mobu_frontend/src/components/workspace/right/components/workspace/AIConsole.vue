<template>
  <div class="ai-console">
    <div class="console-body">
      <PromptBox />
      <GenerateAction />
      <ResultGallery @open-lightbox="openLightbox" />
    </div>

    <ImageLightbox 
      v-model:is-open="isLightboxOpen"
      v-model:active-index="lightboxIndex"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PromptBox from './PromptBox.vue'
import GenerateAction from './GenerateAction.vue'
import ResultGallery from './ResultGallery.vue'
import ImageLightbox from '../common/ImageLightbox.vue'

const isLightboxOpen = ref(false)
const lightboxIndex = ref(0)
const openLightbox = (index) => {
  lightboxIndex.value = index
  isLightboxOpen.value = true
}
// ⚠️ 全局收起逻辑已被安全移除并提升至父容器
</script>

<style scoped>
.ai-console { display: flex; flex-direction: column; height: 100%; width: 100%; }
.console-body { padding: 20px 16px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 28px; }
</style>