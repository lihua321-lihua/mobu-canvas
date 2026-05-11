import { ElMessage } from 'element-plus'
import { useBoardStore } from '../../../../stores/boardStore' 
import { polishPromptAPI } from '../services/aiService'

// ==========================================
// 🛡️ 稳如老狗的终极防呆校验 (带噪点容差的 RGBA 扫描法)
// ==========================================
export const isEmptyCanvas = (base64) => {
  // 如果连基础字符串都不够，直接判定为空
  if (!base64 || typeof base64 !== 'string' || base64.length < 100) return Promise.resolve(true)

  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    
    img.onload = () => {
      const canvas = document.createElement('canvas')
      // 🚀 保持原分辨率，绝不压缩，防止用户的极细线条丢失
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d', { willReadFrequently: true })
      
      // 直接绘制原图，不垫任何底色，保留原本的透明通道信息
      ctx.drawImage(img, 0, 0)
      
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const data = imageData.data
      
      let isEmpty = true
      
      // 步长为 4，安全遍历每一个像素的 R, G, B, A
      for (let i = 0; i < data.length; i += 4) {
        const r = data[i]
        const g = data[i + 1]
        const b = data[i + 2]
        const a = data[i + 3]
        
        // 💡 核心阈值判空逻辑：过滤肉眼不可见的浏览器噪点
        // 条件 1: 必须有足够的不透明度 (a >= 10)，过滤极弱的透明噪点
        // 条件 2: 不能是纯白色或极浅的灰色 (r, g, b <= 245)，过滤白纸背景
        if (a >= 10 && (r <= 245 || g <= 245 || b <= 245)) {
          // 只要找到一个满足条件的“有效笔触像素”，立刻判定为非空！
          isEmpty = false
          break
        }
      }
      
      resolve(isEmpty)
    }
    
    img.onerror = () => resolve(true)
    img.src = base64
  })
}

export function usePromptPolish() {
  const store = useBoardStore()

  const autoPolishPrompt = async (text) => {
    if (!text) return ''
    
    const hasChinese = /[\u4e00-\u9fa5]/.test(text)
    if (!hasChinese) return text 

    try {
      console.log('🔍 检测到中文，正在呼叫大模型进行自动润色...')
      const enhancedText = await polishPromptAPI(text)
      store.promptText = enhancedText 
      return enhancedText
    } catch (error) {
      // 💯 严格遵循文档：捕获 408 超时异常，使用 ElMessage.warning 提示，并默默降级使用原词
      if (error.isTimeout) {
        console.warn('⚠️ 触发文档规定的 408 降级策略:', error.message)
        ElMessage.warning('提示词润色服务超时，将携带原词强行施法！')
      } else {
        console.warn('⚠️ 润色异常，触发降级:', error.message)
      }
      return text 
    }
  }

  const handlePolish = async () => {
    if (!store.promptText) {
      return ElMessage.warning('请先输入基础提示词')
    }

    const loadingMsg = ElMessage({ 
      message: '✨ 魔法润色中，请稍候...', 
      type: 'info', 
      duration: 0 
    })

    try {
      const enhancedText = await polishPromptAPI(store.promptText)
      store.promptText = enhancedText 
      loadingMsg.close()
      ElMessage.success('润色成功！')
    } catch (error) {
      loadingMsg.close()
      // 手动点击如果超时，给出友好的警告
      if (error.isTimeout) {
        ElMessage.warning('大模型润色超时，您可以直接点击生成按钮使用原词施法。')
      } else {
        ElMessage.error(error.message)
      }
    }
  }

  return {
    handlePolish,
    autoPolishPrompt
  }
}