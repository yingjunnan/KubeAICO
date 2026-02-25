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
            <span>Cluster</span>
            <select v-model="localClusterId" @change="onClusterChange">
              <option value="">default</option>
              <option v-for="cluster in activeClusters" :key="cluster.id" :value="cluster.cluster_id">
                {{ cluster.name }}
              </option>
            </select>
          </label>
          <label>
            <span>Namespace</span>
            <input v-model="localNamespace" placeholder="all" @change="emitFilters" />
          </label>
          <label>
            <span>Env</span>
            <select v-model="localEnv" @change="emitFilters">
              <option value="">all</option>
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
import { computed, onMounted, ref } from 'vue'
import SideNav from './SideNav.vue'
import { getClusters } from '../services/api'
import type { ManagedCluster } from '../types/api'

const CLUSTER_STORAGE_KEY = 'kubeaico_selected_cluster_id'

const props = withDefaults(
  defineProps<{
    title: string
    range?: number
    namespace?: string
    clusterId?: string
    env?: string
  }>(),
  {
    range: 60,
    namespace: '',
    clusterId: '',
    env: '',
  },
)

const emit = defineEmits<{
  filtersChange: [
    {
      range: number
      namespace?: string
      cluster_id?: string
      env?: string
    },
  ]
}>()

const localRange = ref(String(props.range))
const localNamespace = ref(props.namespace)
const localClusterId = ref(props.clusterId)
const localEnv = ref(props.env)
const clusters = ref<ManagedCluster[]>([])

const activeClusters = computed(() => clusters.value.filter((cluster) => cluster.is_active))

async function loadClusterOptions() {
  try {
    const response = await getClusters()
    clusters.value = response.items

    const validClusterIds = new Set(activeClusters.value.map((item) => item.cluster_id))
    const persistedClusterId = localStorage.getItem(CLUSTER_STORAGE_KEY) || ''

    if (!localClusterId.value) {
      if (persistedClusterId && validClusterIds.has(persistedClusterId)) {
        localClusterId.value = persistedClusterId
      } else {
        localClusterId.value = activeClusters.value[0]?.cluster_id || ''
      }
    } else if (!validClusterIds.has(localClusterId.value)) {
      localClusterId.value = ''
    }
  } catch {
    clusters.value = []
  }
  onClusterChange()
}

function onClusterChange() {
  if (localClusterId.value) {
    localStorage.setItem(CLUSTER_STORAGE_KEY, localClusterId.value)
  } else {
    localStorage.removeItem(CLUSTER_STORAGE_KEY)
  }
  emitFilters()
}

function emitFilters() {
  emit('filtersChange', {
    range: Number(localRange.value),
    namespace: localNamespace.value || undefined,
    cluster_id: localClusterId.value || undefined,
    env: localEnv.value || undefined,
  })
}

onMounted(() => {
  void loadClusterOptions()
})
</script>
