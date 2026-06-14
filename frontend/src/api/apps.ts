import { http } from './http'
import type { GeneratedApp, GeneratedCode } from '../types'

export async function saveGeneratedApp(payload: GeneratedCode & {
  prompt: string
  session_id?: string | null
  status?: string
}) {
  const { data } = await http.post<GeneratedApp>('/api/apps', payload)
  return data
}

export async function listGeneratedApps() {
  const { data } = await http.get<GeneratedApp[]>('/api/apps')
  return data
}

export async function getGeneratedApp(id: string) {
  const { data } = await http.get<GeneratedApp>(`/api/apps/${id}`)
  return data
}

export async function updateGeneratedApp(
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
  const { data } = await http.patch<GeneratedApp>(`/api/apps/${id}`, payload)
  return data
}

export async function deleteGeneratedApp(id: string) {
  await http.delete(`/api/apps/${id}`)
}
