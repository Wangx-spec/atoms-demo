export interface User {
  id: string
  email: string
  credits: number
  avatar_url?: string | null
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AgentSession {
  id: string
  title: string
  messages: Array<{
    role: string
    content: string
    created_at: string
  }>
}

export interface GeneratedCode {
  html: string
  css: string
  js: string
}

export interface GeneratedApp extends GeneratedCode {
  id: string
  user_id: string
  session_id?: string | null
  prompt: string
  preview_url?: string | null
  status: string
  created_at: string
}
