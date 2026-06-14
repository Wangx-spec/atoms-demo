import { defineStore } from 'pinia'

import * as galleryApi from '../api/gallery'
import type { GalleryDetail, GalleryItem } from '../types'

interface GalleryState {
  items: GalleryItem[]
  current: GalleryDetail | null
  sort: string
  loading: boolean
}

export const useGalleryStore = defineStore('gallery', {
  state: (): GalleryState => ({
    items: [],
    current: null,
    sort: 'latest',
    loading: false,
  }),
  actions: {
    async loadGallery(sort?: string, tag?: string) {
      this.loading = true
      this.sort = sort ?? this.sort
      sort = this.sort
      try {
        this.items = await galleryApi.listGallery({ sort, tag })
      } finally {
        this.loading = false
      }
    },
    async loadArtwork(id: string) {
      this.current = await galleryApi.getArtwork(id)
      return this.current
    },
    async toggleLike(id: string) {
      if (!this.current) return
      this.current = this.current.liked
        ? await galleryApi.unlikeArtwork(id)
        : await galleryApi.likeArtwork(id)
    },
    async comment(id: string, content: string) {
      await galleryApi.addComment(id, content)
      this.current = await galleryApi.getArtwork(id)
    },
    async removeComment(id: string, commentId: string) {
      await galleryApi.deleteComment(commentId)
      this.current = await galleryApi.getArtwork(id)
    },
  },
})
