<template>
  <AppShell title="Resource Management" @filters-change="onFilters">
    <section class="card toolbar">
      <div class="toolbar-title">
        <p class="eyebrow">Resource Type</p>
        <h3>{{ kind }}</h3>
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
                  type="button"
                  @click="openDetail(item.name, item.namespace)"
                >
                  Detail
                </button>
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

    <section v-if="detail" class="card detail-panel">
      <div class="detail-header">
        <h3>{{ detail.item.kind }}/{{ detail.item.name }}</h3>
        <button type="button" @click="detail = null">Close</button>
      </div>
      <p class="hint">
        Namespace: {{ detail.item.namespace }} | Status: {{ detail.item.status }} |
        Restarts: {{ detail.item.restarts }}
      </p>

      <div class="detail-grid">
        <article>
          <h4>Recent Events</h4>
          <ul>
            <li v-for="(event, idx) in detail.events" :key="`${event.reason}-${idx}`">
              <strong>{{ event.type }}/{{ event.reason }}</strong>
              <span>{{ event.message }}</span>
            </li>
            <li v-if="detail.events.length === 0" class="hint">No related events.</li>
          </ul>
        </article>
        <article>
          <h4>Recent Logs</h4>
          <pre>{{ detail.logs.join('\n') || 'No logs available.' }}</pre>
        </article>
      </div>
    </section>

    <Teleport to="body">
      <div v-if="operationModal.visible" class="theme-modal-backdrop" @click.self="closeOperationModal">
        <section class="theme-modal">
          <header class="theme-modal-header">
            <h3>
              {{ operationModal.type === 'scale' ? 'Scale Workload' : 'Rollout Restart' }}
            </h3>
            <button type="button" @click="closeOperationModal">Close</button>
          </header>

          <div class="theme-modal-body">
            <p v-if="operationModal.target">
              Target:
              <strong>
                {{ kind }}/{{ operationModal.target.name }}
              </strong>
              in namespace
              <strong>{{ operationModal.target.namespace }}</strong>
            </p>

            <label v-if="operationModal.type === 'scale'" class="theme-modal-field">
              <span>Replicas</span>
              <input
                v-model.number="scaleReplicas"
                type="number"
                min="0"
                max="1000"
                step="1"
              />
            </label>

            <p v-else class="hint">
              This will patch workload template annotations to trigger a rolling restart.
            </p>

            <p v-if="operationModal.error" class="error-text">{{ operationModal.error }}</p>
          </div>

          <footer class="theme-modal-actions">
            <button type="button" @click="closeOperationModal" :disabled="operationModal.submitting">
              Cancel
            </button>
            <button class="primary-btn" type="button" @click="submitOperation" :disabled="operationModal.submitting">
              {{
                operationModal.submitting
                  ? 'Submitting...'
                  : operationModal.type === 'scale'
                    ? 'Apply Scale'
                    : 'Confirm Restart'
              }}
            </button>
          </footer>
        </section>
      </div>
    </Teleport>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { getResourceDetail, getResources, rolloutRestart, scaleResource } from '../services/api'
import type { ResourceDetailResponse, ResourceKind, WorkloadItem } from '../types/api'

const route = useRoute()
const router = useRouter()

const validKinds: ResourceKind[] = ['deployment', 'statefulset', 'daemonset', 'pod', 'service', 'ingress']
const scalableKinds = new Set<ResourceKind>(['deployment', 'statefulset', 'daemonset'])

const kind = ref<ResourceKind>('deployment')
const namespace = ref('')
const statusFilter = ref('')
const labelSelector = ref('')
const resources = ref<WorkloadItem[]>([])
const detail = ref<ResourceDetailResponse | null>(null)
const scaleReplicas = ref(1)

const operationModal = ref<{
  visible: boolean
  type: 'scale' | 'restart'
  target: { name: string; namespace: string } | null
  error: string
  submitting: boolean
}>({
  visible: false,
  type: 'scale',
  target: null,
  error: '',
  submitting: false,
})

async function loadResources() {
  const response = await getResources({
    kind: kind.value,
    namespace: namespace.value || undefined,
    status: statusFilter.value || undefined,
    label_selector: labelSelector.value || undefined,
  })
  resources.value = response.items
}

async function syncKindFromRoute(nextKindRaw: unknown) {
  const nextKind = String(nextKindRaw || '').toLowerCase()
  if (!validKinds.includes(nextKind as ResourceKind)) {
    kind.value = 'deployment'
    await router.replace({ path: '/workloads', query: { kind: 'deployment' } })
    return
  }
  kind.value = nextKind as ResourceKind
}

function openScale(name: string, targetNamespace: string, currentReplica: number) {
  scaleReplicas.value = currentReplica
  operationModal.value = {
    visible: true,
    type: 'scale',
    target: { name, namespace: targetNamespace },
    error: '',
    submitting: false,
  }
}

function restart(name: string, targetNamespace: string) {
  operationModal.value = {
    visible: true,
    type: 'restart',
    target: { name, namespace: targetNamespace },
    error: '',
    submitting: false,
  }
}

function closeOperationModal() {
  if (operationModal.value.submitting) return
  operationModal.value.visible = false
  operationModal.value.error = ''
}

async function submitOperation() {
  const target = operationModal.value.target
  if (!target) return

  operationModal.value.error = ''
  operationModal.value.submitting = true

  try {
    if (operationModal.value.type === 'scale') {
      if (!Number.isInteger(scaleReplicas.value) || scaleReplicas.value < 0 || scaleReplicas.value > 1000) {
        operationModal.value.error = 'Replicas must be an integer between 0 and 1000.'
        return
      }
      await scaleResource({
        kind: kind.value,
        name: target.name,
        namespace: target.namespace,
        replicas: scaleReplicas.value,
      })
    } else {
      await rolloutRestart({
        kind: kind.value,
        name: target.name,
        namespace: target.namespace,
      })
    }

    operationModal.value.visible = false
    await loadResources()
  } catch (error) {
    operationModal.value.error = 'Operation failed. Please retry.'
  } finally {
    operationModal.value.submitting = false
  }
}

async function openDetail(name: string, targetNamespace: string) {
  detail.value = await getResourceDetail({
    kind: kind.value,
    name,
    namespace: targetNamespace,
    log_lines: 120,
  })
}

async function onFilters(payload: { range: number; namespace?: string; env: string }) {
  namespace.value = payload.namespace || ''
  await loadResources()
}

onMounted(async () => {
  await syncKindFromRoute(route.query.kind)
  await loadResources()
})

watch(
  () => route.query.kind,
  async (nextKind) => {
    await syncKindFromRoute(nextKind)
    await loadResources()
  },
)
</script>
