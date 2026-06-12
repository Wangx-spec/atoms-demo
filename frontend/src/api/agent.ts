import { http } from './http'
import type { AgentSession, GeneratedCode } from '../types'

export async function createSession(title?: string) {
  const { data } = await http.post<AgentSession>('/api/agent/sessions', { title })
  return data
}

export async function sendMessage(sessionId: string, prompt: string) {
  const { data } = await http.post<{ session_id: string; stream_url: string }>(
    `/api/agent/sessions/${sessionId}/messages`,
    { prompt },
  )
  return data
}

export async function generateCode(sessionId: string) {
  const { data } = await http.post<GeneratedCode>(`/api/agent/sessions/${sessionId}/generate-code`)
  return data
}
