<template>
  <div class="canvas-board" ref="containerRef">

    <v-stage
      ref="stageRef"
      :config="stageConfig"
      :style="{ cursor: getStageCursor() }"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @mouseleave="handleMouseLeave"
      @touchstart="handleMouseDown"
      @touchmove="handleMouseMove"
      @touchend="handleMouseUp"
      @wheel="handleWheel"
      @dragend="handleDragEnd"
    >
      <v-layer ref="backgroundLayerRef" :config="{ id: 'background-layer', listening: false }">
        <v-rect
          :config="{
            id: 'solid-white-bg',
            x: 0,
            y: 0,
            width: store.canvasWidth,
            height: store.canvasHeight,
            fill: '#ffffff',
            shadowColor: 'rgba(0, 0, 0, 0.2)',
            shadowBlur: 30,
            shadowOffsetX: 0,
            shadowOffsetY: 15,
            listening: false
          }"
        />
      </v-layer>
      
      <v-layer ref="userDrawLayerRef" :config="{ id: 'user-draw-layer' }">
        </v-layer>
      
      <v-layer ref="systemOverlayRef" :config="{ id: 'system-mask-overlay', listening: false }"></v-layer>
      <v-layer ref="transformerLayerRef" :config="{ id: 'transformer-layer' }"></v-layer>
    </v-stage>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue' 
import { useBoardStore } from '../../stores/boardStore'
import { getStroke } from 'perfect-freehand'
import Konva from 'konva' 

const store = useBoardStore()
const isDrawing = ref(false)
const stageRef = ref(null) 
const userDrawLayerRef = ref(null)
const systemOverlayRef = ref(null)
const transformerLayerRef = ref(null)

const containerRef = ref(null)
const stageWidth = ref(window.innerWidth)
const stageHeight = ref(window.innerHeight)
let resizeObserver = null
let isInitialized = false 

let transformerNode = null 

// 动态光标
const getStageCursor = () => {
  if (store.isPlacingImage) return 'move'
  if (store.workMode === 'refine') return 'crosshair'
  if (store.activeTool === 'move') return 'move'
  return 'default'
}

const syncLayersToKonva = (newLayers) => {
  if (!userDrawLayerRef.value) return
  const drawLayer = userDrawLayerRef.value.getNode()

  const existingGroups = drawLayer.find('.user-group')
  const newLayerIds = newLayers.map(l => 'user-group-' + l.id)

  existingGroups.forEach(group => {
    if (!newLayerIds.includes(group.id())) {
      const children = group.getChildren().slice()
      children.forEach(child => child.remove()) 
      group.destroy()
    }
  })

  newLayers.forEach((layerData, index) => {
    const groupId = 'user-group-' + layerData.id
    let group = drawLayer.findOne('#' + groupId)
    if (!group) {
      group = new Konva.Group({ id: groupId, name: 'user-group' })
      drawLayer.add(group)
    }
    group.setAttrs({
      visible: layerData.visible,
      opacity: layerData.opacity / 100,
      clipX: 0, clipY: 0, clipWidth: store.canvasWidth, clipHeight: store.canvasHeight
    })
    // 强制更新层级
    group.setZIndex(index) 
  })

  // 🌟 核心修复：无论用户图层怎么排列，永远把实体白纸按在最底层 (Z-Index: 0)
  const bgRect = drawLayer.findOne('#solid-white-bg')
  if (bgRect) {
    bgRect.moveToBottom()
  }

  if (systemOverlayRef.value) {
    const sysLayer = systemOverlayRef.value.getNode()
    sysLayer.setAttrs({
      clipX: 0, clipY: 0, clipWidth: store.canvasWidth, clipHeight: store.canvasHeight
    })
    sysLayer.moveToTop()
  }

  if (transformerLayerRef.value && !transformerNode) {
    const trLayer = transformerLayerRef.value.getNode()
    transformerNode = new Konva.Transformer({
      anchorSize: 10, anchorCornerRadius: 5, anchorStroke: '#3b82f6',
      anchorFill: '#ffffff', borderStroke: '#3b82f6', keepRatio: true 
    })
    trLayer.add(transformerNode)
    trLayer.moveToTop()
  }
}

