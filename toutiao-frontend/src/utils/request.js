import axios from 'axios'
import { useUserStore } from '../store/user'
import { apiConfig } from '../config/api'
import { showToast } from 'vant'
import router from '../router'

const request = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: 15000
})

request.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 200) return res
    if (res.code === 401) {
      showToast('请重新登录')
      router.push('/login')
    }
    return Promise.reject(new Error(res.message || '请求失败'))
  },
  error => {
    if (error.response?.status === 401) {
      showToast('请重新登录')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default request
