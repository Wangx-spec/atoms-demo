<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { useTasksStore } from '../stores/tasks'
import { useMediaArtworksStore } from '../stores/mediaArtworks'
import type { Task } from '../types'

const tasksStore = useTasksStore()
const mediaArtworksStore = useMediaArtworksStore()

const tab = ref<'image' | 'music'>('image')

const imagePrompt = ref('一只在霓虹城市夜景中奔跑的赛博朋克猫')
const imageStyle = ref('cyberpunk')
const imageWidth = ref(512)
const imageHeight = ref(512)
const imageSteps = ref(30)

const musicPrompt = ref('轻快的 lofi 学习背景音乐，带轻微爵士钢琴')
const musicDuration = ref(15)
const musicStyle = ref('lofi')
const musicInstruments = ref('piano, drums')

const mediaTasks = computed(() =>
  tasksStore.tasks.filter(
    (t) => t.type === 'image_generation' || t.type === 'music_generation',
  ),
)

onMounted(() => {
  tasksStore.loadTasks()
})

async function generateImage() {
  await tasksStore.createTask('image_generation', {
    prompt: imagePrompt.value,
    style: imageStyle.value,
    width: imageWidth.value,
    height: imageHeight.value,
    steps: imageSteps.value,
  })
}

async function generateMusic() {
  await tasksStore.createTask('music_generation', {
    prompt: musicPrompt.value,
    duration: musicDuration.value,
    style: musicStyle.value,
    instruments: musicInstruments.value,
  })
}

function isImage(type: string) {
  return type === 'image_generation'
}

function canDelete(task: Task) {
  return task.status === 'succeeded' || task.status === 'failed'
}

async function saveArtwork(task: Task) {
  const title = typeof task.params.prompt === 'string' ? task.params.prompt.slice(0, 40) : undefined
  const artwork = await mediaArtworksStore.saveTask(task.id, title)
  tasksStore.markSaved(task.id, artwork.id)
}

async function deleteTask(task: Task) {
  if (window.confirm('确定删除这条任务记录吗？已保存到我的作品的内容不会被删除。')) {
    await tasksStore.deleteTask(task.id)
  }
}
</script>

<template>
  <main class="page">
    <header class="page-header">
      <div>
        <h1>多模态创作</h1>
        <p>生成图片与音乐，任务异步执行，进度实时刷新</p>
      </div>
    </header>

    <div class="studio-tabs">
      <button :class="{ active: tab === 'image' }" @click="tab = 'image'">图片</button>
      <button :class="{ active: tab === 'music' }" @click="tab = 'music'">音乐</button>
    </div>

    <section v-if="tab === 'image'" class="studio-form">
      <label class="field"><span>Prompt</span><textarea v-model="imagePrompt" rows="3" /></label>
      <div class="form-row">
        <label class="field"><span>风格</span><input v-model="imageStyle" /></label>
        <label class="field"><span>宽</span><input v-model.number="imageWidth" type="number" /></label>
        <label class="field"><span>高</span><input v-model.number="imageHeight" type="number" /></label>
        <label class="field"><span>步数</span><input v-model.number="imageSteps" type="number" /></label>
      </div>
      <button class="primary-button" :disabled="tasksStore.creating" @click="generateImage">
        生成图片
      </button>
    </section>

    <section v-else class="studio-form">
      <label class="field"><span>Prompt</span><textarea v-model="musicPrompt" rows="3" /></label>
      <div class="form-row">
        <label class="field"><span>时长(秒)</span><input v-model.number="musicDuration" type="number" /></label>
        <label class="field"><span>风格</span><input v-model="musicStyle" /></label>
        <label class="field"><span>乐器</span><input v-model="musicInstruments" /></label>
      </div>
      <button class="primary-button" :disabled="tasksStore.creating" @click="generateMusic">
        生成音乐
      </button>
    </section>

    <section class="task-results">
      <h2>任务记录</h2>
      <p v-if="!mediaTasks.length" class="page-hint">还没有任务，先生成一个吧。</p>
      <ul v-else class="task-list">
        <li v-for="task in mediaTasks" :key="task.id" class="task-card">
          <header>
            <span>{{ isImage(task.type) ? '图片' : '音乐' }}</span>
            <span :class="['task-status', task.status]">{{ task.status }}</span>
          </header>
          <div class="task-progress">
            <div class="task-progress-bar" :style="{ width: `${task.progress}%` }" />
          </div>
          <div v-if="task.status === 'succeeded' && task.result_url" class="task-result">
            <img v-if="isImage(task.type)" :src="task.result_url" alt="生成结果" />
            <audio v-else controls :src="task.result_url" />
          </div>
          <p v-if="task.status === 'failed'" class="auth-error">{{ task.error_message }}</p>
          <footer class="app-actions">
            <button
              v-if="task.status === 'succeeded' && !task.saved_artwork_id"
              class="secondary-button"
              :disabled="mediaArtworksStore.isSavingTask(task.id)"
              @click="saveArtwork(task)"
            >
              {{ mediaArtworksStore.isSavingTask(task.id) ? '保存中...' : '保存到我的作品' }}
            </button>
            <span v-else-if="task.saved_artwork_id" class="page-hint">已保存到我的作品</span>
            <button v-if="canDelete(task)" class="danger-button" @click="deleteTask(task)">
              删除记录
            </button>
          </footer>
        </li>
      </ul>
    </section>
  </main>
</template>
