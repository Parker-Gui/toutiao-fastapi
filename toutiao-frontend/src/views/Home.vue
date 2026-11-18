<template>
  <div class="home">
    <van-nav-bar :title="$t('home.title')" fixed />

    <!-- 分类 tabs（只做切换，不包裹列表内容） -->
    <van-tabs
      v-model:active="activeTab"
      sticky
      swipeable
      animated
    >
      <van-tab
        v-for="(category, index) in displayCategories"
        :key="category.id"
        :title="getCategoryTranslation(category.name)"
      />
    </van-tabs>

    <!-- 列表内容区域（van-list 在 van-tab 外面，直接参与页面滚动） -->
    <div class="news-list-wrapper">
      <van-pull-refresh v-model="newsStore.refreshing" @refresh="onRefresh">
        <van-list
          v-model:loading="newsStore.loading"
          :finished="newsStore.finished"
          :finished-text="$t('home.noMore')"
          @load="onLoad"
        >
          <news-item
            v-for="item in newsStore.newsList"
            :key="item.id"
            :news="item"
          />
        </van-list>
      </van-pull-refresh>
    </div>

    <tab-bar />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useNewsStore } from '../store/modules/news'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import NewsItem from '../components/NewsItem.vue'
import TabBar from '../components/TabBar.vue'

const newsStore = useNewsStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const activeTab = ref(0)

// 监听路由变化
watch(
  () => route.query.categoryId,
  (newCategoryId) => {
    if (newCategoryId) {
      const categoryId = parseInt(newCategoryId)
      // 找到分类ID对应的索引
      const filteredCategories = newsStore.categories.filter(category => category.name !== '更多')
      const index = filteredCategories.findIndex(cat => cat.id === categoryId)
      
      if (index !== -1) {
        // 设置activeTab为对应索引
        activeTab.value = index
        // 切换分类
        newsStore.changeCategory(categoryId)
      }
    }
  },
  { immediate: true }
)

onMounted(() => {
  // 获取新闻分类，然后加载第一页
  newsStore.getCategories().then(() => {
    newsStore.getNewsList()
  })
})

// 计算属性：显示的分类（只显示非"更多"分类）
const displayCategories = computed(() => {
  // 获取所有非"更多"分类
  return newsStore.categories.filter(category => category.name !== '更多');
})

// 获取分类名称的翻译
const getCategoryTranslation = (categoryName) => {
  const categoryMap = {
    '头条': 'headline',
    '社会': 'society',
    '国内': 'domestic',
    '国际': 'international',
    '娱乐': 'entertainment',
    '体育': 'sports',
    '军事': 'military',
    '科技': 'technology',
    '财经': 'finance',
    '更多': 'more'
  };
  
  const key = categoryMap[categoryName];
  return key ? t(`home.categories.${key}`) : categoryName;
}
    

// 跳转到分类页面
const goToCategory = () => {
  router.push('/category')
}

// 监听 activeTab 变化 → 切换分类并重置
watch(activeTab, (newIndex) => {
  const filtered = newsStore.categories.filter(c => c.name !== '更多')
  const category = filtered[newIndex]
  if (category) {
    newsStore.changeCategory(category.id)
  }
})

// 下拉刷新
const onRefresh = () => {
  newsStore.getNewsList(true)
}

// 上拉加载更多
const onLoad = () => {
  newsStore.getNewsList()
}

// 每页10条，当下拉刷新清空列表，然后加载第一页
// 上拉加载更多，就是加载下一页，然后追加到列表后面

</script>

<style scoped>
.home {
  padding-top: 46px;
  padding-bottom: 50px;
  background-color: var(--color-bg-page);
  min-height: 100vh;
}

/* ================================
   导航栏 — 品牌红色
   ================================ */
.home :deep(.van-nav-bar) {
  background-color: var(--color-brand);
}
.home :deep(.van-nav-bar__title) {
  color: #fff;
  font-weight: 600;
  font-size: 18px;
}
.home :deep(.van-nav-bar .van-icon) {
  color: #fff;
}

/* ================================
   标签页 — 品牌色
   ================================ */
:deep(.van-tabs__wrap) {
  background-color: #fff;
}
:deep(.van-tab) {
  font-size: 14px;
}
.home :deep(.van-tab--active) {
  color: var(--color-brand);
  font-weight: 700;
  font-size: 16px;
}
.home :deep(.van-tabs__line) {
  background-color: var(--color-brand);
  height: 3px;
  border-radius: 2px;
}

.news-list-wrapper {
  padding: 12px 12px 0;
}
</style>