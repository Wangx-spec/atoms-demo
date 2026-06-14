import { http } from './http'

export interface SandboxStatus {
  app_id: string
  status: string
  runtime: string
  preview_url?: string | null
  error?: string | null
}

export async function startSandbox(appId: string) {
  const { data } = await http.post<SandboxStatus>(`/api/apps/${appId}/sandbox`)
  return data
}

export async function getSandbox(appId: string) {
  const { data } = await http.get<SandboxStatus>(`/api/apps/${appId}/sandbox`)
  return data
}

export async function stopSandbox(appId: string) {
  await http.delete(`/api/apps/${appId}/sandbox`)
}

export async function getSandboxLogs(appId: string) {
  const { data } = await http.get<{ logs: string }>(`/api/apps/${appId}/sandbox/logs`)
  return data.logs
}