const redrawCanvas = () => {
  if (!userDrawLayerRef.value) return
  const drawLayer = userDrawLayerRef.value.getNode()

  store.uiLayers.forEach(layerData => {
    const group = drawLayer.findOne('#user-group-' + layerData.id)
    if (group) {
      if (layerData.imageSrc) {
        const kImg = store.nativeImagesMap.get(layerData.id)
        if (kImg) {
          // 强制注入混合模式，确保底层属性生效
          const targetBlend = layerData.blendMode || (store.workMode === 'draft' ? 'multiply' : 'source-over')
          kImg.setAttrs({
            globalCompositeOperation: targetBlend
          })

          if (kImg.getParent() !== group) {
            const currentChildren = group.getChildren().slice()
            currentChildren.forEach(child => child.remove())
            group.add(kImg)
          }
          group.getLayer()?.batchDraw()
        }
      } else {
        const lines = store.nativeLinesMap.get(layerData.id) || []
        const currentChildren = group.getChildren().slice()
        currentChildren.forEach(child => child.remove())
        
        lines.forEach(node => {
          node.globalCompositeOperation(layerData.blendMode)
          group.add(node)
        })
      }
    }
  })
  drawLayer.batchDraw()

  if (systemOverlayRef.value) {
    const sysLayer = systemOverlayRef.value.getNode()
    const overlayChildren = sysLayer.getChildren().slice()
    overlayChildren.forEach(child => child.remove())
    
    const currentMasks = store.nativeMasksMap.get(store.activeLayerId) || []
    currentMasks.forEach(node => sysLayer.add(node))
    sysLayer.batchDraw()
  }

  if (transformerLayerRef.value) {
    transformerLayerRef.value.getNode().moveToTop()
  }
}

const loadImages = () => {
  store.uiLayers.forEach(layerData => {
    if (layerData.imageSrc && !store.nativeImagesMap.has(layerData.id)) {
      const img = new window.Image()
      img.crossOrigin = 'anonymous' 
      img.onload = () => {
        const kImg = new Konva.Image({
          image: img,
          x: layerData.x || 0,
          y: layerData.y || 0,
          scaleX: layerData.scaleX || 1,
          scaleY: layerData.scaleY || 1,
          rotation: layerData.rotation || 0,
          name: `image-${layerData.id}`,
          globalCompositeOperation: layerData.blendMode
        })

        kImg.on('dragend', (e) => store.updateLayerTransform(layerData.id, { x: e.target.x(), y: e.target.y() }))
        kImg.on('transformend', (e) => {
          store.updateLayerTransform(layerData.id, {
            x: e.target.x(), y: e.target.y(), scaleX: e.target.scaleX(), scaleY: e.target.scaleY(), rotation: e.target.rotation()
          })
        })

        kImg.on('mousedown touchstart', () => {
          if ((store.activeTool === 'move' || store.isPlacingImage) && !layerData.locked) {
            store.activeLayerId = layerData.id
          }
        })

        store.nativeImagesMap.set(layerData.id, kImg)
        redrawCanvas()
        updateTransformer()
      }
      img.src = layerData.imageSrc
    }
  })
}

const updateTransformer = () => {
  if (!transformerLayerRef.value || !transformerNode) return
  const trLayer = transformerLayerRef.value.getNode()

  store.uiLayers.forEach(l => {
    const kImg = store.nativeImagesMap.get(l.id)
    if (kImg) {
      const isDraggable = (store.activeTool === 'move' || store.isPlacingImage) && !l.locked && store.activeLayerId === l.id
      kImg.draggable(isDraggable)
    }
  })

  const activeLayer = store.activeLayer
  if (activeLayer && activeLayer.imageSrc && (store.activeTool === 'move' || store.isPlacingImage) && !activeLayer.locked) {
    const kImg = store.nativeImagesMap.get(activeLayer.id)
    if (kImg) {
      transformerNode.nodes([kImg])
    } else {
      transformerNode.nodes([])
    }
  } else {
    transformerNode.nodes([])
  }
  trLayer.batchDraw()
}

onMounted(() => {
  if (containerRef.value) {
    resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect
      stageWidth.value = width
      stageHeight.value = height
      
      if (!isInitialized && width > 0 && height > 0) {
        store.centerCanvas(width, height)
        isInitialized = true
        syncLayersToKonva(store.layers) 
        loadImages()
      }
    })
    resizeObserver.observe(containerRef.value)
  }

  store.setCanvasExtractors({
    getMergedBase64,
    getLineartBase64,
    getColorBase64,
    getMaskBase64: () => extractMaskImage(store.activeLayerId)
  })
})

onUnmounted(() => {
  if (resizeObserver) resizeObserver.disconnect()
})

const stageConfig = computed(() => ({ 
  width: stageWidth.value, height: stageHeight.value, x: store.stageX, y: store.stageY, scaleX: store.stageScale, scaleY: store.stageScale, rotation: store.stageRotation, draggable: store.activeTool === 'hand' 
}))

