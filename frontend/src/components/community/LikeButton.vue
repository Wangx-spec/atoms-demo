<script setup lang="ts">
defineProps<{
  liked: boolean
  count: number
}>()

defineEmits<{
  toggle: []
}>()
</script>

<template>
  <button :class="['like-button', { liked }]" @click="$emit('toggle')">
    <span>{{ liked ? '已赞' : '点赞' }}</span>
    <strong>{{ count }}</strong>
  </button>
</template>
