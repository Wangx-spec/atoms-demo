import { http } from './http'
import type { AdminAppItem, AdminTaskItem, AdminUser, Announcement } from '../types'

export async function getStats() {
  const { data } = await http.get<{ users: number; apps: number; tasks: number }>(
    '/api/admin/stats',
  )
  return data
}

export async function listUsers() {
  const { data } = await http.get<AdminUser[]>('/api/admin/users')
  return data
}

export async function adjustCredits(userId: string, delta: number) {
  const { data } = await http.post<AdminUser>(`/api/admin/users/${userId}/credits`, { delta })
  return data
}

export async function listApps(statusFilter?: string) {
  const { data } = await http.get<AdminAppItem[]>('/api/admin/apps', {
    params: statusFilter ? { status_filter: statusFilter } : {},
  })
  return data
}

export async function moderateApp(appId: string, action: 'approve' | 'reject') {
  const { data } = await http.post<AdminAppItem>(`/api/admin/apps/${appId}/moderate`, { action })
  return data
}

export async function listTasks() {
  const { data } = await http.get<AdminTaskItem[]>('/api/admin/tasks')
  return data
}

export async function listAnnouncements() {
  const { data } = await http.get<Announcement[]>('/api/admin/announcements')
  return data
}

export async function createAnnouncement(title: string, body: string) {
  const { data } = await http.post<Announcement>('/api/admin/announcements', { title, body })
  return data
}

export async function deleteAnnouncement(id: string) {
  await http.delete(`/api/admin/announcements/${id}`)
}
