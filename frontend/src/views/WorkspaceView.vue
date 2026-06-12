<script setup lang="ts">
import { computed, onMounted } from 'vue'

import PromptPanel from '../components/workspace/PromptPanel.vue'
import CodeEditor from '../components/workspace/CodeEditor.vue'
import PreviewFrame from '../components/workspace/PreviewFrame.vue'
import { useAgentStore } from '../stores/agent'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const agentStore = useAgentStore()

const previewHtml = computed(() => agentStore.previewHtml)

onMounted(async () => {
  try {
    await authStore.ensureDemoUser()
    await agentStore.bootstrap()
  } catch {
    authStore.resetSession()
    await authStore.ensureDemoUser()
    await agentStore.bootstrap()
  }
})
</script>

<template>
  <main class="workspace">
    <PromptPanel
      v-model:prompt="agentStore.prompt"
      :generating="agentStore.generating"
      :stream-text="agentStore.streamText"
      @generate="agentStore.generate"
    />

    <section class="workspace-main">
      <header class="topbar">
        <div>
          <strong>创作工作台</strong>
          <span>{{ agentStore.sessionId ? `Session ${agentStore.sessionId.slice(0, 8)}` : '初始化中' }}</span>
        </div>
        <button class="secondary-button" :disabled="agentStore.saving" @click="agentStore.save">
          {{ agentStore.saving ? '保存中...' : '保存作品' }}
        </button>
      </header>

      <div class="split-view">
        <CodeEditor
          v-model:html="agentStore.html"
          v-model:css="agentStore.css"
          v-model:js="agentStore.js"
        />
        <PreviewFrame :srcdoc="previewHtml" />
      </div>

      <footer class="saved-strip">
        <span>已保存 {{ agentStore.savedApps.length }} 个作品</span>
      </footer>
    </section>
  </main>
</template>
