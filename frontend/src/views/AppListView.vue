<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import AppCard from '../components/apps/AppCard.vue'
import MediaArtworkCard from '../components/apps/MediaArtworkCard.vue'
import { useAppsStore } from '../stores/apps'
import { useMediaArtworksStore } from '../stores/mediaArtworks'

const appsStore = useAppsStore()
const mediaArtworksStore = useMediaArtworksStore()
const router = useRouter()

const loading = computed(() => appsStore.loading || mediaArtworksStore.loading)
const empty = computed(() => appsStore.apps.length === 0 && mediaArtworksStore.artworks.length === 0)

onMounted(async () => {
  await Promise.all([appsStore.loadApps(), mediaArtworksStore.loadArtworks()])
})

function open(id: string) {
  router.push(`/apps/${id}`)
}

async function remove(id: string) {
  if (window.confirm('确定删除这个作品吗？此操作不可撤销。')) {
    await appsStore.deleteApp(id)
  }
}

async function removeMedia(id: string) {
  if (window.confirm('确定删除这个媒体作品吗？此操作不可撤销。')) {
    await mediaArtworksStore.deleteArtwork(id)
  }
}
</script>

<template>
  <main class="page">
    <header class="page-header">
      <div>
        <h1>我的作品</h1>
        <p>管理你保存的应用、图片和音乐</p>
      </div>
      <button class="primary-button" @click="router.push('/')">返回工作台</button>
    </header>

    <p v-if="loading" class="page-hint">加载中...</p>
    <p v-else-if="empty" class="page-hint">
      还没有保存的作品，去工作台生成并保存第一个吧。
    </p>

    <section v-else class="app-grid">
      <AppCard
        v-for="app in appsStore.apps"
        :key="app.id"
        :app="app"
        @open="open"
        @remove="remove"
      />
      <MediaArtworkCard
        v-for="artwork in mediaArtworksStore.artworks"
        :key="artwork.id"
        :artwork="artwork"
        @remove="removeMedia"
      />
    </section>
  </main>
</template>
