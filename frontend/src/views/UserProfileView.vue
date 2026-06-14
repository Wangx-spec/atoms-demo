<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import * as galleryApi from '../api/gallery'
import type { UserProfile } from '../types'

const route = useRoute()
const profile = ref<UserProfile | null>(null)

async function load() {
  const userId = route.params.id as string
  profile.value = await galleryApi.getUserProfile(userId)
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<template>
  <main v-if="profile" class="page">
    <header class="page-header">
      <div>
        <h1>{{ profile.display_name || `用户 ${profile.user_id.slice(0, 8)}` }}</h1>
        <p>{{ profile.bio || '这位创作者还没有填写简介。' }}</p>
        <p class="page-hint">公开作品 {{ profile.public_app_count }} 个</p>
      </div>
    </header>

    <ul class="gallery-grid">
      <li v-for="item in profile.apps" :key="item.id" class="gallery-card">
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
  </main>
  <main v-else class="page"><p class="page-hint">加载中...</p></main>
</template>