watch(() => store.layers, (newLayers) => {
  if (isInitialized) {
    syncLayersToKonva(newLayers)
    loadImages()
    updateTransformer()
  }
}, { deep: true }) 

watch(() => [store.activeTool, store.activeLayerId, store.isPlacingImage], () => {
  if (isInitialized) updateTransformer()
})

watch(() => store.workMode, () => {
  if (isInitialized) redrawCanvas()
})

const handleDragEnd = (e) => {
  if (store.activeTool !== 'hand') return
  const stage = e.target.getStage()
  store.stageX = stage.x()
  store.stageY = stage.y()
}

const handleWheel = (e) => {
  e.evt.preventDefault() 
  const stage = stageRef.value.getNode()
  const oldScale = store.stageScale
  const pointer = stage.getPointerPosition()
  if (!pointer) return
  const mousePointTo = { x: (pointer.x - stage.x()) / oldScale, y: (pointer.y - stage.y()) / oldScale }
  const scaleBy = 1.1
  const direction = e.evt.deltaY > 0 ? -1 : 1
  const newScale = direction > 0 ? oldScale * scaleBy : oldScale / scaleBy
  if (newScale < 0.1 || newScale > 10) return
  const newPos = { x: pointer.x - mousePointTo.x * newScale, y: pointer.y - mousePointTo.y * newScale }
  store.stageScale = newScale
  store.stageX = newPos.x
  store.stageY = newPos.y
}

const updateThumbnail = () => {
  const activeId = store.activeLayerId
  if (!stageRef.value) return
  const stage = stageRef.value.getNode()
  const nativeGroup = stage.findOne('#user-group-' + activeId)
  if (nativeGroup) {
    const ratio = 64 / store.canvasWidth 
    const targetLayerData = store.layers.find(l => l.id === activeId)
    
    if (transformerLayerRef.value) transformerLayerRef.value.getNode().hide()
    if (targetLayerData) targetLayerData.thumbnail = nativeGroup.toDataURL({ pixelRatio: ratio })
    if (transformerLayerRef.value) transformerLayerRef.value.getNode().show()
  }
}

