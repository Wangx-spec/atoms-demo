<script setup lang="ts">
import { computed } from 'vue'

import type { GeneratedApp } from '../../types'

const props = defineProps<{
  app: GeneratedApp
}>()

defineEmits<{
  open: [id: string]
  remove: [id: string]
}>()

const title = computed(() => {
  const text = props.app.prompt?.trim() || '未命名作品'
  return text.length > 40 ? `${text.slice(0, 40)}...` : text
})

const createdAt = computed(() => new Date(props.app.created_at).toLocaleString())
</script>

<template>
  <article class="app-card">
    <header>
      <h3>{{ title }}</h3>
      <span class="app-status">{{ app.status }}</span>
    </header>
    <p class="app-meta">创建于 {{ createdAt }}</p>
    <footer class="app-actions">
      <button class="secondary-button" @click="$emit('open', app.id)">打开编辑</button>
      <button class="danger-button" @click="$emit('remove', app.id)">删除</button>
    </footer>
  </article>
</template>
