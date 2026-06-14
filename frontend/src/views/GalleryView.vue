<script setup lang="ts">
import { onMounted } from 'vue'

import { useGalleryStore } from '../stores/gallery'

const galleryStore = useGalleryStore()

onMounted(() => {
  galleryStore.loadGallery('latest')
})
</script>

<template>
  <main class="page">
    <header class="page-header">
      <div>
        <h1>社区画廊</h1>
        <p>浏览社区公开的作品，点赞与评论</p>
      </div>
      <div class="sort-tabs">
        <button :class="{ active: galleryStore.sort === 'latest' }" @click="galleryStore.loadGallery('latest')">
          最新
        </button>
        <button :class="{ active: galleryStore.sort === 'popular' }" @click="galleryStore.loadGallery('popular')">
          热门
        </button>
      </div>
    </header>

    <p v-if="galleryStore.loading" class="page-hint">加载中...</p>
    <p v-else-if="!galleryStore.items.length" class="page-hint">还没有公开作品。</p>

    <ul v-else class="gallery-grid">
      <li v-for="item in galleryStore.items" :key="item.id" class="gallery-card">
        <RouterLink :to="`/gallery/${item.id}`">
          <div class="gallery-thumb">
            <img v-if="item.preview_url" :src="item.preview_url" alt="预览" />
            <span v-else>{{ item.title || item.prompt }}</span>
          </div>
          <div class="gallery-meta">
            <strong>{{ item.title || item.prompt.slice(0, 40) }}</strong>
            <div class="gallery-stats">
              <span>♥ {{ item.like_count }}</span>
              <span>💬 {{ item.comment_count }}</span>
              <span>👁 {{ item.view_count }}</span>
            </div>
          </div>
        </RouterLink>
      </li>
    </ul>
  </main>
</template>
