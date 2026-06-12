import { defineStore } from 'pinia'

import * as agentApi from '../api/agent'
import * as appsApi from '../api/apps'
import type { GeneratedApp } from '../types'

interface AgentState {
  sessionId: string
  prompt: string
  streamText: string
  html: string
  css: string
  js: string
  generating: boolean
  saving: boolean
  savedApps: GeneratedApp[]
}

export const useAgentStore = defineStore('agent', {
  state: (): AgentState => ({
    sessionId: '',
    prompt: '做一个个人作品集首页，展示项目、技能和联系方式',
    streamText: '',
    html: '<main class="empty-preview">输入需求后点击生成</main>',
    css: 'body { margin: 0; font-family: system-ui; } .empty-preview { padding: 32px; }',
    js: '',
    generating: false,
    saving: false,
    savedApps: [],
  }),
  getters: {
    previewHtml(state) {
      return buildPreviewHtml(state.html, state.css, state.js)
    },
  },
  actions: {
    async bootstrap() {
      const session = await agentApi.createSession('MVP 创作会话')
      this.sessionId = session.id
      this.savedApps = await appsApi.listGeneratedApps()
    },
    async generate() {
      if (!this.sessionId) {
        await this.bootstrap()
      }
      this.generating = true
      this.streamText = ''
      try {
        const message = await agentApi.sendMessage(this.sessionId, this.prompt)
        await this.consumeStream(message.stream_url)
        const code = await agentApi.generateCode(this.sessionId)
        this.html = code.html
        this.css = code.css
        this.js = code.js
      } finally {
        this.generating = false
      }
    },
    async consumeStream(streamUrl: string) {
      const token = localStorage.getItem('atoms_token')
      const response = await fetch(streamUrl, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (!response.body) return

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let done = false

      while (!done) {
        const result = await reader.read()
        done = result.done
        const text = decoder.decode(result.value || new Uint8Array(), { stream: !done })
        text
          .split('\n\n')
          .filter(Boolean)
          .forEach((event) => {
            if (event.startsWith('data: ')) {
              this.streamText += event.replace(/^data: /, '')
            }
          })
      }
    },
    async save() {
      this.saving = true
      try {
        const app = await appsApi.saveGeneratedApp({
          prompt: this.prompt,
          session_id: this.sessionId,
          html: this.html,
          css: this.css,
          js: this.js,
          status: 'saved',
        })
        this.savedApps.unshift(app)
      } finally {
        this.saving = false
      }
    },
  },
})

function buildPreviewHtml(html: string, css: string, js: string) {
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>${css}</style>
</head>
<body>
  ${html}
  <script>${js}<\/script>
</body>
</html>`
}
