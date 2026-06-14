<script setup lang="ts">
defineProps<{
  srcdoc: string
  src?: string | null
}>()
</script>

<template>
  <section class="preview-panel">
    <div class="preview-toolbar">
      <span>{{ src ? 'Live Preview (沙箱)' : 'Preview' }}</span>
    </div>
    <iframe
      v-if="src"
      title="沙箱预览"
      sandbox="allow-scripts allow-same-origin"
      :src="src"
    />
    <iframe v-else title="应用预览" sandbox="allow-scripts" :srcdoc="srcdoc" />
  </section>
</template>
