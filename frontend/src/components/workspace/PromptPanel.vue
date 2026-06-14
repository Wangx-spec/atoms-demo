<script setup lang="ts">
import type { AgentEvent } from '../../types'

defineProps<{
  generating: boolean
  streamText: string
  events: AgentEvent[]
}>()

const prompt = defineModel<string>('prompt', { required: true })

defineEmits<{
  generate: []
}>()

const labels: Record<string, string> = {
  analysis_started: '分析需求',
  analysis_completed: '需求分析完成',
  structure_planned: '结构规划完成',
  code_generating: '生成代码',
  reviewing: '代码审查',
  completed: '生成完成',
  error: '生成失败',
}
</script>

<template>
  <aside class="prompt-panel">
    <div>
      <h1>Atoms Demo</h1>
      <p>用自然语言生成一个可编辑、可预览、可保存的应用原型。</p>
    </div>

    <label class="field">
      <span>需求描述</span>
      <textarea v-model="prompt" rows="8" />
    </label>

    <button class="primary-button" :disabled="generating" @click="$emit('generate')">
      {{ generating ? '生成中...' : '生成应用' }}
    </button>

    <section class="timeline">
      <h2>生成过程</h2>
      <ul v-if="events.length" class="event-list">
        <li v-for="(event, index) in events" :key="index" :class="['event-item', event.type]">
          <span class="event-dot" />
          <div>
            <strong>{{ labels[event.type] || event.type }}</strong>
            <p v-if="event.message">{{ event.message }}</p>
          </div>
        </li>
      </ul>
      <pre v-else>{{ streamText || '等待开始' }}</pre>
    </section>
  </aside>
</template>
