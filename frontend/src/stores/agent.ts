import { defineStore } from 'pinia'

import * as agentApi from '../api/agent'
import * as appsApi from '../api/apps'
import type { AgentEvent, GeneratedApp } from '../types'
import { buildPreviewHtml } from '../utils/preview'

interface AgentState {
  sessionId: string
  prompt: string
  streamText: string
  events: AgentEvent[]
  html: string
  css: string
  js: string
  hasGeneratedCode: boolean
  generating: boolean
  saving: boolean
  savedApps: GeneratedApp[]
}

export const useAgentStore = defineStore('agent', {
  state: (): AgentState => ({
    sessionId: '',
    prompt: '做一个个人作品集首页，展示项目、技能和联系方式',
    streamText: '',
    events: [],
    html: '<main class="empty-preview">输入需求后点击生成</main>',
    css: 'body { margin: 0; font-family: system-ui; } .empty-preview { padding: 32px; }',
    js: '',
    hasGeneratedCode: false,
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
      this.events = []
      this.hasGeneratedCode = false
      try {
        const message = await agentApi.sendMessage(this.sessionId, this.prompt)
        await this.consumeStream(message.stream_url)
        // The SSE stream already carries the final code in the `completed` event.
        // Only call the fallback endpoint if the stream did not include code.
        if (!this.hasGeneratedCode) {
          const code = await agentApi.generateCode(this.sessionId)
          this.html = code.html
          this.css = code.css
          this.js = code.js
          this.hasGeneratedCode = Boolean(code.html)
        }
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
      let buffer = ''
      let done = false

      while (!done) {
        const result = await reader.read()
        done = result.done
        buffer += decoder.decode(result.value || new Uint8Array(), { stream: !done })

        const blocks = buffer.split('\n\n')
        buffer = blocks.pop() ?? ''
        for (const block of blocks) {
          this.handleEventBlock(block)
        }
      }
    },
    handleEventBlock(block: string) {
      const dataLine = block
        .split('\n')
        .find((line) => line.startsWith('data:'))
      if (!dataLine) return
      const raw = dataLine.replace(/^data:\s*/, '').trim()
      if (!raw || raw === 'ok') return
      try {
        const event = JSON.parse(raw) as AgentEvent
        this.events.push(event)
        this.streamText += `${event.message || event.type}\n`
        if (event.type === 'completed' && event.data?.code) {
          const code = event.data.code as { html: string; css: string; js: string }
          this.html = code.html
          this.css = code.css
          this.js = code.js
          this.hasGeneratedCode = Boolean(code.html)
        }
      } catch {
        this.streamText += `${raw}\n`
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
