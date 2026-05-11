<template>
  <div class="auth-layout">
    <div class="bg-grid"></div>

    <div class="auth-card">
      
      <div class="brand-header"> 
        <header class="top-nav">
          <img :src="logoImg" alt="MoBu Canvas" class="logo" />
          <span class="brand-name">MoBu Canvas</span>
        </header>
        <p class="motto">
          {{ isLoginMode ? '- 欢迎回来，继续你的创作 -' : '- 加入墨步，探索可控 AI 的边界 -' }}
        </p>
      </div>

      <div class="tab-switcher">
        <div 
          class="tab-item" 
          :class="{ 'is-active': isLoginMode }" 
          @click="switchMode(true)"
        >登录</div>
        <div 
          class="tab-item" 
          :class="{ 'is-active': !isLoginMode }" 
          @click="switchMode(false)"
        >注册</div>
        <div class="tab-indicator" :style="{ transform: isLoginMode ? 'translateX(0)' : 'translateX(100%)' }"></div>
      </div>

      <div class="form-container">
        <transition name="fade-slide" mode="out-in">
          <form @submit.prevent="handleSubmit" :key="isLoginMode ? 'login' : 'register'" class="auth-form">
            
            <el-input
              v-if="!isLoginMode"
              v-model="formData.nickname"
              placeholder="你的创作者昵称"
              class="mobu-input"
              size="large"
            />

            <el-input
              v-model="formData.account"
              placeholder="邮箱地址 / 手机号"
              autocomplete="off"
              class="mobu-input"
              size="large"
            />

            <el-input
              v-model="formData.password"
              type="password"
              placeholder="密码 (不少于6位)"
              show-password
              autocomplete="new-password"
              class="mobu-input"
              size="large"
            />

            <el-button 
              native-type="submit" 
              :loading="isLoading" 
              class="mega-btn"
            >
              {{ isLoginMode ? '进入画板' : '开启创作之旅' }}
            </el-button>
          </form>
        </transition>
      </div>

      <div class="footer-extensions">
        <a v-if="isLoginMode" href="#" class="forgot-link">忘记密码？</a>
        <div v-else class="terms-hint">
          注册即代表同意墨步 <a href="#">用户协议</a> 与 <a href="#">隐私政策</a>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

// 🌟 核心修复 1：通过显式 import 引入图片，彻底解决 Vite 路径打包报错和图片裂开问题
import logoImg from '../assets/mobu_logo.png'

const router = useRouter()
const isLoginMode = ref(true)
const isLoading = ref(false)

const formData = reactive({
  account: '', 
  password: '',
  nickname: ''
})

const switchMode = (mode) => {
  if (isLoginMode.value === mode) return
  isLoginMode.value = mode
  formData.password = ''
  formData.nickname = ''
}

// 🌟 核心修复 2：移除真实的 Axios 请求，替换为前端纯本地 Mock 逻辑
const handleSubmit = async () => {
  if (!formData.account.trim()) return ElMessage.warning('请输入账号')
  if (formData.password.length < 6) return ElMessage.warning('密码长度不能少于6位')
  if (!isLoginMode.value && !formData.nickname.trim()) return ElMessage.warning('请输入创作者昵称')

  isLoading.value = true

  // 使用 setTimeout 模拟 800 毫秒的网络请求延迟，让按钮的 loading 动画生效
  setTimeout(() => {
    if (isLoginMode.value) {
      // ===== 🟢 登录拦截逻辑 =====
      const mockAccount = '19000000000'
      const mockPassword = '123456'

      if (formData.account === mockAccount && formData.password === mockPassword) {
        // 1. 账号密码匹配成功，伪造一个 Token 存入本地浏览器
        localStorage.setItem('mobu_token', 'mock_fake_token_888888')
        ElMessage.success('登录成功，欢迎回来！')
        
        // 2. 丝滑跳转到尺寸选择页 (或者直接跳 /workspace)
        router.push('/') 
      } else {
        // 密码错误提示
        ElMessage.error('账号或密码错误！(测试账号: 19000000000, 密码: 123456)')
      }
    } else {
      // ===== 🔵 注册拦截逻辑 =====
      // 假装注册成功，直接切回登录页面让用户自己登
      ElMessage.success('账号创建成功，请登录！')
      switchMode(true)
    }
    
    isLoading.value = false
  }, 800)
}
</script>

