<script setup lang="ts">
defineProps<{
  srcdoc: string
}>()
</script>

<template>
  <section class="preview-panel">
    <div class="preview-toolbar">
      <span>Preview</span>
    </div>
    <iframe title="应用预览" sandbox="allow-scripts" :srcdoc="srcdoc" />
  </section>
</template>
