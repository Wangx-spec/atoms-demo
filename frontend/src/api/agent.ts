import { http } from './http'
import type { AgentSession, AgentSessionSummary, GeneratedCode } from '../types'

export async function createSession(title?: string) {
  const { data } = await http.post<AgentSession>('/api/agent/sessions', { title })
  return data
}

export async function listSessions() {
  const { data } = await http.get<AgentSessionSummary[]>('/api/agent/sessions')
  return data
}

export async function getSession(sessionId: string) {
  const { data } = await http.get<AgentSession>(`/api/agent/sessions/${sessionId}`)
  return data
}

export async function renameSession(sessionId: string, title: string) {
  const { data } = await http.patch<AgentSession>(`/api/agent/sessions/${sessionId}`, { title })
  return data
}

export async function deleteSession(sessionId: string) {
  await http.delete(`/api/agent/sessions/${sessionId}`)
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
