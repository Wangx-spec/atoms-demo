<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const mode = ref<'login' | 'register'>('login')
const email = ref('')
const password = ref('')
const error = ref('')

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = ''
}

async function submit() {
  error.value = ''
  if (!email.value || !password.value) {
    error.value = '请输入邮箱和密码'
    return
  }
  try {
    if (mode.value === 'login') {
      await authStore.login(email.value, password.value)
    } else {
      await authStore.register(email.value, password.value)
    }
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect)
  } catch (err: any) {
    error.value = err?.response?.data?.detail || '操作失败，请稍后再试'
  }
}
</script>

<template>
  <main class="auth-view">
    <section class="auth-card">
      <h1>Atoms Demo</h1>
      <p>{{ mode === 'login' ? '登录你的账号' : '创建一个新账号' }}</p>

      <label class="field">
        <span>邮箱</span>
        <input v-model="email" type="email" autocomplete="email" placeholder="you@example.com" />
      </label>

      <label class="field">
        <span>密码</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="至少 6 位"
          @keyup.enter="submit"
        />
      </label>

      <p v-if="error" class="auth-error">{{ error }}</p>

      <button class="primary-button" :disabled="authStore.loading" @click="submit">
        {{ authStore.loading ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
      </button>

      <button class="auth-toggle" type="button" @click="toggleMode">
        {{ mode === 'login' ? '还没有账号？去注册' : '已有账号？去登录' }}
      </button>
    </section>
  </main>
</template>
