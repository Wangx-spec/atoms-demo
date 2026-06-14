import { defineStore } from 'pinia'

import * as adminApi from '../api/admin'
import type { AdminAppItem, AdminTaskItem, AdminUser, Announcement } from '../types'

interface AdminState {
  stats: { users: number; apps: number; tasks: number }
  users: AdminUser[]
  apps: AdminAppItem[]
  tasks: AdminTaskItem[]
  announcements: Announcement[]
}

export const useAdminStore = defineStore('admin', {
  state: (): AdminState => ({
    stats: { users: 0, apps: 0, tasks: 0 },
    users: [],
    apps: [],
    tasks: [],
    announcements: [],
  }),
  actions: {
    async loadStats() {
      this.stats = await adminApi.getStats()
    },
    async loadUsers() {
      this.users = await adminApi.listUsers()
    },
    async adjustCredits(userId: string, delta: number) {
      const updated = await adminApi.adjustCredits(userId, delta)
      const index = this.users.findIndex((u) => u.id === userId)
      if (index !== -1) this.users[index] = updated
    },
    async loadApps(statusFilter?: string) {
      this.apps = await adminApi.listApps(statusFilter)
    },
    async moderateApp(appId: string, action: 'approve' | 'reject') {
      const updated = await adminApi.moderateApp(appId, action)
      const index = this.apps.findIndex((a) => a.id === appId)
      if (index !== -1) this.apps[index] = updated
    },
    async loadTasks() {
      this.tasks = await adminApi.listTasks()
    },
    async loadAnnouncements() {
      this.announcements = await adminApi.listAnnouncements()
    },
    async createAnnouncement(title: string, body: string) {
      const item = await adminApi.createAnnouncement(title, body)
      this.announcements.unshift(item)
    },
    async deleteAnnouncement(id: string) {
      await adminApi.deleteAnnouncement(id)
      this.announcements = this.announcements.filter((a) => a.id !== id)
    },
  },
})
