import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000'

/**
 * 魔法润色接口 (💯 严格对齐 v1.2 交接文档)
 */
export const polishPromptAPI = async (promptText) => {
  try {
    // 严格遵循文档：路径为 /api/v1/llm/polish-prompt，入参为 prompt
    const response = await axios.post(`${BASE_URL}/api/v1/llm/polish-prompt`, {
      prompt: promptText
    })

    // 严格遵循文档：校验 code === 200，提取 data.polishedPrompt
    if (response.data && response.data.code === 200) {
      return response.data.data.polishedPrompt 
    } else {
      throw new Error(response.data?.message || '润色失败，请重试')
    }
  } catch (error) {
    // 严格遵循文档：透传 408 超时状态码供业务层做降级处理
    if (error.response && error.response.status === 408) {
      const timeoutErr = new Error('大模型响应超时，请稍后重试')
      timeoutErr.isTimeout = true
      throw timeoutErr
    }
    console.error('润色接口报错详情:', error.response?.data)
    const errorMsg = error.response?.data?.message || error.message || '网络请求失败，请检查后端服务'
    throw new Error(errorMsg)
  }
}

/**
 * 提交 AI 生图任务接口 (💯 严格对齐 v1.2 交接文档)
 */
export const submitGenerateTaskAPI = async (payload) => {
  try {
    // 严格遵循文档：路径为 /api/v1/sd/generate
    const response = await axios.post(`${BASE_URL}/api/v1/sd/generate`, payload)

    // 严格遵循文档：校验 status === 'success'，返回包含 prompt_id 和 client_id
    if (response.data && response.data.status === 'success') {
      return response.data 
    } else {
      throw new Error(response.data?.message || '生成请求失败，请重试')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.message || error.message || '系统发生未知异常，请检查网络或控制台'
    throw new Error(errorMsg)
  }
}

/**
 * SSE 长连接工厂函数 (💯 严格对齐 v1.2 交接文档)
 */
export const createSSEConnection = (clientId, promptId, callbacks) => {
  // 严格遵循文档：GET /api/v1/sd/stream/{client_id}/{prompt_id}
  const url = `${BASE_URL}/api/v1/sd/stream/${clientId}/${promptId}`
  const eventSource = new EventSource(url)

  // 严格遵循文档：监听 progress、completed、error 事件
  eventSource.addEventListener('progress', (event) => {
    if (callbacks.onProgress) callbacks.onProgress(JSON.parse(event.data))
  })

  eventSource.addEventListener('completed', (event) => {
    if (callbacks.onCompleted) callbacks.onCompleted(JSON.parse(event.data))
  })

  eventSource.addEventListener('error', (event) => {
    if (callbacks.onError) {
      try {
        callbacks.onError(JSON.parse(event.data))
      } catch (e) {
        callbacks.onError(event)
      }
    }
  })

  eventSource.onerror = (err) => {
    if (callbacks.onError) callbacks.onError({ message: 'SSE 通信中断或连接失败', detail: err })
  }

  return {
    close: () => {
      eventSource.close()
      console.log(`[SSE] 连接已安全销毁: ${promptId}`)
    }
  }
}