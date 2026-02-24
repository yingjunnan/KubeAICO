<template>
  <div class="login-page">
    <div class="login-card card">
      <p class="eyebrow">Kubernetes Operations Console</p>
      <h1>Sign in to KubeAICO</h1>
      <form @submit.prevent="onSubmit">
        <label>
          <span>Username</span>
          <input v-model="username" required />
        </label>
        <label>
          <span>Password</span>
          <input v-model="password" type="password" required />
        </label>
        <button class="primary-btn" :disabled="auth.loading" type="submit">
          {{ auth.loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <p class="hint">Default account: admin / admin123</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('admin')
const password = ref('admin123')
const errorMessage = ref('')

async function onSubmit() {
  errorMessage.value = ''
  try {
    await auth.login(username.value, password.value)
    await router.push('/')
  } catch (error) {
    errorMessage.value = 'Login failed. Please check username/password.'
  }
}
</script>
