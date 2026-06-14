<script setup lang="ts">
import { computed } from 'vue'

import type { MediaArtwork } from '../../types'

const props = defineProps<{
  artwork: MediaArtwork
}>()

defineEmits<{
  remove: [id: string]
}>()

const title = computed(() => {
  const text = props.artwork.title || props.artwork.prompt || '未命名媒体作品'
  return text.length > 40 ? `${text.slice(0, 40)}...` : text
})

const createdAt = computed(() => new Date(props.artwork.created_at).toLocaleString())
const isImage = computed(() => props.artwork.type === 'image')
</script>

<template>
  <article class="app-card">
    <header>
      <h3>{{ title }}</h3>
      <span class="app-status">{{ isImage ? '图片' : '音乐' }}</span>
    </header>
    <div v-if="artwork.media_url" class="task-result">
      <img v-if="isImage" :src="artwork.media_url" alt="媒体作品" />
      <audio v-else controls :src="artwork.media_url" />
    </div>
    <p class="app-meta">创建于 {{ createdAt }}</p>
    <footer class="app-actions">
      <button class="danger-button" @click="$emit('remove', artwork.id)">删除</button>
    </footer>
  </article>
</template>
