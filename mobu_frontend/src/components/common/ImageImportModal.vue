<template>
  <Teleport to="body">
    <Transition name="fade-modal">
      <div v-if="modelValue" class="modal-overlay" @click.self="closeModal">
        
        <div class="import-card">
          <header class="card-header">
            <h2 class="title">导入图片</h2>
            <button class="close-btn" @click="closeModal">&times;</button>
          </header>

          <p class="instruction">请先为导入的图片选择一个规范的画布比例：</p>

          <div class="preset-mini-grid">
            <button 
              v-for="preset in canvasPresets" 
              :key="preset.id"
              class="mini-preset-btn"
              @click="triggerFileUpload(preset)"
            >
              <div class="wireframe-mini" :style="{ aspectRatio: preset.ratio }"></div>
              <span class="label">{{ preset.label }}</span>
            </button>
          </div>

          <input 
            type="file" 
            ref="fileInputRef" 
            class="hidden-input" 
            accept="image/jpeg, image/png, image/webp"
            @change="handleFileSelected"
          />

          <div v-if="isProcessing" class="processing-overlay">
            <span class="loading-text">正在处理图像数据...</span>
          </div>
        </div>

      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useBoardStore } from '../../stores/boardStore' // 请根据实际路径调整
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Boolean, required: true }
})
const emit = defineEmits(['update:modelValue'])

const router = useRouter()
const store = useBoardStore()

const fileInputRef = ref(null)
const isProcessing = ref(false)
const targetPreset = ref(null)

// 复用预设数据
const canvasPresets = [
  { id: '1:1', label: '1:1 正方', width: 1080, height: 1080, ratio: '1 / 1' },
  { id: '3:4', label: '3:4 社交', width: 1080, height: 1440, ratio: '3 / 4' },
  { id: '4:3', label: '4:3 经典', width: 1080, height: 810, ratio: '4 / 3' },
  { id: '9:16', label: '9:16 竖屏', width: 1080, height: 1920, ratio: '9 / 16' },
  { id: '16:9', label: '16:9 横屏', width: 1080, height: 607, ratio: '16 / 9' }
]

const closeModal = () => {
  if (isProcessing.value) return // 处理中禁止关闭
  emit('update:modelValue', false)
  fileInputRef.value.value = '' // 清空 input
}

// 步骤 1：用户点击了某个比例，记录目标尺寸，触发物理文件选择
const triggerFileUpload = (preset) => {
  targetPreset.value = preset
  fileInputRef.value.click()
}

// 步骤 2：读取用户图片，完成图层初始化，并跳转
const handleFileSelected = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 校验图片类型
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    ElMessage.error('仅支持 JPG, PNG 或 WEBP 格式图片')
    return
  }

  isProcessing.value = true

  const reader = new FileReader()
  reader.onload = (e) => {
    const base64Image = e.target.result
    
    // ==========================================
    // 🌟 核心业务逻辑：直接调用 Store 中封装好的高级排版初始化方法
    // ==========================================
    
    store.initImportedImage(
      base64Image, 
      targetPreset.value.width, 
      targetPreset.value.height
    )

    // 跳转至工作区，此时会自动进入全局“图片排版模式”
    isProcessing.value = false
    closeModal()
    router.push('/workspace')
  }

  reader.onerror = () => {
    isProcessing.value = false
    ElMessage.error('读取图片失败，请重试')
  }

  reader.readAsDataURL(file)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(17, 24, 39, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.import-card {
  width: 520px;
  background-color: #ffffff;
  border-radius: 8px;
  border: 2px solid #111827;
  padding: 32px 40px;
  position: relative;
  /* 粗野主义硬阴影，保持极简视觉一致性 */
  box-shadow: 8px 8px 0px #111827;
  font-family: 'Inter', 'PingFang SC', sans-serif;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title {
  font-size: 20px;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  line-height: 1;
  color: #9CA3AF;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover { color: #111827; }

.instruction {
  font-size: 14px;
  color: #6B7280;
  margin-bottom: 24px;
}

.preset-mini-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.mini-preset-btn {
  background: transparent;
  border: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.wireframe-mini {
  width: 100%;
  border: 1.5px solid #D1D5DB;
  background-image: radial-gradient(#E5E7EB 1px, transparent 1px);
  background-size: 6px 6px;
  transition: all 0.2s;
}

.mini-preset-btn:hover .wireframe-mini {
  border-color: #111827;
  box-shadow: 3px 3px 0px #111827;
  transform: translate(-1px, -1px);
}

.label {
  font-size: 12px;
  font-weight: 600;
  color: #4B5563;
}

.mini-preset-btn:hover .label { color: #111827; }

.hidden-input { display: none; }

.processing-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
}

.loading-text {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* 模态框进出动画 */
.fade-modal-enter-active, .fade-modal-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-modal-enter-from, .fade-modal-leave-to {
  opacity: 0;
  transform: scale(0.98);
}
</style>