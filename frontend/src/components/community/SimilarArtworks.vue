<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'

import * as discoveryApi from '../../api/discovery'
import type { GalleryItem } from '../../types'

const props = defineProps<{
  appId: string
}>()

const items = ref<GalleryItem[]>([])

async function load() {
  try {
    items.value = await discoveryApi.similarArtworks(props.appId)
  } catch {
    items.value = []
  }
}

onMounted(load)
watch(() => props.appId, load)
</script>

<template>
  <section v-if="items.length" class="similar-section">
    <h3>相似作品</h3>
    <ul class="similar-list">
      <li v-for="item in items" :key="item.id">
        <RouterLink :to="`/gallery/${item.id}`">
          <img v-if="item.preview_url" :src="item.preview_url" alt="预览" />
          <span>{{ item.title || item.prompt.slice(0, 24) }}</span>
        </RouterLink>
      </li>
    </ul>
  </section>
</template>
