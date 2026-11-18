<template>
  <van-tabbar v-model="active" route>
    <van-tabbar-item to="/home" icon="home-o">{{ $t('nav.home') }}</van-tabbar-item>
    <van-tabbar-item to="/aichat" icon="chat-o">{{ $t('nav.aiChat') }}</van-tabbar-item>
    <van-tabbar-item to="/my" icon="user-o">{{ $t('nav.my') }}</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const active = ref(0)

// 根据当前路由路径设置激活的标签
const setActiveTab = () => {
  const path = route.path
  if (path.includes('/home')) {
    active.value = 0
  } else if (path.includes('/aichat')) {
    active.value = 1
  } else if (path.includes('/my')) {
    active.value = 2
  }
}

// 初始化时设置激活标签
setActiveTab()
</script>

<style scoped>
:deep(.van-tabbar-item--active) {
  color: var(--color-brand);
}

:deep(.van-tabbar-item__icon) {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

:deep(.van-tabbar-item--active .van-tabbar-item__icon) {
  transform: scale(1.1);
}
</style>