// 导出拦截
const exportImage = () => {
  if (!stageRef.value) return
  const stage = stageRef.value.getNode()
  const oldScale = stage.scaleX()
  const oldX = stage.x()
  const oldY = stage.y()

  if (systemOverlayRef.value) systemOverlayRef.value.getNode().hide()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().hide() 

  stage.scale({ x: 1, y: 1 })
  stage.position({ x: 0, y: 0 })

  const dataURL = stage.toDataURL({ x: 0, y: 0, width: store.canvasWidth, height: store.canvasHeight, pixelRatio: 3, mimeType: 'image/png' })

  stage.scale({ x: oldScale, y: oldScale })
  stage.position({ x: oldX, y: oldY })
  
  if (systemOverlayRef.value) systemOverlayRef.value.getNode().show()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().show()

  const link = document.createElement('a')
  link.download = `MoBu_Artwork_${new Date().getTime()}.png`
  link.href = dataURL
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const getMergedBase64 = () => {
  const stage = stageRef.value.getNode()
  if (systemOverlayRef.value) systemOverlayRef.value.getNode().hide()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().hide() 
  const dataURL = stage.toDataURL({ pixelRatio: 1, mimeType: 'image/png' })
  if (systemOverlayRef.value) systemOverlayRef.value.getNode().show()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().show()
  return dataURL
}

const getLineartBase64 = () => {
  const stage = stageRef.value.getNode()
  if (store.uiLayers.length === 0) return null
  const lineartLayerId = store.uiLayers[0].id 
  
  store.uiLayers.forEach(l => {
    const node = stage.findOne('#user-group-' + l.id)
    if (node) l.id === lineartLayerId ? node.show() : node.hide()
  })
  
  if (systemOverlayRef.value) systemOverlayRef.value.getNode().hide()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().hide() 
  const dataURL = stage.toDataURL({ pixelRatio: 1, mimeType: 'image/png' })

  store.uiLayers.forEach(l => {
    const node = stage.findOne('#user-group-' + l.id)
    if (node && l.visible) node.show()
    else if (node && !l.visible) node.hide()
  })
  if (systemOverlayRef.value) systemOverlayRef.value.getNode().show()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().show()
  return dataURL
}

const getColorBase64 = () => {
  const stage = stageRef.value.getNode()
  if (store.uiLayers.length < 2) return null 
  
  const lineartLayerId = store.uiLayers[0].id
  
  store.uiLayers.forEach(l => {
    const node = stage.findOne('#user-group-' + l.id)
    if (node) l.id === lineartLayerId ? node.hide() : (l.visible ? node.show() : node.hide())
  })
  
  if (systemOverlayRef.value) systemOverlayRef.value.getNode().hide()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().hide() 
  const dataURL = stage.toDataURL({ pixelRatio: 1, mimeType: 'image/png' })

  store.uiLayers.forEach(l => {
    const node = stage.findOne('#user-group-' + l.id)
    if (node && l.visible) node.show()
    else if (node && !l.visible) node.hide()
  })
  if (systemOverlayRef.value) systemOverlayRef.value.getNode().show()
  if (transformerLayerRef.value) transformerLayerRef.value.getNode().show()
  return dataURL
}

const extractMaskImage = (layerId) => {
  const masks = store.nativeMasksMap.get(layerId) || []
  if (masks.length === 0) return null

  const offscreenContainer = document.createElement('div')
  const offscreenStage = new Konva.Stage({ container: offscreenContainer, width: store.canvasWidth, height: store.canvasHeight })
  const offscreenLayer = new Konva.Layer()
  offscreenStage.add(offscreenLayer)

  const bgRect = new Konva.Rect({ x: 0, y: 0, width: store.canvasWidth, height: store.canvasHeight, fill: '#000000' })
  offscreenLayer.add(bgRect)

  masks.forEach(maskNode => {
    const maskClone = maskNode.clone()
    const isEraser = maskNode.globalCompositeOperation() === 'destination-out'
    maskClone.setAttrs({ stroke: isEraser ? '#000000' : '#FFFFFF', opacity: 1, globalCompositeOperation: 'source-over' })
    offscreenLayer.add(maskClone)
  })

  offscreenLayer.draw()
  const maskDataURL = offscreenStage.toDataURL({ mimeType: 'image/png', pixelRatio: 1 })
  offscreenStage.destroy()
  return maskDataURL
}

defineExpose({ exportImage, updateThumbnail, redrawCanvas, extractMaskImage })

const flatToPairs = (flatArr) => { const pairs = []; for (let i = 0; i < flatArr.length; i += 2) { pairs.push([flatArr[i], flatArr[i + 1]]) }; return pairs }
const getSvgPathFromStroke = (stroke) => { if (!stroke.length) return ''; const d = stroke.reduce((acc, [x0, y0], i, arr) => { const [x1, y1] = arr[(i + 1) % arr.length]; acc.push(x0, y0, (x0 + x1) / 2, (y0 + y1) / 2); return acc }, ['M', ...stroke[0], 'Q']); d.push('Z'); return d.join(' ') }
const getPointerPos = (e) => { const stage = e.target.getStage(); if (e.evt && e.evt.touches && e.evt.touches.length > 0) { stage.setPointersPositions(e.evt) }; const pos = stage.getPointerPosition(); if (!pos) return { x: 0, y: 0 }; const transform = stage.getAbsoluteTransform().copy(); transform.invert(); return transform.point(pos) }

let currentShape = null 
let currentPoints = []  
let startX = 0
let startY = 0

const handleMouseDown = (e) => {
  if (store.isPlacingImage || store.activeTool === 'hand' || store.activeTool === 'move') return 

  const activeLayer = store.activeLayer
  if (!activeLayer || activeLayer.locked || !activeLayer.visible) return

  const stage = stageRef.value.getNode()
  const isRefineMode = store.workMode === 'refine'
  let targetNativeLayer;

  if (isRefineMode) {
    targetNativeLayer = stage.findOne('#system-mask-overlay')
  } else {
    targetNativeLayer = stage.findOne('#user-group-' + store.activeLayerId)
  }
  if (!targetNativeLayer) return

  isDrawing.value = true
  const pos = getPointerPos(e) 
  
  startX = pos.x
  startY = pos.y
  currentPoints = [pos.x, pos.y, pos.x, pos.y]

  const isEraser = store.activeTool === 'eraser'
  let size, opacity, color, globalCompositeOperation;
  
  if (isRefineMode) {
    size = isEraser ? store.eraserSize : store.maskBrushSize
    globalCompositeOperation = isEraser ? 'destination-out' : 'source-over'
    opacity = isEraser ? 1 : 0.4
    color = '#ff0000'
  } else {
    size = isEraser ? store.eraserSize : store.brushSize
    opacity = isEraser ? (store.eraserOpacity / 100) : (store.brushOpacity / 100)
    color = store.brushColor
    globalCompositeOperation = isEraser ? 'destination-out' : activeLayer.blendMode
  }

  if (store.activeTool === 'shape') {
    if (store.activeShape === 'line') currentShape = new Konva.Line({ points: currentPoints, stroke: color, strokeWidth: size, opacity, lineCap: 'round', lineJoin: 'round', globalCompositeOperation })
    else if (store.activeShape === 'square') currentShape = new Konva.Rect({ x: startX, y: startY, width: 0, height: 0, stroke: color, strokeWidth: size, opacity, globalCompositeOperation })
    else if (store.activeShape === 'circle') currentShape = new Konva.Circle({ x: startX, y: startY, radius: 0, stroke: color, strokeWidth: size, opacity, globalCompositeOperation })
    else if (store.activeShape === 'polygon') currentShape = new Konva.RegularPolygon({ x: startX, y: startY, sides: store.polygonSides, radius: 0, stroke: color, strokeWidth: size, opacity, globalCompositeOperation })
  } else {
    if (store.activeBrush === 'willow' && !isRefineMode) { 
      const stroke = getStroke(flatToPairs(currentPoints), { size, thinning: 0.6, smoothing: 0.5, streamline: 0.5 })
      currentShape = new Konva.Path({ data: getSvgPathFromStroke(stroke), fill: color, opacity, globalCompositeOperation })
    } else {
      const tension = isRefineMode ? 0.5 : (store.activeBrush === 'pencil' ? 0 : 0.5)
      currentShape = new Konva.Line({ points: currentPoints, stroke: color, strokeWidth: size, opacity, tension, lineCap: 'round', lineJoin: 'round', globalCompositeOperation })
    }
  }

  if (currentShape) {
    targetNativeLayer.add(currentShape)
    
    if (isRefineMode) {
      const masks = store.nativeMasksMap.get(store.activeLayerId) || []
      masks.push(currentShape)
      store.nativeMasksMap.set(store.activeLayerId, masks)
      if (store.nativeMasksRedoMap) store.nativeMasksRedoMap.set(store.activeLayerId, [])
    } else {
      const lines = store.nativeLinesMap.get(store.activeLayerId) || []
      lines.push(currentShape)
      store.nativeLinesMap.set(store.activeLayerId, lines)
      if (store.nativeRedoMap) store.nativeRedoMap.set(store.activeLayerId, [])
    }
    targetNativeLayer.getLayer().batchDraw()
  }
}

const handleMouseMove = (e) => {
  if (!isDrawing.value || store.isPlacingImage || store.activeTool === 'hand' || store.activeTool === 'move' || !currentShape) return 
  
  const activeLayer = store.activeLayer
  if (!activeLayer || activeLayer.locked || !activeLayer.visible) {
    isDrawing.value = false; currentShape = null; return
  }

  const stage = stageRef.value.getNode()
  const isRefineMode = store.workMode === 'refine'
  const targetNativeLayer = isRefineMode 
    ? stage.findOne('#system-mask-overlay') 
    : stage.findOne('#user-group-' + store.activeLayerId)

  if (!targetNativeLayer) return

  const pos = getPointerPos(e)

  if (store.activeTool === 'shape') {
    if (store.activeShape === 'line') currentShape.points([startX, startY, pos.x, pos.y])
    else if (store.activeShape === 'square') { currentShape.x(Math.min(startX, pos.x)); currentShape.y(Math.min(startY, pos.y)); currentShape.width(Math.abs(pos.x - startX)); currentShape.height(Math.abs(pos.y - startY)) }
    else if (store.activeShape === 'circle' || store.activeShape === 'polygon') { const radius = Math.sqrt(Math.pow(pos.x - startX, 2) + Math.pow(pos.y - startY, 2)); currentShape.radius(radius) }
  } else {
    currentPoints.push(pos.x, pos.y)
    if (store.activeTool === 'brush' && store.activeBrush === 'willow' && !isRefineMode) {
      const isEraser = store.activeTool === 'eraser'
      const size = isEraser ? store.eraserSize : store.brushSize
      const stroke = getStroke(flatToPairs(currentPoints), { size, thinning: 0.7, smoothing: 0.5, streamline: 0.5 })
      currentShape.data(getSvgPathFromStroke(stroke)) 
    } else {
      currentShape.points(currentPoints) 
    }
  }

  targetNativeLayer.getLayer().batchDraw()
}

const handleMouseUp = () => { 
  if (isDrawing.value) updateThumbnail()
  isDrawing.value = false 
  currentShape = null
  currentPoints = []
}

const handleMouseLeave = () => { 
  if (isDrawing.value) updateThumbnail()
  isDrawing.value = false 
  currentShape = null
  currentPoints = []
}
</script>

<style scoped>
.canvas-board { 
  width: 100%; 
  height: 100%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  user-select: none; 
  -webkit-user-select: none; 
  touch-action: none; 
  position: relative; 
}

</style>