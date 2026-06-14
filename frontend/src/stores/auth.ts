import { defineStore } from 'pinia'

import * as authApi from '../api/auth'
import { TOKEN_KEY } from '../api/http'
import type { User } from '../types'

interface AuthState {
  token: string
  user: User | null
  loading: boolean
  initialized: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: null,
    loading: false,
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user),
  },
  actions: {
    async login(email: string, password: string) {
      this.loading = true
      try {
        const response = await authApi.login(email, password)
        this.setSession(response.access_token, response.user)
      } finally {
        this.loading = false
      }
    },
    async register(email: string, password: string) {
      this.loading = true
      try {
        const response = await authApi.register(email, password)
        this.setSession(response.access_token, response.user)
      } finally {
        this.loading = false
      }
    },
    async loadCurrentUser() {
      this.initialized = true
      if (!this.token) {
        this.user = null
        return
      }
      try {
        this.user = await authApi.getCurrentUser()
      } catch {
        this.resetSession()
      }
    },
    setSession(token: string, user: User) {
      this.token = token
      this.user = user
      this.initialized = true
      localStorage.setItem(TOKEN_KEY, token)
    },
    logout() {
      this.resetSession()
    },
    resetSession() {
      this.token = ''
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
