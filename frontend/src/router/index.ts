import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../stores/auth'
import AppDetailView from '../views/AppDetailView.vue'
import AppListView from '../views/AppListView.vue'
import ArtworkDetailView from '../views/ArtworkDetailView.vue'
import GalleryView from '../views/GalleryView.vue'
import LoginView from '../views/LoginView.vue'
import SearchView from '../views/SearchView.vue'
import StudioView from '../views/StudioView.vue'
import UserProfileView from '../views/UserProfileView.vue'
import WorkspaceView from '../views/WorkspaceView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/',
      name: 'workspace',
      component: WorkspaceView,
      meta: { requiresAuth: true },
    },
    {
      path: '/apps',
      name: 'apps',
      component: AppListView,
      meta: { requiresAuth: true },
    },
    {
      path: '/apps/:id',
      name: 'app-detail',
      component: AppDetailView,
      meta: { requiresAuth: true },
    },
    {
      path: '/studio',
      name: 'studio',
      component: StudioView,
      meta: { requiresAuth: true },
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: GalleryView,
    },
    {
      path: '/gallery/:id',
      name: 'artwork-detail',
      component: ArtworkDetailView,
    },
    {
      path: '/u/:id',
      name: 'user-profile',
      component: UserProfileView,
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminLayout,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.initialized) {
    await auth.loadCurrentUser()
  }
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined }
  }
  if (to.meta.requiresAdmin && !auth.user?.is_admin) {
    return '/'
  }
  if (to.path === '/login' && auth.isAuthenticated) {
    return '/'
  }
  return true
})

export default router
