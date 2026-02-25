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
        <div class="detail-header-actions">
          <button type="button" @click="loadDetailLogs" :disabled="detailLogs.loading">
            {{ detailLogs.loading ? 'Loading Logs...' : detailLogs.loaded ? 'Reload Logs' : 'Load Logs' }}
          </button>
          <button type="button" @click="closeDetailPanel">Close</button>
        </div>
      </div>
      <p class="hint">
        Namespace: {{ detail.item.namespace }} | Status: {{ detail.item.status }} |
        Restarts: {{ detail.item.restarts }}
      </p>

      <section v-if="detail.metrics?.series?.length" class="detail-metrics-grid">
        <TrendChart
          v-for="(series, idx) in detail.metrics.series"
          :key="series.key"
          :title="series.label"
          :subtitle="`Latest ${latestDisplay(series)} • Unit ${unitLabel(series)}`"
          :x-axis="axisFromPoints(series.points)"
          :values="displayValues(series)"
          :color="chartColor(idx)"
        />
      </section>

      <div class="detail-grid">
        <article>
          <h4>Resource Manifest (YAML)</h4>
          <pre>{{ detailManifestYaml }}</pre>
        </article>
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
      </div>

      <article class="detail-logs-card">
        <div class="detail-logs-header">
          <h4>Recent Logs</h4>
          <button type="button" @click="loadDetailLogs" :disabled="detailLogs.loading">
            {{ detailLogs.loading ? 'Loading...' : detailLogs.loaded ? 'Refresh' : 'Load' }}
          </button>
        </div>
        <p v-if="!detailLogs.loaded && !detailLogs.loading && !detailLogs.error" class="hint">
          Logs are loaded on demand. Click "Load Logs" to fetch the latest lines.
        </p>
        <p v-if="detailLogs.error" class="error-text">{{ detailLogs.error }}</p>
        <pre v-if="detailLogs.loaded">{{ detailLogs.lines.join('\n') || 'No logs available.' }}</pre>
      </article>
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
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import TrendChart from '../components/TrendChart.vue'
import { getResourceDetail, getResourceLogs, getResources, rolloutRestart, scaleResource } from '../services/api'
import type { ResourceDetailResponse, ResourceKind, ResourceMetricSeries, WorkloadItem } from '../types/api'

const route = useRoute()
const router = useRouter()

const validKinds: ResourceKind[] = ['deployment', 'statefulset', 'daemonset', 'pod', 'service', 'ingress']
const scalableKinds = new Set<ResourceKind>(['deployment', 'statefulset', 'daemonset'])

const kind = ref<ResourceKind>('deployment')
const namespace = ref('')
const clusterId = ref('')
const statusFilter = ref('')
const labelSelector = ref('')
const resources = ref<WorkloadItem[]>([])
const detail = ref<ResourceDetailResponse | null>(null)
const detailLogs = ref<{
  loaded: boolean
  loading: boolean
  error: string
  lines: string[]
}>({
  loaded: false,
  loading: false,
  error: '',
  lines: [],
})
const scaleReplicas = ref(1)
let detailRequestSeq = 0
let logsRequestSeq = 0

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
    cluster_id: clusterId.value || undefined,
  })
  resources.value = response.items

  if (
    detail.value &&
    (
      detail.value.item.kind !== kind.value ||
      !resources.value.some(
        (item) =>
          item.name === detail.value?.item.name &&
          item.namespace === detail.value?.item.namespace,
      )
    )
  ) {
    closeDetailPanel()
  }
}

function resetDetailLogs() {
  logsRequestSeq += 1
  detailLogs.value = {
    loaded: false,
    loading: false,
    error: '',
    lines: [],
  }
}

