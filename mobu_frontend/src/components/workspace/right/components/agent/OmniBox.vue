<template>
  <div class="omni-box-container" :class="{ 'agent-active': isExecuting }">
    <textarea 
      v-model="inputText"
      class="magic-textarea" 
      placeholder="输入灵感，或向智能体求助 (按回车发送)..."
      @keydown.enter.prevent="handleEnter"
      :disabled="isExecuting"
    ></textarea>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isExecuting: Boolean // 接收外部传入的正在执行状态
})

const emit = defineEmits(['send-message'])
const inputText = ref('')

const handleEnter = () => {
  if (!inputText.value.trim() || props.isExecuting) return
  emit('send-message', inputText.value)
  inputText.value = '' // 发送后清空输入框
}
</script>

<style scoped>
.omni-box-container {
  position: relative;
  background: #fafafa;
  border-radius: 8px;
  padding: 12px 16px;
  transition: all 0.8s ease;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

/* 智能体执行代笔时的水墨呼吸态 */
.omni-box-container.agent-active {
  background: #ffffff;
  border-bottom: 1px solid transparent;
  animation: ink-breathe 3s infinite alternate ease-in-out;
}

@keyframes ink-breathe {
  0% { box-shadow: 0 2px 15px rgba(44, 62, 80, 0.02); }
  100% { box-shadow: 0 10px 30px rgba(44, 62, 80, 0.12); }
}

.magic-textarea {
  width: 100%;
  height: 48px;
  border: none;
  background: transparent;
  outline: none;
  resize: none;
  font-family: -apple-system, sans-serif;
  font-size: 13px;
  line-height: 1.5;
  color: #333;
}

.magic-textarea::placeholder {
  color: #a4a4a4;
  font-family: "Noto Serif SC", serif;
}
</style>