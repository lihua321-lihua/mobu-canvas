<template>
  <v-group>
    <v-image
      ref="imageNodeRef"
      :config="imageConfig"
      @dragend="handleDragEnd"
      @transformend="handleTransformEnd"
      @mousedown="handleSelect"
      @touchstart="handleSelect"
    />
    <v-transformer
      ref="transformerNodeRef"
      v-if="shouldShowTransformer"
      :config="transformerConfig"
    />
  </v-group>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useBoardStore } from '@/stores/boardStore'

const props = defineProps({
  layer: {
    type: Object,
    required: true
  }
})

const store = useBoardStore()

// Konva 节点引用
const imageNodeRef = ref(null)
const transformerNodeRef = ref(null)

// 原生 HTML Image 实例
const htmlImageObj = ref(null)

// ==========================================
// 1. 异步加载 Base64 图片
// ==========================================
const loadImage = () => {
  if (!props.layer.imageSrc) return
  const img = new window.Image()
  // 生产级防御：彻底杜绝 Tainted Canvas 跨域污染崩溃
  img.crossOrigin = 'anonymous' 
  img.onload = () => {
    htmlImageObj.value = img
  }
  img.src = props.layer.imageSrc
}

onMounted(() => loadImage())
watch(() => props.layer.imageSrc, loadImage)

// ==========================================
// 2. Konva 节点配置项映射
// ==========================================
const imageConfig = computed(() => ({
  image: htmlImageObj.value,
  x: props.layer.x || 0,
  y: props.layer.y || 0,
  scaleX: props.layer.scaleX || 1,
  scaleY: props.layer.scaleY || 1,
  rotation: props.layer.rotation || 0,
  // 只有在“抓手/选择”模式且图层未被锁定时，才允许物理拖拽
  draggable: store.activeTool === 'move' && !props.layer.isLocked,
  name: `image-${props.layer.id}`
}))

// Transformer 配置：定制化 UI
const transformerConfig = {
  anchorSize: 10,
  anchorCornerRadius: 5,
  anchorStroke: '#3b82f6',
  anchorFill: '#ffffff',
  borderStroke: '#3b82f6',
  keepRatio: true // 默认等比缩放，防止图片拉伸变形
}

// ==========================================
// 3. 交互状态管理 (Transformer 绑定)
// ==========================================
// 判断是否应该显示控制框
const shouldShowTransformer = computed(() => {
  return store.activeLayerId === props.layer.id && 
         store.activeTool === 'move' && 
         !props.layer.isLocked
})

// 监听状态，动态将 Transformer 挂载到图片节点上
watch(shouldShowTransformer, async (show) => {
  if (show) {
    await nextTick() // 等待 Transformer 渲染
    if (transformerNodeRef.value && imageNodeRef.value) {
      const transformerNode = transformerNodeRef.value.getNode()
      const imageNode = imageNodeRef.value.getNode()
      transformerNode.nodes([imageNode])
      transformerNode.getLayer().batchDraw()
    }
  }
}, { immediate: true })

// 点击图片激活图层
const handleSelect = () => {
  if (store.activeTool === 'move' && !props.layer.isLocked) {
    store.activeLayerId = props.layer.id
  }
}

// ==========================================
// 4. 数据回写与状态同步 (写入 Pinia)
// ==========================================
const handleDragEnd = (e) => {
  const node = e.target
  // 更新图层数据
  store.updateLayerTransform(props.layer.id, {
    x: node.x(),
    y: node.y()
  })
  // 记录到撤销/重做栈 (需在 store 中实现 recordState)
  store.recordState()
}

const handleTransformEnd = (e) => {
  const node = e.target
  store.updateLayerTransform(props.layer.id, {
    x: node.x(),
    y: node.y(),
    scaleX: node.scaleX(),
    scaleY: node.scaleY(),
    rotation: node.rotation()
  })
  store.recordState()
}
</script>