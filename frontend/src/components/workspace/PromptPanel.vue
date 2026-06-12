<script setup lang="ts">
defineProps<{
  generating: boolean
  streamText: string
}>()

const prompt = defineModel<string>('prompt', { required: true })

defineEmits<{
  generate: []
}>()
</script>

<template>
  <aside class="prompt-panel">
    <div>
      <h1>Atoms Demo</h1>
      <p>用自然语言生成一个可编辑、可预览、可保存的应用原型。</p>
    </div>

    <label class="field">
      <span>需求描述</span>
      <textarea v-model="prompt" rows="8" />
    </label>

    <button class="primary-button" :disabled="generating" @click="$emit('generate')">
      {{ generating ? '生成中...' : '生成应用' }}
    </button>

    <section class="timeline">
      <h2>生成过程</h2>
      <pre>{{ streamText || '等待开始' }}</pre>
    </section>
  </aside>
</template>
