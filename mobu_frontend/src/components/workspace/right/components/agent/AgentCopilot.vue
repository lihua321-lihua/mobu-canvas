<template>
  <div class="agent-copilot">
    <div class="chat-history-scroll" ref="chatScrollRef">
      <div class="greeting">
        墨意已就绪，你需要怎样的灵感？
      </div>

      <div 
        v-for="msg in chatHistory" 
        :key="msg.id"
        class="msg-row"
        :class="msg.role === 'user' ? 'is-user' : 'is-agent'"
      >
        <div v-if="msg.role === 'agent'" class="ink-anchor">
          <svg viewBox="0 0 24 24" class="ink-drop" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2.75C12 2.75 6.25 10.5 6.25 15C6.25 18.1763 8.82373 20.75 12 20.75C15.1763 20.75 17.75 18.1763 17.75 15C17.75 10.5 12 2.75 12 2.75Z" fill="currentColor"/>
          </svg>
        </div>

        <div class="msg-content">
          <div class="msg-text">{{ msg.text }}</div>

          <Transition name="seal-pop">
            <button 
              v-if="msg.showSeal && !store.isAgentExecuting" 
              class="seal-btn"
              @click="handleSealApproval(msg)"
            >
              准许落笔
            </button>
          </Transition>
        </div>
      </div>
    </div>

    <ActionStream :action-text="currentActionText" />

    <div class="omni-box-wrapper">
      <OmniBox 
        @send-message="handleUserMessage" 
        :is-executing="store.isAgentExecuting" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useBoardStore } from '../../../../../stores/boardStore' // 确保路径正确
import OmniBox from './OmniBox.vue'
import ActionStream from './ActionStream.vue'

const store = useBoardStore()
const chatScrollRef = ref(null)
const currentActionText = ref('')

// 状态：对话历史
const chatHistory = ref([])
let msgId = 0

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (chatScrollRef.value) {
    chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
  }
}

// 接收用户的输入 (从 OmniBox 传来)
const handleUserMessage = async (text) => {
  if (!text.trim()) return
  
  // 1. 插入用户消息 (右侧靠右)
  chatHistory.value.push({
    id: msgId++,
    role: 'user',
    text: text,
    showSeal: false
  })
  scrollToBottom()

  // 2. 模拟 Agent 思考并回复 (Plan 模式)
  setTimeout(() => {
    chatHistory.value.push({
      id: msgId++,
      role: 'agent',
      text: '感受到了，清晨的微光最适合。已为您调配秋日色板，并锁定【氛围铺色】模式，需要我代笔吗？',
      showSeal: true // 展现盖章按钮
    })
    scrollToBottom()
  }, 1000)
}

// 用户点击【准许落笔】触发执行 (Execute 模式)
const handleSealApproval = async (msg) => {
  // 隐藏当前消息的印章
  msg.showSeal = false 
  
  // 剧本式 UI 播报
  currentActionText.value = '正在为您接管画板与提示词...'
  
  // 模拟从后端拿到的 JSON 动作指令
  const mockAgentResponse = {
    prompt_override: "masterpiece, autumn atmosphere, falling leaves, detailed illustration, warm morning light",
    switch_tab: "color", // 自动切换到铺色模式
    trigger_generate: true
  }

  // 移交 Pinia 调度中心进行“隔空操控”
  setTimeout(() => {
    store.dispatchAgentAction(mockAgentResponse)
    currentActionText.value = '已切换至【氛围铺色】，墨意凝聚中...'
  }, 1200)

  setTimeout(() => {
    currentActionText.value = '' 
  }, 4000)
}
</script>

<style scoped>
.agent-copilot {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px 24px;
  box-sizing: border-box;
  background-color: #ffffff;
}

/* 隐藏原生滚动条，保持极简 */
.chat-history-scroll {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}
.chat-history-scroll::-webkit-scrollbar {
  width: 4px;
}
.chat-history-scroll::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.05);
  border-radius: 4px;
}

.greeting {
  font-family: "Noto Serif SC", serif;
  font-size: 13px;
  color: #a4a4a4;
  text-align: center;
  margin: 30px 0 40px 0;
  letter-spacing: 2px;
}

/* ========================================= */
/* ✨ 云水行文排版核心 CSS */
/* ========================================= */
.msg-row {
  display: flex;
  width: 100%;
  margin-bottom: 28px;
  position: relative;
}

.msg-content {
  max-width: 85%;
  display: flex;
  flex-direction: column;
}

/* 1. 人类指令 (右侧) */
.is-user {
  justify-content: flex-end;
}
.is-user .msg-content {
  align-items: flex-end;
}
.is-user .msg-text {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50; /* 黛黑色 */
  text-align: right;
  line-height: 1.6;
}

/* 2. 智能伴生 (左侧) */
.is-agent {
  justify-content: flex-start;
  padding-left: 24px; /* 为水墨滴留出空间 */
}
.is-agent .msg-content {
  align-items: flex-start;
}
.is-agent .msg-text {
  font-family: "Noto Serif SC", "Songti SC", serif;
  font-size: 14px;
  color: #666666;
  text-align: left;
  line-height: 1.8; /* 增加行高，娓娓道来 */
}

/* 水墨滴微锚点 */
.ink-anchor {
  position: absolute;
  left: 0;
  top: 4px;
  color: #2c3e50;
  opacity: 0.35;
}
.ink-drop {
  width: 14px;
  height: 14px;
}

/* 准许落笔印章 */
.seal-btn {
  margin-top: 12px;
  background-color: transparent;
  color: #8b0000; /* 绛红印章色 */
  border: 1px solid #8b0000;
  padding: 4px 16px;
  font-family: "Noto Serif SC", serif;
  font-size: 12px;
  letter-spacing: 1px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  opacity: 0.85;
}
.seal-btn:hover {
  background-color: #8b0000;
  color: #ffffff;
  opacity: 1;
}

.seal-pop-enter-active,
.seal-pop-leave-active {
  transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.seal-pop-enter-from,
.seal-pop-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

.omni-box-wrapper {
  margin-top: auto;
  padding-top: 10px;
}
</style>