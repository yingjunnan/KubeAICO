import { defineStore } from 'pinia'
import { login as apiLogin, me } from '../services/api'
import type { UserRead } from '../types/api'

interface AuthState {
  token: string
  user: UserRead | null
  loading: boolean
}

const TOKEN_KEY = 'kubeaico_token'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY) ?? '',
    user: null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },
  actions: {
    async bootstrap() {
      if (!this.token) return
      try {
        this.user = await me()
      } catch {
        this.logout()
      }
    },
    async login(username: string, password: string) {
      this.loading = true
      try {
        const data = await apiLogin(username, password)
        this.token = data.access_token
        localStorage.setItem(TOKEN_KEY, data.access_token)
        this.user = await me()
      } finally {
        this.loading = false
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
    },
  },
})
