<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const showNav = computed(() => route.path !== '/login' && authStore.isAuthenticated)

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-root">
    <nav v-if="showNav" class="app-nav">
      <div class="app-nav-links">
        <RouterLink to="/">创作工作台</RouterLink>
        <RouterLink to="/studio">多模态</RouterLink>
        <RouterLink to="/apps">我的作品</RouterLink>
        <RouterLink to="/gallery">社区画廊</RouterLink>
        <RouterLink to="/search">搜索</RouterLink>
        <RouterLink v-if="authStore.user?.is_admin" to="/admin">管理后台</RouterLink>
      </div>
      <div class="app-nav-user">
        <span v-if="authStore.user" class="nav-credits">积分 {{ authStore.user.credits }}</span>
        <span v-if="authStore.user">{{ authStore.user.email }}</span>
        <button class="auth-toggle" type="button" @click="logout">退出登录</button>
      </div>
    </nav>
    <RouterView />
  </div>
</template>
