<template>
  <div class="action-stream-container">
    <Transition name="fade-slide">
      <div v-if="actionText" class="action-text">
        {{ actionText }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
defineProps({
  actionText: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.action-stream-container {
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.action-text {
  font-family: "Noto Serif SC", serif;
  font-size: 12px;
  color: #7f8c8d;
  letter-spacing: 1px;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(5px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>