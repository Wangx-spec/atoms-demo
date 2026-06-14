import { http } from './http'
import type { Task, TaskType } from '../types'

export async function createTask(type: TaskType, params: Record<string, unknown>) {
  const { data } = await http.post<Task>('/api/tasks', { type, params })
  return data
}

export async function listTasks() {
  const { data } = await http.get<Task[]>('/api/tasks')
  return data
}

export async function getTask(id: string) {
  const { data } = await http.get<Task>(`/api/tasks/${id}`)
  return data
}

export async function cancelTask(id: string) {
  const { data } = await http.post<Task>(`/api/tasks/${id}/cancel`)
  return data
}

export async function deleteTask(id: string) {
  await http.delete(`/api/tasks/${id}`)
}
