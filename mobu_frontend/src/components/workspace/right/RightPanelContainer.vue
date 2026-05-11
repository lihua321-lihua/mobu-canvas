<template>
  <div class="right-panel-container" ref="containerRef">
    
    <div 
      class="ai-fab-button" 
      v-if="store.isAIConsoleCollapsed" 
      @mousedown.stop
      @click.stop="store.isAIConsoleCollapsed = false"
      title="展开 AI 魔法控制台"
    >
      <img src="../../../assets/ai-fab-icon.png" alt="AI" class="fab-icon" />
    </div>

    <template v-else>
      <div class="ink-switcher">
        <div 
          class="switch-item" 
          :class="{ 'is-active': currentMode === 'pro' }"
          @click="currentMode = 'pro'"
        >
          专业控制台
        </div>
        <div 
          class="switch-item" 
          :class="{ 'is-active': currentMode === 'agent' }"
          @click="currentMode = 'agent'"
        >
          伴生智能
        </div>
      </div>

      <div class="panel-content">
        <Transition name="ink-fade" mode="out-in">
          <AIConsole v-if="currentMode === 'pro'" key="pro" />
          <AgentCopilot v-else key="agent" />
        </Transition>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useBoardStore } from '../../../stores/boardStore' // 请根据实际层级检查路径
import AIConsole from './components/workspace/AIConsole.vue'
import AgentCopilot from './components/agent/AgentCopilot.vue'

const store = useBoardStore()
const currentMode = ref('pro')
const containerRef = ref(null)

// 🛡️ 状态提升：将原先 AIConsole 里的全局 ClickOutside 收起逻辑移到这里
const handleClickOutside = (event) => {
  if (store.isAIConsoleCollapsed) return 
  // 注意：如果你有灯箱放大功能 (Lightbox)，需要把 isLightboxOpen 状态也引过来判断
  if (containerRef.value && !containerRef.value.contains(event.target)) {
    store.isAIConsoleCollapsed = true
  }
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))
</script>

<style scoped>
.right-panel-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #ffffff;
  position: relative; /* 保证悬浮按钮定位准确 */
  border-radius: 16px; 
}

/* 移植过来的悬浮按钮样式 */
.ai-fab-button {
  position: absolute; left: -76px; top: 50%; transform: translateY(-50%); width: 56px; height: 56px;
  border-radius: 50%; background-color: #FFFFFF; border: 1px solid #E5E7EB; box-shadow: 0 8px 24px rgba(0,0,0,0.08);
  display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s; z-index: 1000;
}
.ai-fab-button:hover { transform: translateY(calc(-50% - 2px)) scale(1.05); box-shadow: 0 12px 28px rgba(0,0,0,0.12); }
.fab-icon { width: 24px; height: 24px; object-fit: contain; }

/* 水墨风切换器和动画样式 (与上一轮提供的一致) */
.ink-switcher { display: flex; height: 50px; padding: 0 24px; align-items: center; gap: 32px; border-bottom: 1px solid rgba(0, 0, 0, 0.04);  border-radius: px;justify-content: center; }
.switch-item { font-family: "Noto Serif SC", serif; font-size: 15px; color: #888888; cursor: pointer; position: relative; padding: 8px 0; transition: color 0.3s ease; letter-spacing: 1px; }
.switch-item:hover { color: #555555; }
.switch-item.is-active { color: #2c3e50; font-weight: 600; }
.switch-item::after { content: ''; position: absolute; bottom: 0; left: 10%; width: 80%; height: 2px; background: linear-gradient(90deg, transparent, #2c3e50, transparent); opacity: 0; transform: translateY(2px); transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); }
.switch-item.is-active::after { opacity: 1; transform: translateY(0); }
.panel-content { flex: 1; overflow: hidden; position: relative; }
.ink-fade-enter-active, .ink-fade-leave-active { transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.ink-fade-enter-from { opacity: 0; transform: translateY(10px) scale(0.98); filter: blur(2px); }
.ink-fade-leave-to { opacity: 0; transform: translateY(-10px) scale(0.98); filter: blur(2px); }
</style>