<style scoped>
/* ==========================================
   全局布局与底噪背景
========================================== */
.logo { width: 45px; height: 45px; object-fit: contain; }
.brand-name { 
  font-size: 20px; /* 如果 logo 大了，字号也可以适当加到 22px 或 24px */
  font-weight: 800; 
  color: #111827; 
  letter-spacing: -0.5px; 

  position: relative;
  top: -1px; /* 👈 调这里：如果是 -2px 就是向上移 2px，慢慢试直到视觉完美 */
}
.top-nav {
  display: flex;         
  align-items: center;   /* 👈 核心参数：让内部的 logo 和文字在垂直方向上绝对居中对齐 */
  justify-content: center; /* 如果你想让这组整体在卡片里居中，加这行；如果是靠左，就改成 flex-start，并加点 gap: 8px 留间距 */
}

.auth-layout {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #FAFAFA;
  overflow: hidden;
}

.bg-grid {
  position: absolute;
  inset: 0;
  /* 极简透明网格底纹，与画板首页对齐 */
  background-image: 
    linear-gradient(to right, rgba(0, 0, 0, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 0, 0, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  z-index: 0;
}

/* ==========================================
   中心悬浮毛玻璃卡片
========================================== */
.auth-card {
  position: relative;
  z-index: 1;
  width: 400px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.08), 
              0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

/* ==========================================
   1. 品牌与情绪共鸣区
========================================== */
.brand-header {
  text-align: center;
  margin-bottom: 32px;
}


.motto {
  font-size: 14px;
  color: #6B7280;
  margin: 0;
  letter-spacing: 0.5px;
  margin-top: 10px;
  padding-left: 20px;
}

/* ==========================================
   2. 无界限 Tab 切换
========================================== */
.tab-switcher {
  position: relative;
  display: flex;
  margin-bottom: 32px;
  border-bottom: 1px solid #E5E7EB;
}

.tab-item {
  flex: 1;
  text-align: center;
  padding-bottom: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #9CA3AF;
  cursor: pointer;
  transition: color 0.3s;
}

.tab-item.is-active {
  color: #111827;
}

.tab-indicator {
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 50%;
  height: 2px;
  background-color: #111827;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ==========================================
   3. 表单区 (深度定制 Element Plus)
========================================== */
.form-container {
  min-height: 200px; /* 防止高度塌陷导致抖动 */
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 深度覆写 Element Plus 输入框样式 */
:deep(.mobu-input .el-input__wrapper) {
  background-color: #F3F4F6 !important;
  box-shadow: none !important;
  border-radius: 12px;
  padding: 8px 16px;
  transition: all 0.3s ease;
}

:deep(.mobu-input .el-input__wrapper.is-focus) {
  background-color: #FFFFFF !important;
  box-shadow: 0 0 0 1.5px #111827 inset !important;
}

:deep(.mobu-input .el-input__inner) {
  color: #111827;
  height: 32px;
}

:deep(.mobu-input .el-input__inner::placeholder) {
  color: #9CA3AF;
  font-weight: 400;
}

/* 极其克制的高级黑胶囊按钮 */
.mega-btn {
  width: 100%;
  height: 48px;
  margin-top: 12px;
  background-color: #111827;
  color: #FFFFFF;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.mega-btn:hover:not(:disabled) {
  background-color: #374151;
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -10px rgba(17, 24, 39, 0.5);
}

.mega-btn:active:not(:disabled) {
  transform: translateY(0);
}

/* ==========================================
   4. 辅助通道
========================================== */
.footer-extensions {
  margin-top: 24px;
  text-align: center;
}

.forgot-link {
  font-size: 13px;
  color: #6B7280;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: #111827;
}

.terms-hint {
  font-size: 12px;
  color: #9CA3AF;
}

.terms-hint a {
  color: #111827;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-bottom 0.2s;
}

.terms-hint a:hover {
  border-bottom: 1px solid #111827;
}

/* ==========================================
   Vue Transition 动画 (平滑淡入滑动)
========================================== */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>