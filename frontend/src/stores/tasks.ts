import { defineStore } from 'pinia'

import * as tasksApi from '../api/tasks'
import type { Task, TaskType } from '../types'

interface TasksState {
  tasks: Task[]
  creating: boolean
}

export const useTasksStore = defineStore('tasks', {
  state: (): TasksState => ({
    tasks: [],
    creating: false,
  }),
  actions: {
    async loadTasks() {
      this.tasks = await tasksApi.listTasks()
    },
    async createTask(type: TaskType, params: Record<string, unknown>) {
      this.creating = true
      try {
        const task = await tasksApi.createTask(type, params)
        this.tasks.unshift(task)
        this.pollTask(task.id)
        return task
      } finally {
        this.creating = false
      }
    },
    async pollTask(id: string) {
      for (let i = 0; i < 600; i += 1) {
        const task = await tasksApi.getTask(id)
        const index = this.tasks.findIndex((t) => t.id === id)
        if (index !== -1) {
          this.tasks[index] = task
        }
        if (task.status === 'succeeded' || task.status === 'failed') {
          return task
        }
        await new Promise((resolve) => setTimeout(resolve, 1000))
      }
    },
    async cancelTask(id: string) {
      const task = await tasksApi.cancelTask(id)
      const index = this.tasks.findIndex((t) => t.id === id)
      if (index !== -1) {
        this.tasks[index] = task
      }
    },
    async deleteTask(id: string) {
      await tasksApi.deleteTask(id)
      this.tasks = this.tasks.filter((task) => task.id !== id)
    },
    markSaved(taskId: string, artworkId: string) {
      const index = this.tasks.findIndex((task) => task.id === taskId)
      if (index !== -1) {
        this.tasks[index] = { ...this.tasks[index], saved_artwork_id: artworkId }
      }
    },
  },
})
