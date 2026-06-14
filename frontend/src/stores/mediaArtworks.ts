import { defineStore } from 'pinia'

import * as mediaArtworksApi from '../api/mediaArtworks'
import type { MediaArtwork } from '../types'

interface MediaArtworksState {
  artworks: MediaArtwork[]
  loading: boolean
  savingTaskIds: string[]
}

export const useMediaArtworksStore = defineStore('mediaArtworks', {
  state: (): MediaArtworksState => ({
    artworks: [],
    loading: false,
    savingTaskIds: [],
  }),
  actions: {
    async loadArtworks() {
      this.loading = true
      try {
        this.artworks = await mediaArtworksApi.listMediaArtworks()
      } finally {
        this.loading = false
      }
    },
    async saveTask(taskId: string, title?: string | null) {
      this.savingTaskIds.push(taskId)
      try {
        const artwork = await mediaArtworksApi.saveTaskAsArtwork(taskId, { title })
        const index = this.artworks.findIndex((item) => item.id === artwork.id)
        if (index === -1) {
          this.artworks.unshift(artwork)
        } else {
          this.artworks[index] = artwork
        }
        return artwork
      } finally {
        this.savingTaskIds = this.savingTaskIds.filter((id) => id !== taskId)
      }
    },
    async deleteArtwork(id: string) {
      await mediaArtworksApi.deleteMediaArtwork(id)
      this.artworks = this.artworks.filter((item) => item.id !== id)
    },
    isSavingTask(taskId: string) {
      return this.savingTaskIds.includes(taskId)
    },
  },
})
