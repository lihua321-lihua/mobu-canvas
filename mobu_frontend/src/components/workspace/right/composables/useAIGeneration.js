import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { submitGenerateTaskAPI, createSSEConnection } from '../services/aiService'
import { usePromptPolish, isEmptyCanvas } from './usePromptPolish'
import { injectAILayerFromUrl } from '../../../../utils/aiLayerManager'
import { useBoardStore } from '../../../../stores/boardStore'

export function useAIGeneration() {
  const store = useBoardStore()
  const extractors = computed(() => store.canvasExtractors)
  const { autoPolishPrompt } = usePromptPolish()

  const handleMegaGenerate = async () => {
    if (!store.promptText) {
      return ElMessage.warning('请描述你想要的画面')
    }

    store.isAIGenerating = true
    store.generateProgress = 0

    try {
      const finalPrompt = await autoPolishPrompt(store.promptText)

      const payload = {
        prompt: finalPrompt,
        // 🌟 MOCK 调试开关：指定返回的本地图片数组。
        // 注释掉下面这行，即可恢复真实的 ComfyUI 生图！
       // mock_image_urls: ['/chuntian2.png','/chuntian3.png']
      }

      switch (store.workMode) {
        // 🎯 修复核心：构思线稿 (Draft)
        case 'draft': 
          payload.mode = 'sketch'
          const draftBaseImage = extractors.value.getLineartBase64() || ""
          const isDraftEmpty = await isEmptyCanvas(draftBaseImage)
          payload.base_image = isDraftEmpty ? "" : draftBaseImage
          break
        // 氛围铺色 (Color) - 必须要有线稿
        case 'color':
          payload.mode = 'color' 
          const lineartImage = extractors.value.getLineartBase64() || ""
          const colorImage = extractors.value.getColorBase64() || ""
          if (await isEmptyCanvas(lineartImage)) {
            throw new Error('422: 未检测到有效的线稿图层，无法进行氛围铺色！')
          }
          payload.lineart_image = lineartImage
          payload.color_image = colorImage
          break

        // 局部精修 (Refine) - 必须要有遮罩
        case 'refine':
          payload.mode = 'inpaint'
          const originImage = extractors.value.getMergedBase64() || ""
          const maskImage = extractors.value.getMaskBase64() || ""
          if (await isEmptyCanvas(maskImage)) {
            throw new Error('422: 未检测到涂抹区域，请先使用魔法棒涂抹修补范围！')
          }
          payload.base_image = originImage
          payload.mask_image = maskImage
          break

        default:
          throw new Error('未知的空间维度，无法施法！')
      }

      console.log('✅ Payload 组装完毕，准备发射:', payload)

      const taskData = await submitGenerateTaskAPI(payload)
      const { client_id, prompt_id } = taskData

      ElMessage.success('施法请求已发送，正在建立 SSE 长连接...')

      const sseController = createSSEConnection(client_id, prompt_id, {
        onProgress: (data) => {
          store.generateProgress = data.progress
        },
        // 🌟 将回调改为 async，以便等待图片转码注入
        onCompleted: async (data) => {
          // 1. 打印完整的 data 对象，彻底看清后端发了什么！
          console.log('🎉 收到完整的完成数据包:', data)
          
          sseController.close()
          store.isAIGenerating = false
          store.generateProgress = 100
          
          // 2. 🛡️ 终极防御兼容逻辑：智能寻找图片 URL
          let finalUrls = []
          
          if (data.image_urls && Array.isArray(data.image_urls)) {
            finalUrls = data.image_urls
          } else if (data.image_urls && typeof data.image_urls === 'string') {
            finalUrls = [data.image_urls]
          } else if (data.image_url) {
            finalUrls = [data.image_url]
          } else {
            console.error('❌ 致命错误：在后端返回的数据中找不到任何图片字段！', data)
            return ElMessage.error('生图完成，但前端未能提取到图片地址！')
          }

          // 3. 将兼容处理后的数组存入 Store，供 Gallery 渲染
          store.latestResultImageUrls = finalUrls 
          
          ElMessage.success('✨ 画作生成完成！即将导入画布...')
        },
        onError: (errorData) => {
          console.error('SSE Error:', errorData)
          sseController.close()
          store.isAIGenerating = false
          store.generateProgress = 0
          ElMessage.error(errorData.message || 'AI 引擎生成出错，请重试')
        }
      })

    } catch (error) {
      store.isAIGenerating = false 
      store.generateProgress = 0
      
      if (error.message.includes('422') || error.message.includes('未检测到')) {
        ElMessage.warning(error.message.replace('422: ', ''))
      } else {
        ElMessage.error(error.message || '系统发生未知异常，请检查控制台')
      }
    }
  }

  return {
    handleMegaGenerate
  }
}