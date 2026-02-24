<template>
  <AppShell title="Audit Logs" @filters-change="onFilters">
    <section class="card toolbar">
      <div class="query-fields">
        <input v-model="action" placeholder="action (scale/restart)" @keyup.enter="loadLogs" />
        <input v-model="kind" placeholder="kind (deployment)" @keyup.enter="loadLogs" />
        <input v-model="namespace" placeholder="namespace" @keyup.enter="loadLogs" />
        <button class="primary-btn" type="button" @click="loadLogs">Query</button>
      </div>
    </section>

    <section class="card">
      <table class="resource-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Time</th>
            <th>Action</th>
            <th>Target</th>
            <th>Namespace</th>
            <th>Status</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in items" :key="log.id">
            <td>#{{ log.id }}</td>
            <td>{{ formatTime(log.created_at) }}</td>
            <td>{{ log.action }}</td>
            <td>{{ log.target_kind }}/{{ log.target_name }}</td>
            <td>{{ log.namespace ?? '-' }}</td>
            <td>{{ log.status }}</td>
            <td>{{ log.message ?? '-' }}</td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="7" class="empty-row">No logs found.</td>
          </tr>
        </tbody>
      </table>
      <div class="pager">
        <button type="button" :disabled="offset === 0" @click="prevPage">Previous</button>
        <span>Offset {{ offset }} / Total {{ total }}</span>
        <button type="button" :disabled="offset + limit >= total" @click="nextPage">Next</button>
      </div>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { getAuditLogs } from '../services/api'
import type { AuditLogItem } from '../types/api'

const items = ref<AuditLogItem[]>([])
const total = ref(0)
const limit = ref(30)
const offset = ref(0)

const action = ref('')
const kind = ref('')
const namespace = ref('')

async function loadLogs() {
  const response = await getAuditLogs({
    limit: limit.value,
    offset: offset.value,
    action: action.value || undefined,
    kind: kind.value || undefined,
    namespace: namespace.value || undefined,
  })
  total.value = response.total
  items.value = response.items
}

async function prevPage() {
  offset.value = Math.max(0, offset.value - limit.value)
  await loadLogs()
}

async function nextPage() {
  offset.value += limit.value
  await loadLogs()
}

function onFilters(payload: { range: number; namespace?: string; env: string }) {
  namespace.value = payload.namespace || ''
  offset.value = 0
  void loadLogs()
}

function formatTime(ts: string) {
  return new Date(ts).toLocaleString()
}

onMounted(loadLogs)
</script>
