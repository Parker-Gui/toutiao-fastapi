import { defineStore } from 'pinia'
import request from '../../utils/request'

export const useNewsStore = defineStore('news', {
  state: () => ({
    newsList: [],
    newsDetail: {},
    categories: [],
    currentCategory: 1,
    loading: false,
    refreshing: false,
    finished: false,
    categoriesLoading: false
  }),

  actions: {
    async getCategories() {
      if (this.categoriesLoading) return

      this.categoriesLoading = true

      try {
        const res = await request.get('/api/news/categories')
        this.categories = [...res.data, { id: 10, name: '更多' }]

        if (!this.currentCategory && this.categories.length > 0) {
          this.currentCategory = this.categories[0].id
        }
      } catch (error) {
        console.error('获取新闻分类失败:', error)
        this.categories = [
          { id: 1, name: '头条' },
          { id: 2, name: '社会' },
          { id: 3, name: '国内' },
          { id: 4, name: '国际' },
          { id: 5, name: '娱乐' },
          { id: 6, name: '体育' },
          { id: 7, name: '科技' }
        ]
      } finally {
        this.categoriesLoading = false
      }
    },

    changeCategory(categoryId) {
      if (this.currentCategory !== categoryId) {
        this.currentCategory = categoryId
        this.newsList = []
        this.finished = false
        this.getNewsList(true)
      }
    },

    async getNewsList(isRefresh = false) {
      if (isRefresh) {
        this.refreshing = true
        this.newsList = []
        this.finished = false
      }

      this.loading = true

      try {
        const params = {
          categoryId: this.currentCategory,
          page: isRefresh ? 1 : Math.ceil(this.newsList.length / 10) + 1,
          pageSize: 10
        }
        const res = await request.get('/api/news/list', { params })
        const newsData = res.data.list
        this.newsList = isRefresh ? newsData : [...this.newsList, ...newsData]

        if (newsData.length < params.pageSize || !res.data.hasMore) {
          this.finished = true
        }
      } catch (error) {
        console.error('获取新闻列表失败:', error)
      } finally {
        this.loading = false
        this.refreshing = false
      }
    },

    async getNewsDetail(id) {
      try {
        const res = await request.get('/api/news/detail', {
          params: { newsId: id }
        })
        this.newsDetail = res.data
      } catch (error) {
        console.error('获取新闻详情失败:', error)
      }
    },

    getCategoryName(categoryId) {
      const category = this.categories.find(item => item.id === categoryId)
      return category ? category.name : '未知'
    }
  }
})
