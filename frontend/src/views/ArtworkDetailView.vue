<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'

import CommentSection from '../components/community/CommentSection.vue'
import LikeButton from '../components/community/LikeButton.vue'
import PreviewFrame from '../components/workspace/PreviewFrame.vue'
import SimilarArtworks from '../components/community/SimilarArtworks.vue'
import { useGalleryStore } from '../stores/gallery'
import { buildPreviewHtml } from '../utils/preview'

const route = useRoute()
const galleryStore = useGalleryStore()
const id = route.params.id as string

const previewHtml = computed(() => {
  const art = galleryStore.current
  if (!art) return ''
  return buildPreviewHtml(art.html, art.css, art.js)
})

onMounted(() => {
  galleryStore.loadArtwork(id)
})
</script>

<template>
  <main v-if="galleryStore.current" class="page artwork-detail">
    <header class="page-header">
      <div>
        <h1>{{ galleryStore.current.title || galleryStore.current.prompt.slice(0, 50) }}</h1>
        <RouterLink :to="`/u/${galleryStore.current.user_id}`" class="page-hint">
          作者 {{ galleryStore.current.user_id.slice(0, 8) }}
        </RouterLink>
      </div>
      <LikeButton
        :liked="galleryStore.current.liked"
        :count="galleryStore.current.like_count"
        @toggle="galleryStore.toggleLike(id)"
      />
    </header>

    <div class="artwork-preview">
      <PreviewFrame :srcdoc="previewHtml" />
    </div>

    <p v-if="galleryStore.current.tags" class="artwork-tags">标签：{{ galleryStore.current.tags }}</p>

    <SimilarArtworks :app-id="id" />

    <CommentSection
      :comments="galleryStore.current.comments"
      @submit="(content) => galleryStore.comment(id, content)"
      @remove="(commentId) => galleryStore.removeComment(id, commentId)"
    />
  </main>
  <main v-else class="page">
    <p class="page-hint">加载中或作品不存在。</p>
  </main>
</template>
