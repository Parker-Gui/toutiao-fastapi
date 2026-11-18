<template>
  <div class="news-item" @click="goToDetail">
    <div class="news-content">
      <h3 class="news-title">{{ news.title }}</h3>
      <p class="news-desc">{{ news.description }}</p>
      <div class="news-info">
        <span>{{ news.author }}</span>
        <span>{{ news.publishTime }}</span>
        <span>{{ news.views }} 阅读</span>
      </div>
    </div>
    <div class="news-image">
      <img :src="news.image" :alt="news.title">
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  news: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const goToDetail = () => {
  router.push(`/news/detail/${props.news.id}`)
}
</script>

<style scoped>
.news-item {
  display: flex;
  padding: 14px 16px;
  margin: 0 0 10px;
  background: var(--color-bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-card);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  border-bottom: none;
}

.news-item:active {
  transform: scale(0.98);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.news-content {
  flex: 1;
  margin-right: 12px;
  overflow: hidden;
}

.news-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 8px;
  line-height: 1.4;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.news-desc {
  font-size: var(--font-size-caption);
  color: var(--color-text-secondary);
  margin: 0 0 8px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.news-info {
  font-size: 12px;
  color: var(--color-text-tertiary);
  display: flex;
}

.news-info span {
  margin-right: 10px;
}

.news-image {
  width: 110px;
  height: 80px;
  flex-shrink: 0;
  border-radius: var(--radius-md);
  overflow: hidden;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.news-item:active .news-image img {
  transform: scale(1.03);
}
</style>