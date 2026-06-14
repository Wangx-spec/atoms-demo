<script setup lang="ts">
import { onMounted, ref } from 'vue'

import * as discoveryApi from '../api/discovery'
import type { GalleryItem } from '../types'

const query = ref('')
const results = ref<GalleryItem[]>([])
const recommended = ref<GalleryItem[]>([])
const searching = ref(false)
const searched = ref(false)

async function search() {
  if (!query.value.trim()) return
  searching.value = true
  searched.value = true
  try {
    results.value = await discoveryApi.searchArtworks(query.value.trim())
  } finally {
    searching.value = false
  }
}

onMounted(async () => {
  try {
    recommended.value = await discoveryApi.recommendations()
  } catch {
    recommended.value = []
  }
})
</script>

<template>
  <main class="page">
    <header class="page-header">
      <div>
        <h1>语义搜索</h1>
        <p>用自然语言描述你想找的作品</p>
      </div>
    </header>

    <div class="search-bar">
      <input v-model="query" placeholder="例如：带深色主题的待办清单" @keyup.enter="search" />
      <button class="primary-button" :disabled="searching" @click="search">
        {{ searching ? '搜索中...' : '搜索' }}
      </button>
    </div>

    <section v-if="searched">
      <h2>搜索结果</h2>
      <p v-if="!results.length" class="page-hint">没有匹配的作品。</p>
      <ul v-else class="gallery-grid">
        <li v-for="item in results" :key="item.id" class="gallery-card">
          <RouterLink :to="`/gallery/${item.id}`">
            <div class="gallery-thumb">
              <img v-if="item.preview_url" :src="item.preview_url" alt="预览" />
              <span v-else>{{ item.title || item.prompt }}</span>
            </div>
            <div class="gallery-meta">
              <strong>{{ item.title || item.prompt.slice(0, 40) }}</strong>
            </div>
          </RouterLink>
        </li>
      </ul>
    </section>

    <section v-if="recommended.length" class="recommend-section">
      <h2>为你推荐</h2>
      <ul class="gallery-grid">
        <li v-for="item in recommended" :key="item.id" class="gallery-card">
          <RouterLink :to="`/gallery/${item.id}`">
            <div class="gallery-thumb">
              <img v-if="item.preview_url" :src="item.preview_url" alt="预览" />
              <span v-else>{{ item.title || item.prompt }}</span>
            </div>
            <div class="gallery-meta">
              <strong>{{ item.title || item.prompt.slice(0, 40) }}</strong>
              <div class="gallery-stats"><span>♥ {{ item.like_count }}</span></div>
            </div>
          </RouterLink>
        </li>
      </ul>
    </section>
  </main>
</template>
