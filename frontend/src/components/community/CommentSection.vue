<script setup lang="ts">
import { ref } from 'vue'

import type { GalleryComment } from '../../types'
import { useAuthStore } from '../../stores/auth'

const props = defineProps<{
  comments: GalleryComment[]
}>()

const emit = defineEmits<{
  submit: [content: string]
  remove: [commentId: string]
}>()

const auth = useAuthStore()
const draft = ref('')

function submit() {
  if (!draft.value.trim()) return
  emit('submit', draft.value.trim())
  draft.value = ''
}

void props
</script>

<template>
  <section class="comment-section">
    <h3>评论 ({{ comments.length }})</h3>
    <div v-if="auth.isAuthenticated" class="comment-form">
      <textarea v-model="draft" rows="2" placeholder="写下你的评论..." />
      <button class="secondary-button" @click="submit">发表</button>
    </div>
    <p v-else class="page-hint">登录后可参与评论。</p>

    <ul class="comment-list">
      <li v-for="comment in comments" :key="comment.id" class="comment-item">
        <div>
          <RouterLink :to="`/u/${comment.user_id}`" class="comment-author">
            {{ comment.user_id.slice(0, 8) }}
          </RouterLink>
          <p>{{ comment.content }}</p>
        </div>
        <button
          v-if="auth.user && auth.user.id === comment.user_id"
          class="auth-toggle"
          @click="$emit('remove', comment.id)"
        >
          删除
        </button>
      </li>
    </ul>
  </section>
</template>
