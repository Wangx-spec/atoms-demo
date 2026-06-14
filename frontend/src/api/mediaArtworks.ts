import { http } from './http'
import type { MediaArtwork } from '../types'

export async function saveTaskAsArtwork(taskId: string, payload: { title?: string | null } = {}) {
  const { data } = await http.post<MediaArtwork>(`/api/media-artworks/from-task/${taskId}`, payload)
  return data
}

export async function listMediaArtworks() {
  const { data } = await http.get<MediaArtwork[]>('/api/media-artworks')
  return data
}

export async function deleteMediaArtwork(id: string) {
  await http.delete(`/api/media-artworks/${id}`)
}
