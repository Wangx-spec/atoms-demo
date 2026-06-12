<script setup lang="ts">
const html = defineModel<string>('html', { required: true })
const css = defineModel<string>('css', { required: true })
const js = defineModel<string>('js', { required: true })
</script>

<template>
  <section class="code-editor">
    <div class="editor-tabs">
      <span>HTML</span>
      <span>CSS</span>
      <span>JS</span>
    </div>
    <label>
      <span>HTML</span>
      <textarea v-model="html" spellcheck="false" />
    </label>
    <label>
      <span>CSS</span>
      <textarea v-model="css" spellcheck="false" />
    </label>
    <label>
      <span>JavaScript</span>
      <textarea v-model="js" spellcheck="false" />
    </label>
  </section>
</template>
