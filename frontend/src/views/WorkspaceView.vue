<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import PromptPanel from '../components/workspace/PromptPanel.vue'
import CodeEditor from '../components/workspace/CodeEditor.vue'
import PreviewFrame from '../components/workspace/PreviewFrame.vue'
import { useAgentStore } from '../stores/agent'

const agentStore = useAgentStore()
const router = useRouter()

const previewHtml = computed(() => agentStore.previewHtml)

onMounted(async () => {
  await agentStore.bootstrap()
})

async function saveAndView() {
  await agentStore.save()
  router.push('/apps')
}
</script>

<template>
  <main class="workspace">
    <PromptPanel
      v-model:prompt="agentStore.prompt"
      :generating="agentStore.generating"
      :stream-text="agentStore.streamText"
      :events="agentStore.events"
      @generate="agentStore.generate"
    />

    <section class="workspace-main">
      <header class="topbar">
        <div>
          <strong>创作工作台</strong>
          <span>{{ agentStore.sessionId ? `Session ${agentStore.sessionId.slice(0, 8)}` : '初始化中' }}</span>
        </div>
        <button class="secondary-button" :disabled="agentStore.saving" @click="saveAndView">
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
        <RouterLink to="/apps">查看我的作品</RouterLink>
      </footer>
    </section>
  </main>
</template>
