<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { useAdminStore } from '../../stores/admin'

const adminStore = useAdminStore()

type Tab = 'overview' | 'users' | 'apps' | 'tasks' | 'announcements'
const tab = ref<Tab>('overview')

const newTitle = ref('')
const newBody = ref('')

async function switchTab(next: Tab) {
  tab.value = next
  if (next === 'overview') await adminStore.loadStats()
  if (next === 'users') await adminStore.loadUsers()
  if (next === 'apps') await adminStore.loadApps()
  if (next === 'tasks') await adminStore.loadTasks()
  if (next === 'announcements') await adminStore.loadAnnouncements()
}

async function publishAnnouncement() {
  if (!newTitle.value.trim()) return
  await adminStore.createAnnouncement(newTitle.value.trim(), newBody.value.trim())
  newTitle.value = ''
  newBody.value = ''
}

onMounted(() => switchTab('overview'))
</script>

<template>
  <main class="page admin-page">
    <header class="page-header">
      <div>
        <h1>管理后台</h1>
        <p>用户、作品审核、任务监控、模型配置与公告</p>
      </div>
    </header>

    <nav class="admin-tabs">
      <button :class="{ active: tab === 'overview' }" @click="switchTab('overview')">概览</button>
      <button :class="{ active: tab === 'users' }" @click="switchTab('users')">用户</button>
      <button :class="{ active: tab === 'apps' }" @click="switchTab('apps')">作品审核</button>
      <button :class="{ active: tab === 'tasks' }" @click="switchTab('tasks')">任务</button>
      <button :class="{ active: tab === 'announcements' }" @click="switchTab('announcements')">公告</button>
    </nav>

    <section v-if="tab === 'overview'" class="admin-stats">
      <div class="stat-card"><span>用户</span><strong>{{ adminStore.stats.users }}</strong></div>
      <div class="stat-card"><span>作品</span><strong>{{ adminStore.stats.apps }}</strong></div>
      <div class="stat-card"><span>任务</span><strong>{{ adminStore.stats.tasks }}</strong></div>
    </section>

    <section v-else-if="tab === 'users'">
      <table class="admin-table">
        <thead>
          <tr><th>邮箱</th><th>积分</th><th>管理员</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="user in adminStore.users" :key="user.id">
            <td>{{ user.email }}</td>
            <td>{{ user.credits }}</td>
            <td>{{ user.is_admin ? '是' : '否' }}</td>
            <td>
              <button class="auth-toggle" @click="adminStore.adjustCredits(user.id, 100)">+100</button>
              <button class="auth-toggle" @click="adminStore.adjustCredits(user.id, -100)">-100</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-else-if="tab === 'apps'">
      <table class="admin-table">
        <thead>
          <tr><th>需求</th><th>状态</th><th>可见性</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="app in adminStore.apps" :key="app.id">
            <td>{{ app.prompt.slice(0, 40) }}</td>
            <td>{{ app.status }}</td>
            <td>{{ app.visibility }}</td>
            <td>
              <button class="auth-toggle" @click="adminStore.moderateApp(app.id, 'approve')">通过</button>
              <button class="auth-toggle" @click="adminStore.moderateApp(app.id, 'reject')">下架</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-else-if="tab === 'tasks'">
      <table class="admin-table">
        <thead>
          <tr><th>类型</th><th>状态</th><th>进度</th><th>时间</th></tr>
        </thead>
        <tbody>
          <tr v-for="task in adminStore.tasks" :key="task.id">
            <td>{{ task.type }}</td>
            <td>{{ task.status }}</td>
            <td>{{ task.progress }}%</td>
            <td>{{ new Date(task.created_at).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-else-if="tab === 'announcements'">
      <div class="studio-form">
        <input v-model="newTitle" placeholder="公告标题" />
        <textarea v-model="newBody" rows="3" placeholder="公告内容" />
        <button class="primary-button" @click="publishAnnouncement">发布公告</button>
      </div>
      <ul class="comment-list">
        <li v-for="item in adminStore.announcements" :key="item.id" class="comment-item">
          <div><strong>{{ item.title }}</strong><p>{{ item.body }}</p></div>
          <button class="auth-toggle" @click="adminStore.deleteAnnouncement(item.id)">删除</button>
        </li>
      </ul>
    </section>
  </main>
</template>
