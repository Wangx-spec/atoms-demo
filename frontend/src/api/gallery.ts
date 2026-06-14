import { http } from './http'
import type { GalleryComment, GalleryDetail, GalleryItem, UserProfile } from '../types'

export async function listGallery(params: { sort?: string; tag?: string } = {}) {
  const { data } = await http.get<GalleryItem[]>('/api/gallery', { params })
  return data
}

export async function getArtwork(id: string) {
  const { data } = await http.get<GalleryDetail>(`/api/gallery/${id}`)
  return data
}

export async function likeArtwork(id: string) {
  const { data } = await http.post<GalleryDetail>(`/api/gallery/${id}/like`)
  return data
}

export async function unlikeArtwork(id: string) {
  const { data } = await http.delete<GalleryDetail>(`/api/gallery/${id}/like`)
  return data
}

export async function addComment(id: string, content: string) {
  const { data } = await http.post<GalleryComment>(`/api/gallery/${id}/comments`, { content })
  return data
}

export async function deleteComment(commentId: string) {
  await http.delete(`/api/gallery/comments/${commentId}`)
}

export async function getUserProfile(userId: string) {
  const { data } = await http.get<UserProfile>(`/api/users/${userId}/profile`)
  return data
}
