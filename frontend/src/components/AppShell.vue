<template>
  <div class="app-shell">
    <SideNav />
    <main class="main-area">
      <header class="top-bar card">
        <div>
          <p class="eyebrow">Kubernetes Operations</p>
          <h1>{{ title }}</h1>
        </div>
        <div class="filters">
          <label>
            <span>Range</span>
            <select v-model="localRange" @change="emitFilters">
              <option value="15">15m</option>
              <option value="60">1h</option>
              <option value="360">6h</option>
              <option value="1440">24h</option>
            </select>
          </label>
          <label>
            <span>Namespace</span>
            <input v-model="localNamespace" placeholder="all" @change="emitFilters" />
          </label>
          <label>
            <span>Env</span>
            <select v-model="localEnv" @change="emitFilters">
              <option value="prod">prod</option>
              <option value="staging">staging</option>
              <option value="dev">dev</option>
            </select>
          </label>
        </div>
      </header>
      <section class="content-area">
        <slot />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SideNav from './SideNav.vue'

const props = withDefaults(
  defineProps<{
    title: string
    range?: number
    namespace?: string
    env?: string
  }>(),
  {
    range: 60,
    namespace: '',
    env: 'prod',
  },
)

const emit = defineEmits<{
  filtersChange: [
    {
      range: number
      namespace?: string
      env: string
    },
  ]
}>()

const localRange = ref(String(props.range))
const localNamespace = ref(props.namespace)
const localEnv = ref(props.env)

function emitFilters() {
  emit('filtersChange', {
    range: Number(localRange.value),
    namespace: localNamespace.value || undefined,
    env: localEnv.value,
  })
}
</script>
