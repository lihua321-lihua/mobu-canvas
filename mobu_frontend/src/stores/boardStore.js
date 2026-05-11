import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useBoardStore = defineStore('board', () => {
  const canvasWidth = ref(1080)
  const canvasHeight = ref(1920)

  const stageX = ref(0)          
  const stageY = ref(0)          
  const stageScale = ref(1)      
  const stageRotation = ref(0)   

  const activeTool = ref('brush') 
  const activeBrush = ref('pencil') 
  const brushSize = ref(5)        
  const brushOpacity = ref(100)     
  const brushColor = ref('#000000') 

  const eraserSize = ref(20)      
  const eraserOpacity = ref(100)  

  const activeShape = ref('line') 
  const polygonSides = ref(5)     

  const maskBrushSize = ref(40)

  const isAIGenerating = ref(false)       
  const isAIConsoleCollapsed = ref(false) 
  const currentStage = ref(1)             
  const promptText = ref('')              
  
  const workMode = ref('draft')  
  
  const canvasExtractors = ref(null)
  const latestResultImageUrls = ref([])
  const generateProgress = ref(0) 

  // 🌟 架构师新增：图片排版专属状态
  const isPlacingImage = ref(false)

  const setCanvasExtractors = (extractors) => {
    canvasExtractors.value = extractors
  }

  // 状态机拦截器
  watch(() => workMode.value, (newMode) => {
    if (newMode === 'refine') {
      if (activeTool.value !== 'eraser' && activeTool.value !== 'hand' && activeTool.value !== 'move') {
        activeTool.value = 'inpainting'
      }
    } else {
      if (activeTool.value === 'inpainting') {
        activeTool.value = 'brush'
      }
      if (activeLayerId.value) {
        nativeMasksMap.set(activeLayerId.value, [])
        nativeMasksRedoMap.set(activeLayerId.value, [])
      }
    }
  })

  let layerCounter = 1 

  const layers = ref([
    { id: 'bg', name: '⬜ 背景层', visible: true, locked: true, opacity: 100, blendMode: 'source-over', thumbnail: '', isSystem: true },
    { id: 'layer-1', name: '图层 1', visible: true, locked: false, opacity: 100, blendMode: 'source-over', thumbnail: '', isSystem: false }
  ])

  const activeLayerId = ref('layer-1')

  const uiLayers = computed(() => layers.value.filter(l => !l.isSystem))
  const activeLayer = computed(() => layers.value.find(l => l.id === activeLayerId.value))

  const nativeLinesMap = new Map()
  const nativeRedoMap = new Map()
  const nativeMasksMap = new Map()
  const nativeMasksRedoMap = new Map()
  const nativeImagesMap = new Map()

  // 初始化基础 Map
  const initMaps = (id) => {
    nativeLinesMap.set(id, [])
    nativeRedoMap.set(id, [])
    nativeMasksMap.set(id, [])
    nativeMasksRedoMap.set(id, [])
  }
  initMaps('bg')
  initMaps('layer-1')

  // 🌟 架构师新增：高度封装的“导入并排版”初始化动作
  const initImportedImage = (base64Image, width, height) => {
    canvasWidth.value = width
    canvasHeight.value = height

    nativeLinesMap.clear()
    nativeRedoMap.clear()
    nativeMasksMap.clear()
    nativeMasksRedoMap.clear()
    nativeImagesMap.forEach(img => img.destroy())
    nativeImagesMap.clear()

    layerCounter = 1
    const newId = 'layer-1'
    
    initMaps('bg')
    initMaps(newId)

    layers.value = [
      { id: 'bg', name: '⬜ 背景层', visible: true, locked: true, opacity: 100, blendMode: 'source-over', thumbnail: '', isSystem: true },
      { id: newId, name: '图层 1 (底图)', visible: true, locked: false, opacity: 100, blendMode: 'source-over', thumbnail: '', isSystem: false, imageSrc: base64Image, x: 0, y: 0, scaleX: 1, scaleY: 1, rotation: 0 }
    ]

    activeLayerId.value = newId
    isPlacingImage.value = true 
    activeTool.value = 'move'   
  }

  // 🌟 架构师新增：确认固定图片，退出排版模式
  const confirmImagePlacement = () => {
    isPlacingImage.value = false
    activeTool.value = 'brush' 
  }

  // 存储智能体正在代笔执行的状态 (用于 UI 动画锁定)
  const isAgentExecuting = ref(false)

  /**
   * 核心调度器：解析来自 OpenClaw 智能体的 JSON 指令，执行“隔空操控”
   * @param {Object} payload 智能体返回的动作指令集
   */
  const dispatchAgentAction = async (payload) => {
    isAgentExecuting.value = true

    try {
      // 1. 幽灵代笔 (Ghostwriting)：静默替换 A 面的提示词输入框
      if (payload.prompt_override) {
        promptText.value = payload.prompt_override
      }

      // 2. 自动切挡 (Auto-Switching)：越权修改顶部的“构思/铺色/精修”模式
      if (payload.switch_tab) {
        workMode.value = payload.switch_tab
      }

      // 3. 资产隔离 (Layer Isolation)：自动显隐图层 (创新点二的核心落地)
      if (payload.hide_layer_ids && payload.hide_layer_ids.length > 0) {
        layers.value.forEach(layer => {
          if (payload.hide_layer_ids.includes(layer.id)) {
            layer.visible = false
          }
        })
      }

      // 4. 代为触发执行 (Trigger Generation)：
      if (payload.trigger_generate) {
        // 由于你的老代码中生图请求大概率写在 GenerateAction.vue 里，
        // 这里最优雅的零入侵做法是：只改变状态，让原有的逻辑去 Watch 这个状态，或者直接把 API 请求提上来。
        isAIGenerating.value = true 
        console.log('🖋️ [Agent Dispatcher] 墨意已注入，底层生图引擎触发...')
        // 如果你的生图 API (如 generateImage) 已经封装在 store 里，直接在这里 await 调用即可
      }
    } catch (error) {
      console.error('智能体代笔失败:', error)
    } finally {
      // 保持一定视觉延迟后释放执行状态，让水墨动画走完
      setTimeout(() => {
        isAgentExecuting.value = false
      }, 800)
    }
  }

  const addLayer = (customName = null) => {
    layerCounter++
    const newId = `layer-${layerCounter}`
    initMaps(newId)
    const newLayer = { id: newId, name: customName || `图层 ${layerCounter}`, visible: true, locked: false, opacity: 100, blendMode: 'source-over', thumbnail: '', isSystem: false }
    layers.value.push(newLayer)
    activeLayerId.value = newId 
  }

  // 🌟 架构师新增：图层重命名核心方法
  const renameLayer = (layerId, newName) => {
    const layer = layers.value.find(l => l.id === layerId)
    if (layer && newName.trim()) {
      layer.name = newName.trim()
    }
  }

  const cloneLayer = () => {
    if (!activeLayer.value || activeLayer.value.isSystem) return
    layerCounter++
    const newId = `layer-${layerCounter}`
    
    const currentLines = nativeLinesMap.get(activeLayerId.value) || []
    const clonedLines = JSON.parse(JSON.stringify(currentLines))
    
    initMaps(newId)
    nativeLinesMap.set(newId, clonedLines)
    
    const newLayer = { ...activeLayer.value, id: newId, name: `${activeLayer.value.name} 副本` }
    const index = layers.value.findIndex(l => l.id === activeLayerId.value)
    layers.value.splice(index + 1, 0, newLayer)
    activeLayerId.value = newId
  }

  const deleteLayer = (id) => {
    const index = layers.value.findIndex(l => l.id === id)
    if (index !== -1 && !layers.value[index].isSystem) {
      nativeLinesMap.delete(id)
      nativeRedoMap.delete(id) 
      nativeMasksMap.delete(id) 
      const konvaImg = nativeImagesMap.get(id)
      if (konvaImg) konvaImg.destroy()
      nativeImagesMap.delete(id)

      layers.value.splice(index, 1)
      const remainingUi = layers.value.filter(l => !l.isSystem)
      if (activeLayerId.value === id && remainingUi.length > 0) {
        activeLayerId.value = remainingUi[remainingUi.length - 1].id
      }
    }
  }

  const mergeDownLayer = () => {
    const index = layers.value.findIndex(l => l.id === activeLayerId.value)
    if (index > 1) { 
      const currentLayer = layers.value[index]
      const lowerLayer = layers.value[index - 1]
      if (lowerLayer.isSystem || currentLayer.locked || lowerLayer.locked) return
      
      const currentLines = nativeLinesMap.get(currentLayer.id) || []
      const lowerLines = nativeLinesMap.get(lowerLayer.id) || []
      nativeLinesMap.set(lowerLayer.id, [...lowerLines, ...currentLines])
      
      nativeRedoMap.set(lowerLayer.id, []) 
      nativeLinesMap.delete(currentLayer.id) 
      nativeRedoMap.delete(currentLayer.id) 
      nativeMasksMap.delete(currentLayer.id)
      
      const konvaImg = nativeImagesMap.get(currentLayer.id)
      if (konvaImg) konvaImg.destroy()
      nativeImagesMap.delete(currentLayer.id)

      lowerLayer.thumbnail = currentLayer.thumbnail
      layers.value.splice(index, 1)
      activeLayerId.value = lowerLayer.id
    }
  }

  const clearCanvas = () => {
    if (activeLayer.value && !activeLayer.value.locked) {
      if (workMode.value === 'refine') {
        nativeMasksMap.set(activeLayerId.value, [])
        nativeMasksRedoMap.set(activeLayerId.value, [])
      } else {
        if (activeLayer.value.imageSrc) {
          activeLayer.value.imageSrc = null
          const konvaImg = nativeImagesMap.get(activeLayerId.value)
          if (konvaImg) konvaImg.destroy()
          nativeImagesMap.delete(activeLayerId.value)
        }
        nativeLinesMap.set(activeLayerId.value, [])
        nativeRedoMap.set(activeLayerId.value, [])
        activeLayer.value.thumbnail = ''
      }
    }
  }
  
  const undo = () => {
    if (activeLayer.value && !activeLayer.value.locked) {
      if (workMode.value === 'refine') {
        const masks = nativeMasksMap.get(activeLayerId.value) || []
        const redos = nativeMasksRedoMap.get(activeLayerId.value) || []
        if (masks.length > 0) redos.push(masks.pop())
      } else {
        const lines = nativeLinesMap.get(activeLayerId.value) || []
        const redos = nativeRedoMap.get(activeLayerId.value) || []
        if (lines.length > 0) redos.push(lines.pop())
      }
    }
  }

  const redo = () => {
    if (activeLayer.value && !activeLayer.value.locked) {
      if (workMode.value === 'refine') {
        const masks = nativeMasksMap.get(activeLayerId.value) || []
        const redos = nativeMasksRedoMap.get(activeLayerId.value) || []
        if (redos.length > 0) masks.push(redos.pop())
      } else {
        const lines = nativeLinesMap.get(activeLayerId.value) || []
        const redos = nativeRedoMap.get(activeLayerId.value) || []
        if (redos.length > 0) lines.push(redos.pop())
      }
    }
  }

  const centerCanvas = (viewportWidth, viewportHeight) => {
    const padding = 60 
    const scaleX = (viewportWidth - padding * 2) / canvasWidth.value
    const scaleY = (viewportHeight - padding * 2) / canvasHeight.value
    const scale = Math.min(scaleX, scaleY, 1)
    stageScale.value = scale
    stageRotation.value = 0
    stageX.value = (viewportWidth - canvasWidth.value * scale) / 2
    stageY.value = (viewportHeight - canvasHeight.value * scale) / 2
  }

  const updateLayerTransform = (layerId, transformData) => {
    const layer = layers.value.find(l => l.id === layerId)
    if (layer) {
      Object.assign(layer, transformData)
    }
  }

  return {
    canvasWidth, canvasHeight, stageX, stageY, stageScale, stageRotation,
    activeTool, activeBrush, brushSize, brushOpacity, brushColor, eraserSize, eraserOpacity, activeShape, polygonSides, maskBrushSize, 
    isAIGenerating, isAIConsoleCollapsed, currentStage, promptText, workMode, 
    canvasExtractors, latestResultImageUrls, generateProgress,
    isPlacingImage,
    layers, uiLayers, activeLayerId, activeLayer, nativeLinesMap, nativeRedoMap, nativeMasksMap, nativeImagesMap, 
    addLayer, deleteLayer, clearCanvas, undo, redo, cloneLayer, mergeDownLayer, centerCanvas, setCanvasExtractors, updateLayerTransform,
    initImportedImage, confirmImagePlacement, renameLayer, // 🌟 抛出重命名方法
    isAgentExecuting, 
    dispatchAgentAction
  }
})