function closeDetailPanel() {
  detail.value = null
  resetDetailLogs()
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
        cluster_id: clusterId.value || undefined,
      })
    } else {
      await rolloutRestart({
        kind: kind.value,
        name: target.name,
        namespace: target.namespace,
        cluster_id: clusterId.value || undefined,
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
  resetDetailLogs()
  const requestSeq = ++detailRequestSeq
  const requestedKind = kind.value
  const requestedName = name
  const requestedNamespace = targetNamespace

  const response = await getResourceDetail({
    kind: kind.value,
    name,
    namespace: targetNamespace,
    range_minutes: 10,
    step_seconds: 30,
    cluster_id: clusterId.value || undefined,
  })

  if (
    requestSeq !== detailRequestSeq ||
    kind.value !== requestedKind ||
    !resources.value.some(
      (item) => item.name === requestedName && item.namespace === requestedNamespace,
    )
  ) {
    return
  }

  detail.value = response
}

async function loadDetailLogs() {
  if (!detail.value || detailLogs.value.loading) return

  const activeDetail = detail.value
  const requestSeq = ++logsRequestSeq
  detailLogs.value.loading = true
  detailLogs.value.error = ''

  try {
    const response = await getResourceLogs({
      kind: activeDetail.item.kind,
      name: activeDetail.item.name,
      namespace: activeDetail.item.namespace,
      log_lines: 180,
      cluster_id: clusterId.value || undefined,
    })

    if (
      requestSeq !== logsRequestSeq ||
      !detail.value ||
      detail.value.item.kind !== activeDetail.item.kind ||
      detail.value.item.name !== activeDetail.item.name ||
      detail.value.item.namespace !== activeDetail.item.namespace
    ) {
      return
    }

    detailLogs.value.lines = response.logs
    detailLogs.value.loaded = true
  } catch (error) {
    if (requestSeq !== logsRequestSeq) {
      return
    }
    detailLogs.value.error = 'Load logs failed. Please retry.'
  } finally {
    if (requestSeq === logsRequestSeq) {
      detailLogs.value.loading = false
    }
  }
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return Object.prototype.toString.call(value) === '[object Object]'
}

function yamlScalar(value: unknown): string {
  if (value === null || value === undefined) return 'null'
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : `"${String(value)}"`
  const text = String(value)
  if (!text) return '""'
  if (/^[A-Za-z0-9._/-]+$/.test(text)) return text
  return JSON.stringify(text)
}

function yamlLines(value: unknown, indent: number): string[] {
  const pad = ' '.repeat(indent)

  if (Array.isArray(value)) {
    if (value.length === 0) return [`${pad}[]`]

    const lines: string[] = []
    for (const item of value) {
      if (Array.isArray(item) || isPlainObject(item)) {
        lines.push(`${pad}-`)
        lines.push(...yamlLines(item, indent + 2))
      } else {
        lines.push(`${pad}- ${yamlScalar(item)}`)
      }
    }
    return lines
  }

  if (isPlainObject(value)) {
    const entries = Object.entries(value)
    if (entries.length === 0) return [`${pad}{}`]

    const lines: string[] = []
    for (const [key, item] of entries) {
      if (Array.isArray(item) || isPlainObject(item)) {
        lines.push(`${pad}${key}:`)
        lines.push(...yamlLines(item, indent + 2))
      } else {
        lines.push(`${pad}${key}: ${yamlScalar(item)}`)
      }
    }
    return lines
  }

  return [`${pad}${yamlScalar(value)}`]
}

const detailManifestYaml = computed(() => {
  if (!detail.value) return ''
  const manifest = detail.value.manifest || {}
  return yamlLines(manifest, 0).join('\n')
})

function axisFromPoints(points: { ts: number; value: number }[]): string[] {
  return points.map((point) => {
    const date = new Date(point.ts * 1000)
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  })
}

function valueScale(unit: string): number {
  if (unit === 'bytes') return 1024 ** 3
  if (unit === 'bytes_per_second') return 1024 ** 2
  if (unit === 'ratio') return 0.01
  return 1
}

function displayValues(series: ResourceMetricSeries): number[] {
  if (series.unit === 'ratio') {
    return series.points.map((point) => Number((point.value * 100).toFixed(3)))
  }
  const scale = valueScale(series.unit)
  return series.points.map((point) => Number((point.value / scale).toFixed(3)))
}

function latestDisplay(series: ResourceMetricSeries): string {
  const latest = series.points[series.points.length - 1]?.value ?? 0
  if (series.unit === 'cores') return `${latest.toFixed(2)} cores`
  if (series.unit === 'bytes') return `${(latest / 1024 ** 3).toFixed(2)} GiB`
  if (series.unit === 'bytes_per_second') return `${(latest / 1024 ** 2).toFixed(2)} MiB/s`
  if (series.unit === 'ratio') return `${(latest * 100).toFixed(2)} %`
  if (series.unit === 'replicas') return `${latest.toFixed(0)} replicas`
  return String(latest)
}

function unitLabel(series: ResourceMetricSeries): string {
  if (series.unit === 'cores') return 'cores'
  if (series.unit === 'bytes') return 'GiB'
  if (series.unit === 'bytes_per_second') return 'MiB/s'
  if (series.unit === 'ratio') return '%'
  if (series.unit === 'replicas') return 'replicas'
  return series.unit
}

function chartColor(index: number): string {
  const palette = ['#69bfa0', '#4ea8de', '#f0a868', '#8f8cf2', '#62c7b3', '#d981a7']
  return palette[index % palette.length]
}

async function onFilters(payload: { range: number; namespace?: string; cluster_id?: string; env?: string }) {
  namespace.value = payload.namespace || ''
  clusterId.value = payload.cluster_id || ''
  await loadResources()
}

onMounted(async () => {
  await syncKindFromRoute(route.query.kind)
  await loadResources()
})

watch(
  () => route.query.kind,
  async (nextKind) => {
    detailRequestSeq += 1
    closeDetailPanel()
    await syncKindFromRoute(nextKind)
    await loadResources()
  },
)
</script>
