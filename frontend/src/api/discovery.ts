import { http } from './http'
import type { GalleryItem } from '../types'

export async function searchArtworks(query: string) {
  const { data } = await http.get<GalleryItem[]>('/api/search', { params: { q: query } })
  return data
}

export async function similarArtworks(appId: string) {
  const { data } = await http.get<GalleryItem[]>(`/api/gallery/${appId}/similar`)
  return data
}

export async function recommendations() {
  const { data } = await http.get<GalleryItem[]>('/api/recommendations')
  return data
}
