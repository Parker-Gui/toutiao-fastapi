import { ref, watchEffect } from 'vue'

const STORAGE_KEY = 'toutiao-theme'

// 检测系统暗色模式偏好
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)')

// 当前主题：'light' | 'dark' | 'auto'
const currentTheme = ref(localStorage.getItem(STORAGE_KEY) || 'light')

// 实际生效的暗色状态
const isDark = ref(false)

function updateTheme() {
  if (currentTheme.value === 'auto') {
    isDark.value = prefersDark.matches
  } else {
    isDark.value = currentTheme.value === 'dark'
  }

  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
}

// 初始执行
updateTheme()

// 监听系统主题变化
prefersDark.addEventListener('change', () => {
  if (currentTheme.value === 'auto') {
    updateTheme()
  }
})

// 响应式更新
watchEffect(() => {
  localStorage.setItem(STORAGE_KEY, currentTheme.value)
  updateTheme()
})

export function useTheme() {
  function setLight()  { currentTheme.value = 'light' }
  function setDark()   { currentTheme.value = 'dark' }
  function setAuto()   { currentTheme.value = 'auto' }

  return { currentTheme, isDark, setLight, setDark, setAuto,  }
}