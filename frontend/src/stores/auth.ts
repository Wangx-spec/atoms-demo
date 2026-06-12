import { defineStore } from 'pinia'

import * as authApi from '../api/auth'
import type { User } from '../types'

interface AuthState {
  token: string
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('atoms_token') || '',
    user: null,
  }),
  actions: {
    async ensureDemoUser() {
      if (this.token) return

      const email = 'demo@atoms.local'
      const password = 'demo123456'
      try {
        const response = await authApi.register(email, password)
        this.setSession(response.access_token, response.user)
      } catch {
        const response = await authApi.login(email, password)
        this.setSession(response.access_token, response.user)
      }
    },
    setSession(token: string, user: User) {
      this.token = token
      this.user = user
      localStorage.setItem('atoms_token', token)
    },
    resetSession() {
      this.token = ''
      this.user = null
      localStorage.removeItem('atoms_token')
    },
  },
})
