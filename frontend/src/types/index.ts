export interface User {
  id: string
  email: string
  credits: number
  avatar_url?: string | null
  is_admin?: boolean
}

export interface AdminUser {
  id: string
  email: string
  credits: number
  is_admin: boolean
  created_at: string
}

export interface AdminAppItem {
  id: string
  user_id: string
  prompt: string
  status: string
  visibility: string
  created_at: string
}

export interface AdminTaskItem {
  id: string
  user_id: string
  type: string
  status: string
  progress: number
  created_at: string
}

export interface Announcement {
  id: string
  title: string
  body: string
  published: boolean
  created_at: string
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
  runtime: string
  visibility: string
  title?: string | null
  tags?: string | null
  view_count: number
  like_count: number
  comment_count: number
  created_at: string
  updated_at: string
}

export interface AgentSessionSummary {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export type AgentEventType =
  | 'analysis_started'
  | 'analysis_completed'
  | 'structure_planned'
  | 'code_generating'
  | 'reviewing'
  | 'completed'
  | 'error'

export interface AgentEvent {
  type: AgentEventType
  message: string
  data?: Record<string, unknown> | null
}

export type TaskType =
  | 'code_generation'
  | 'image_generation'
  | 'music_generation'
  | 'preview_snapshot'

export interface Task {
  id: string
  user_id: string
  type: string
  status: 'pending' | 'running' | 'succeeded' | 'failed'
  progress: number
  result_url?: string | null
  saved_artwork_id?: string | null
  error_message?: string | null
  params: Record<string, unknown>
  result_meta: Record<string, unknown>
  created_at: string
}

export interface MediaArtwork {
  id: string
  user_id: string
  source_task_id?: string | null
  type: 'image' | 'music'
  prompt: string
  title?: string | null
  params: Record<string, unknown>
  content_type: string
  media_url?: string | null
  visibility: string
  created_at: string
  updated_at: string
}

export interface GalleryItem {
  id: string
  user_id: string
  title?: string | null
  prompt: string
  tags?: string | null
  preview_url?: string | null
  view_count: number
  like_count: number
  comment_count: number
  published_at?: string | null
}

export interface GalleryComment {
  id: string
  user_id: string
  app_id: string
  content: string
  created_at: string
}

export interface GalleryDetail extends GalleryItem {
  html: string
  css: string
  js: string
  runtime: string
  liked: boolean
  comments: GalleryComment[]
}

export interface UserProfile {
  user_id: string
  display_name?: string | null
  bio?: string | null
  avatar_url?: string | null
  public_app_count: number
  apps: GalleryItem[]
}
