<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import CodeEditor from '../components/workspace/CodeEditor.vue'
import PreviewFrame from '../components/workspace/PreviewFrame.vue'
import * as sandboxApi from '../api/sandbox'
import { useAppsStore } from '../stores/apps'
import { buildPreviewHtml } from '../utils/preview'

const route = useRoute()
const router = useRouter()
const appsStore = useAppsStore()

const id = route.params.id as string
const html = ref('')
const css = ref('')
const js = ref('')
const prompt = ref('')
const status = ref('saved')
const visibility = ref('private')
const notFound = ref(false)
const message = ref('')

const sandboxStatus = ref('stopped')
const sandboxUrl = ref<string | null>(null)
const sandboxError = ref('')
const sandboxLogs = ref('')
const sandboxBusy = ref(false)

const previewHtml = computed(() => buildPreviewHtml(html.value, css.value, js.value))

onMounted(async () => {
  try {
    const app = await appsStore.loadApp(id)
    if (!app) {
      notFound.value = true
      return
    }
    html.value = app.html
    css.value = app.css
    js.value = app.js
    prompt.value = app.prompt
    status.value = app.status
    visibility.value = app.visibility
  } catch {
    notFound.value = true
  }
})

async function togglePublish() {
  const next = visibility.value === 'public' ? 'private' : 'public'
  await appsStore.updateApp(id, { visibility: next })
  visibility.value = next
  message.value = next === 'public' ? '已公开到社区画廊' : '已设为私有'
}

async function save() {
  message.value = ''
  await appsStore.updateApp(id, {
    html: html.value,
    css: css.value,
    js: js.value,
    prompt: prompt.value,
    status: status.value,
  })
  message.value = '已保存'
}

async function remove() {
  if (window.confirm('确定删除这个作品吗？此操作不可撤销。')) {
    await appsStore.deleteApp(id)
    router.push('/apps')
  }
}

async function runSandbox() {
  sandboxBusy.value = true
  sandboxError.value = ''
  try {
    const result = await sandboxApi.startSandbox(id)
    sandboxStatus.value = result.status
    sandboxUrl.value = result.preview_url ?? null
    await refreshLogs()
  } catch (err) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    sandboxError.value = detail || '启动沙箱失败，请确认 Docker 守护进程可用。'
  } finally {
    sandboxBusy.value = false
  }
}

async function stopSandbox() {
  sandboxBusy.value = true
  try {
    await sandboxApi.stopSandbox(id)
    sandboxStatus.value = 'stopped'
    sandboxUrl.value = null
  } finally {
    sandboxBusy.value = false
  }
}

async function refreshLogs() {
  try {
    sandboxLogs.value = await sandboxApi.getSandboxLogs(id)
  } catch {
    sandboxLogs.value = ''
  }
}
</script>

<template>
  <main class="workspace">
    <aside class="prompt-panel">
      <div>
        <h1>作品编辑</h1>
        <p>编辑 HTML/CSS/JS，实时预览并保存修改。</p>
      </div>

      <label class="field">
        <span>需求描述</span>
        <textarea v-model="prompt" rows="6" />
      </label>

      <label class="field">
        <span>状态</span>
        <input v-model="status" type="text" />
      </label>

      <button class="primary-button" :disabled="appsStore.saving" @click="save">
        {{ appsStore.saving ? '保存中...' : '保存修改' }}
      </button>

      <button class="secondary-button" @click="togglePublish">
        {{ visibility === 'public' ? '取消公开' : '公开到画廊' }}
      </button>

      <div class="sandbox-controls">
        <button
          v-if="sandboxStatus !== 'running'"
          class="secondary-button"
          :disabled="sandboxBusy"
          @click="runSandbox"
        >
          {{ sandboxBusy ? '启动中...' : '在沙箱中运行' }}
        </button>
        <template v-else>
          <button class="secondary-button" :disabled="sandboxBusy" @click="stopSandbox">
            停止沙箱
          </button>
          <button class="auth-toggle" type="button" @click="refreshLogs">刷新日志</button>
        </template>
        <p v-if="sandboxError" class="auth-error">{{ sandboxError }}</p>
        <pre v-if="sandboxLogs" class="sandbox-logs">{{ sandboxLogs }}</pre>
      </div>

      <button class="danger-button" @click="remove">删除作品</button>
      <button class="auth-toggle" type="button" @click="router.push('/apps')">返回作品列表</button>
      <p v-if="message" class="page-hint">{{ message }}</p>
    </aside>

    <section class="workspace-main">
      <header class="topbar">
        <div>
          <strong>作品 {{ id.slice(0, 8) }}</strong>
          <span v-if="notFound">作品不存在或无权访问</span>
          <span v-else>实时预览</span>
        </div>
      </header>

      <div class="split-view">
        <CodeEditor v-model:html="html" v-model:css="css" v-model:js="js" />
        <PreviewFrame :srcdoc="previewHtml" :src="sandboxUrl" />
      </div>
    </section>
  </main>
</template>
