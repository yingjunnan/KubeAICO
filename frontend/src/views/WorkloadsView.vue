<template>
  <AppShell title="Resource Management" @filters-change="onFilters">
    <section class="card toolbar">
      <div class="kind-switch">
        <button
          v-for="item in kinds"
          :key="item"
          type="button"
          :class="{ active: kind === item }"
          @click="changeKind(item)"
        >
          {{ item }}
        </button>
      </div>
      <div class="query-fields">
        <input v-model="namespace" placeholder="namespace" @keyup.enter="loadResources" />
        <input v-model="statusFilter" placeholder="status" @keyup.enter="loadResources" />
        <input v-model="labelSelector" placeholder="label app=xxx" @keyup.enter="loadResources" />
        <button class="primary-btn" type="button" @click="loadResources">Query</button>
      </div>
    </section>

    <section class="card">
      <table class="resource-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Namespace</th>
            <th>Status</th>
            <th>Replicas</th>
            <th>Ready</th>
            <th>Restarts</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in resources" :key="`${item.namespace}-${item.name}`">
            <td>{{ item.name }}</td>
            <td>{{ item.namespace }}</td>
            <td>{{ item.status }}</td>
            <td>{{ item.replicas ?? '-' }}</td>
            <td>{{ item.available_replicas ?? '-' }}</td>
            <td>{{ item.restarts }}</td>
            <td>
              <div class="action-row">
                <button
                  v-if="scalableKinds.has(kind)"
                  type="button"
                  @click="openScale(item.name, item.namespace, item.replicas ?? 1)"
                >
                  Scale
                </button>
                <button
                  v-if="scalableKinds.has(kind)"
                  type="button"
                  @click="restart(item.name, item.namespace)"
                >
                  Rollout Restart
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { getResources, rolloutRestart, scaleResource } from '../services/api'
import type { ResourceKind, WorkloadItem } from '../types/api'

const route = useRoute()
const router = useRouter()

const kinds: ResourceKind[] = ['deployment', 'statefulset', 'daemonset', 'pod', 'service', 'ingress']
const scalableKinds = new Set<ResourceKind>(['deployment', 'statefulset', 'daemonset'])

const kind = ref<ResourceKind>((route.query.kind as ResourceKind) || 'deployment')
const namespace = ref('')
const statusFilter = ref('')
const labelSelector = ref('')
const resources = ref<WorkloadItem[]>([])

async function loadResources() {
  const response = await getResources({
    kind: kind.value,
    namespace: namespace.value || undefined,
    status: statusFilter.value || undefined,
    label_selector: labelSelector.value || undefined,
  })
  resources.value = response.items
}

async function changeKind(nextKind: ResourceKind) {
  kind.value = nextKind
  await router.replace({ path: '/workloads', query: { kind: nextKind } })
  await loadResources()
}

async function openScale(name: string, targetNamespace: string, currentReplica: number) {
  const value = window.prompt(`Scale ${name} replicas`, String(currentReplica))
  if (value == null) return
  const replicas = Number(value)
  if (Number.isNaN(replicas) || replicas < 0) return

  if (!window.confirm(`Confirm scaling ${name} to ${replicas} replicas?`)) return

  await scaleResource({
    kind: kind.value,
    name,
    namespace: targetNamespace,
    replicas,
  })
  await loadResources()
}

async function restart(name: string, targetNamespace: string) {
  if (!window.confirm(`Confirm rollout restart ${name}?`)) return

  await rolloutRestart({
    kind: kind.value,
    name,
    namespace: targetNamespace,
  })
  await loadResources()
}

async function onFilters(payload: { range: number; namespace?: string; env: string }) {
  namespace.value = payload.namespace || ''
  await loadResources()
}

onMounted(loadResources)
</script>
