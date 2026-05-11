<template>
  <div class="prompt-section">
    <div class="prompt-wrapper">
      <el-input
        v-model="store.promptText"
        type="textarea"
        :rows="5"
        resize="none"
        placeholder="描述你想要的画面..."
        class="light-prompt-input"
      />
      <button class="magic-polish-btn" @click="handlePolish">
        <img :src="magicIconImg" alt="润色" class="custom-magic-icon" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { useBoardStore } from '../../../../../stores/boardStore' // 请根据实际项目保留 @ 别名或替换为相对路径
import { usePromptPolish } from '../../composables/usePromptPolish'
import magicIconImg from '../../../../../assets/magic-icon.png' // 请根据实际项目调整

const store = useBoardStore()
const { handlePolish } = usePromptPolish()
</script>

<style scoped>
.prompt-section { display: flex; flex-direction: column; }
.prompt-wrapper { position: relative; width: 100%; }
:deep(.light-prompt-input) {
  --el-input-focus-border-color: transparent;
  --el-input-border-color: transparent;
}
:deep(.light-prompt-input .el-textarea__inner) { 
  background-color: #F9FAFB; border: 1px solid #E5E7EB; box-shadow: none !important; 
  color: #374151; padding: 12px 12px 42px 12px; border-radius: 8px; 
  font-size: 13px; line-height: 1.6; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
:deep(.light-prompt-input .el-textarea__inner:focus) { 
  background-color: #FFFFFF; border-color: #111827;
  box-shadow: 0 0 0 2px rgba(17, 24, 39, 0.05) !important; 
}
:deep(.light-prompt-input .el-textarea__inner::placeholder) { color: #9CA3AF; }
.magic-polish-btn { 
  position: absolute; right: 8px; bottom: 8px; background: #FFFFFF; border: 1px solid #E5E7EB; 
  border-radius: 8px; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; 
  padding: 0; cursor: pointer; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.magic-polish-btn:hover { border-color: #D1D5DB; background-color: #F9FAFB; transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0,0,0,0.04); }
.custom-magic-icon { width: 18px; height: 18px; object-fit: contain; opacity: 0.7; transition: opacity 0.2s; }
.magic-polish-btn:hover .custom-magic-icon { opacity: 1; }
</style>