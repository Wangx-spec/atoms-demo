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
