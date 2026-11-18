import { defineStore } from 'pinia'
import { useUserStore } from '../user'
import request from '../../utils/request'

export const useHistoryStore = defineStore('history', {
  state: () => ({
    history: []
  }),

  getters: {
    getHistory: state => state.history
  },

  actions: {
    async addHistoryApi(newsId) {
      if (!useUserStore().getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        const res = await request.post('/api/history/add', { newsId })
        return { success: true, data: res.data }
      } catch (error) {
        console.error('添加浏览历史请求失败:', error)
        return { success: false, message: '网络请求失败' }
      }
    },

    addHistory(news) {
      const existingIndex = this.history.findIndex(item => item.id === news.id)
      if (existingIndex !== -1) {
        this.history.splice(existingIndex, 1)
      }

      this.history.unshift({ ...news, viewTime: new Date().toISOString() })
      if (this.history.length > 50) {
        this.history.pop()
      }
    },

    clearHistory() {
      this.history = []
    },

    async clearHistoryApi() {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        this.clearHistory()
        return { success: true, isLocal: true }
      }

      try {
        await request.delete('/api/history/clear')
        this.clearHistory()
        return { success: true }
      } catch (error) {
        console.error('清空浏览历史请求失败:', error)
        return { success: false, message: '网络请求失败' }
      }
    },

    removeHistory(id) {
      this.history = this.history.filter(item => item.id !== id)
    },

    async removeHistoryApi(id) {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        this.removeHistory(id)
        return { success: true, isLocal: true }
      }

      try {
        await request.delete('/api/history/remove', { params: { newsId: id } })
        this.removeHistory(id)
        return { success: true }
      } catch (error) {
        console.error('删除浏览历史请求失败:', error)
        return { success: false, message: '网络请求失败' }
      }
    },

    async getHistoryListApi() {
      if (!useUserStore().getLoginStatus) {
        return { success: false, message: '请先登录', isLocal: true }
      }

      try {
        const res = await request.get('/api/history/list')
        this.history = res.data.list || []
        return { success: true, data: this.history }
      } catch (error) {
        console.error('获取浏览历史请求失败:', error)
        return { success: false, message: '网络请求失败' }
      }
    }
  },

  persist: {
    enabled: true,
    strategies: [{ key: 'history-store', storage: localStorage }]
  }
})
