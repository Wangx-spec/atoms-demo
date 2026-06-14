import { defineStore } from 'pinia'

import * as appsApi from '../api/apps'
import type { GeneratedApp, GeneratedCode } from '../types'

interface AppsState {
  apps: GeneratedApp[]
  current: GeneratedApp | null
  loading: boolean
  saving: boolean
}

export const useAppsStore = defineStore('apps', {
  state: (): AppsState => ({
    apps: [],
    current: null,
    loading: false,
    saving: false,
  }),
  actions: {
    async loadApps() {
      this.loading = true
      try {
        this.apps = await appsApi.listGeneratedApps()
      } finally {
        this.loading = false
      }
    },
    async loadApp(id: string) {
      this.loading = true
      try {
        this.current = await appsApi.getGeneratedApp(id)
        return this.current
      } finally {
        this.loading = false
      }
    },
    async saveApp(payload: GeneratedCode & {
      prompt: string
      session_id?: string | null
      status?: string
    }) {
      this.saving = true
      try {
        const app = await appsApi.saveGeneratedApp(payload)
        this.apps.unshift(app)
        return app
      } finally {
        this.saving = false
      }
    },
    async updateApp(
      id: string,
      payload: Partial<
        GeneratedCode & {
          prompt: string
          status: string
          runtime: string
          visibility: string
        }
      >,
    ) {
      this.saving = true
      try {
        const updated = await appsApi.updateGeneratedApp(id, payload)
        this.current = updated
        const index = this.apps.findIndex((app) => app.id === id)
        if (index !== -1) {
          this.apps[index] = updated
        }
        return updated
      } finally {
        this.saving = false
      }
    },
    async deleteApp(id: string) {
      await appsApi.deleteGeneratedApp(id)
      this.apps = this.apps.filter((app) => app.id !== id)
      if (this.current?.id === id) {
        this.current = null
      }
    },
  },
})
