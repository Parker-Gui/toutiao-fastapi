import { defineStore } from 'pinia'
import { useUserStore } from '../user'
import request from '../../utils/request'

export const useFavoriteStore = defineStore('favorite', {
  state: () => ({
    favorites: [],
    loading: false
  }),

  getters: {
    getFavorites: state => state.favorites,
    isFavorite: state => id => state.favorites.some(item => item.id === id)
  },

  actions: {
    async checkFavoriteStatusApi(newsId) {
      const userStore = useUserStore()
      if (!userStore.getLoginStatus) {
        return { success: true, isFavorite: this.isFavorite(newsId), isLocal: true }
      }

      try {
        this.loading = true
        const res = await request.get('/api/favorite/check', { params: { newsId } })
        return { success: true, isFavorite: Boolean(res.data.isFavorite) }
      } catch (error) {
        console.error('检查收藏状态请求失败:', error)
        return { success: true, isFavorite: this.isFavorite(newsId), isLocal: true }
      } finally {
        this.loading = false
      }
    },

    async addFavoriteApi(newsId) {
      if (!useUserStore().getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        const res = await request.post('/api/favorite/add', { newsId })
        return { success: true, data: res.data }
      } catch (error) {
        console.error('添加收藏请求失败:', error)
        return { success: false, message: '网络请求失败' }
      } finally {
        this.loading = false
      }
    },

    async removeFavoriteApi(newsId) {
      if (!useUserStore().getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        await request.delete('/api/favorite/remove', { params: { newsId } })
        return { success: true }
      } catch (error) {
        console.error('取消收藏请求失败:', error)
        return { success: false, message: '网络请求失败' }
      } finally {
        this.loading = false
      }
    },

    addFavorite(news) {
      if (!this.isFavorite(news.id)) {
        this.favorites.unshift({ ...news, favoriteTime: new Date().toISOString() })
      }
    },

    removeFavorite(id) {
      this.favorites = this.favorites.filter(item => item.id !== id)
    },

    async toggleFavorite(news) {
      if (!news || !news.id) {
        console.error('无效的新闻对象:', news)
        return null
      }

      if (this.isFavorite(news.id)) {
        const result = await this.removeFavoriteApi(news.id)
        if (result.success) {
          this.removeFavorite(news.id)
          return false
        }
        return null
      }

      const result = await this.addFavoriteApi(news.id)
      if (result.success) {
        this.addFavorite(news)
        return true
      }
      return null
    },

    clearFavorites() {
      this.favorites = []
    },

    async clearFavoritesApi() {
      if (!useUserStore().getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        await request.delete('/api/favorite/clear')
        this.clearFavorites()
        return { success: true }
      } catch (error) {
        console.error('清空收藏请求失败:', error)
        return { success: false, message: '网络请求失败' }
      } finally {
        this.loading = false
      }
    },

    async getFavoriteListApi(page = 1, pageSize = 10) {
      if (!useUserStore().getLoginStatus) {
        return { success: false, message: '请先登录' }
      }

      try {
        this.loading = true
        const res = await request.get('/api/favorite/list', {
          params: { page, pageSize }
        })
        this.favorites = res.data.list
        return { success: true, data: res.data }
      } catch (error) {
        console.error('获取收藏列表请求失败:', error)
        return { success: false, message: '网络请求失败' }
      } finally {
        this.loading = false
      }
    }
  },

  persist: {
    enabled: true,
    strategies: [{ key: 'favorite-store', storage: localStorage }]
  }
})
