<template>
  <div class="mobu-start-screen">
    
    <div class="ambient-mesh-1"></div>
    <div class="ambient-mesh-2"></div>
    <div class="bg-grid"></div>

    <header class="top-nav">
      <img src="../assets/mobu_logo.png" alt="MoBu Logo" class="brand-logo" />
      <span class="brand-name">MoBu Canvas</span>
    </header>

    <main class="hero-section">
      
      <div class="title-group">
        <h1 class="hero-title">步步随心，画由意动</h1>
        <h2 class="hero-subtitle">- 墨步，你的可控式AI绘画伴侣 -</h2>
      </div>

      <button class="start-btn" @click="goToSizeSelection">
        <span class="btn-text">开始创作</span>
      </button>

    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goToSizeSelection = () => {
  router.push('/home')
}
</script>

<style scoped>
/* ================== 全局基建 ================== */
.mobu-start-screen {
  width: 100vw;
  height: 100vh;
  background-color: #F8F9FA; /* 调深一点点的底色，压住阵脚 */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* ================== 视差光影与底噪 (解决页面空洞) ================== */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(to right, rgba(17, 24, 39, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(17, 24, 39, 0.03) 1px, transparent 1px);
  background-size: 64px 64px; /* 放大网格，显得更大气 */
  mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
  z-index: 1;
}

/* 柔和的深邃光效，给纯白页面加入“昂贵”的质感 */
.ambient-mesh-1 {
  position: absolute;
  top: -10%; left: 10%; width: 50vw; height: 50vw;
  background: radial-gradient(circle, rgba(209, 213, 219, 0.4) 0%, rgba(248, 249, 250, 0) 70%);
  filter: blur(80px);
  z-index: 0;
}
.ambient-mesh-2 {
  position: absolute;
  bottom: -20%; right: 5%; width: 60vw; height: 60vw;
  background: radial-gradient(circle, rgba(229, 231, 235, 0.5) 0%, rgba(248, 249, 250, 0) 70%);
  filter: blur(100px);
  z-index: 0;
}

/* ================== 顶部导航 ================== */
.top-nav {
  position: absolute;
  top: 32px;
  left: 40px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 10;
}
.brand-logo { width: 32px; height: 32px; object-fit: contain; }
.brand-name { font-size: 20px; font-weight: 800; color: #111827; letter-spacing: -0.5px; }

/* ================== 核心视觉区排版 ================== */
.hero-section {
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* ✨ 彻底干掉负边距，让 Flexbox 实现 100% 的绝对垂直居中 */
  margin: 0; 
}

/* 收紧标题组的内部空间 */
.title-group {
  display: flex;
  flex-direction: column;
  align-items: center; 
  margin-bottom: 48px; /* 缩减与按钮的距离，建立紧凑感 */
}

/* 阶梯 1: 主标题 (收缩字间距，放大字号) */
.hero-title { 
  font-size: 80px; /* 字号加大，撑起画面 */
  font-weight: 900; 
  color: #111827; 
  letter-spacing: 2px; /* 极其关键：大字号必须缩小字间距，才能形成有力量的“视觉块” */
  margin: 0;
  /* 增加微妙的渐变和阴影，解决纯黑字的单调 */
  background: linear-gradient(135deg, #111827 0%, #4B5563 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
}

/* 阶梯 2: 副标题 (贴紧主标题) */
.hero-subtitle { 
  font-size: 22px; 
  font-weight: 500;
  color: #6B7280; 
  letter-spacing: 4px; /* 副标题反而加大字间距，形成底座托付感 */
  margin: 16px 0 0 0; /* 距离主标题极近，形成一体化阅读流 */
}

/* ================== 行动按钮 ================== */
.start-btn {
  background: #111827;
  color: white;
  border: none;
  border-radius: 100px; /* 胶囊形按钮，更具现代 SaaS 的亲和力 */
  padding: 18px 56px;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  box-shadow: 0 12px 32px rgba(17, 24, 39, 0.15); /* 阴影变柔和宽广 */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.start-btn:hover { 
  transform: translateY(-2px) scale(1.02); 
  box-shadow: 0 20px 40px rgba(17, 24, 39, 0.25); 
  background: #1f2937;
}

.start-btn:active {
  transform: translateY(0) scale(0.98);
  box-shadow: 0 4px 12px rgba(17, 24, 39, 0.15);
}
</style>