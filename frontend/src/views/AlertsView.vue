<template>
  <AppShell title="Alerts & Fault Events" @filters-change="onFilters">
    <section class="alerts-grid">
      <article v-for="item in alerts" :key="item.id" class="card alert-card">
        <div class="alert-head">
          <span :class="['badge', item.severity.toLowerCase()]">{{ item.severity }}</span>
          <span class="source">{{ item.source }}</span>
          <time>{{ formatTime(item.start_time) }}</time>
        </div>
        <h3>{{ item.title }}</h3>
        <p>{{ item.message }}</p>
        <div class="recommendation">
          <strong>Suggestion:</strong>
          <span>{{ item.recommendation }}</span>
        </div>
      </article>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { getAlerts } from '../services/api'
import type { AlertItem } from '../types/api'

const alerts = ref<AlertItem[]>([])
const namespace = ref('')
const clusterId = ref('')

async function loadAlerts() {
  const response = await getAlerts({
    namespace: namespace.value || undefined,
    limit: 50,
    cluster_id: clusterId.value || undefined,
  })
  alerts.value = response.items
}

function onFilters(payload: { range: number; namespace?: string; cluster_id?: string; env?: string }) {
  namespace.value = payload.namespace || ''
  clusterId.value = payload.cluster_id || ''
  void loadAlerts()
}

function formatTime(ts: string) {
  const date = new Date(ts)
  return date.toLocaleString()
}

onMounted(loadAlerts)
</script>
