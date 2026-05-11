/**
 * src/utils/aiLayerManager.js
 * 核心引擎：AI 生成结果的安全注入与图层管理
 */
import { ElMessage, ElLoading } from 'element-plus'

/**
 * 将后端返回的图片 URL 安全地作为新图层注入到画布中
 * @param {String} imageUrl - 后端返回的图片 URL
 * @param {Object} store - Pinia 的 boardStore 实例
 */
export const injectAILayerFromUrl = async (imageUrl, store) => {
  if (!imageUrl) return

  // 开启全屏防抖 Loading，防止用户在图片下载期间乱点
  const loading = ElLoading.service({
    lock: true,
    text: '正在将 AI 杰作解析为高清图层...',
    background: 'rgba(255, 255, 255, 0.8)',
  })

  try {
    // ==========================================
    // 第一道防线：将外部 URL 强制转为本地 Blob，彻底粉碎跨域污染 (Tainted Canvas) 危机
    // 注意：这要求你的后端 OSS 配置了允许跨域的 CORS Header (Access-Control-Allow-Origin: *)
    // ==========================================
    const response = await fetch(imageUrl, {
      mode: 'cors', // 强制跨域请求
      cache: 'no-cache'
    })

    if (!response.ok) {
      throw new Error(`图片抓取失败: HTTP状态码 ${response.status}`)
    }

    const imageBlob = await response.blob()

    // ==========================================
    // 第二道防线：Blob 转 Base64 字符串
    // 统一数据格式，保证 Store 里无论是本地导入还是 AI 生成，全是安全的 Base64
    // ==========================================
    const base64Image = await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result)
      reader.onerror = reject
      reader.readAsDataURL(imageBlob)
    })

    // ==========================================
    // 核心流转：与 Pinia 状态机进行“握手”
    // ==========================================
    
    // 1. 调用 Store 的方法新建一个物理图层
    store.addLayer('✨ AI 生成结果')
    
    // 2. 此时 store.activeLayerId 已经被 addLayer 自动切到了最新图层
    const newLayerId = store.activeLayerId
    const targetLayer = store.layers.find(l => l.id === newLayerId)

    if (targetLayer) {
      // 3. 极其精准的数据覆写：植入图像，并赋予默认物理属性
      const autoBlendMode = store.workMode === 'draft' ? 'Multiply' : 'source-over'
      Object.assign(targetLayer, {
        imageSrc: base64Image,
        x: 0,
        y: 0,
        scaleX: 1,
        scaleY: 1,
        rotation: 0,
        isLocked: false,
        blendMode: autoBlendMode
      })

      // 4. 强行将用户的工具切为 'move' (移动工具)，
      // 这样用户一看到新图层，就能立刻点击它出现控制框，进行缩放排版
      store.activeTool = 'move'
      store.isPlacingImage = true
      ElMessage.success({
        message: '图层注入成功！已自动为您切换至移动工具',
        type: 'success',
        duration: 3000
      })
    } else {
      throw new Error('图层状态机寻址失败')
    }

  } catch (error) {
    console.error('【AI 图层注入灾难】:', error)
    ElMessage.error(`图层注入失败: ${error.message || '网络或跨域受限'}`)
  } finally {
    // 必须释放 Loading 线程
    loading.close()
  }
}