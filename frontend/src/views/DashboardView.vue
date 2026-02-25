<template>
  <AppShell
    title="Cluster Overview"
    :range="filters.range"
    :namespace="filters.namespace"
    :cluster-id="filters.cluster_id"
    :env="filters.env"
    @filters-change="updateFilters"
  >
    <section class="hero card">
      <div class="hero-copy">
        <p class="eyebrow">AI Predictive Operations</p>
        <h2>Kubernetes Predictive Strategy</h2>
        <p>
          Real-time cluster health, load trends, anomaly signals, and actionable operations.
        </p>
      </div>
      <div class="hero-visual">
        <div class="bubble bubble-lg"></div>
        <div class="bubble bubble-md"></div>
        <div class="bubble bubble-sm"></div>
        <div class="risk-pill">Risk Score: {{ summary?.risk_score ?? '-' }}</div>
      </div>
    </section>

    <section class="stats-grid">
      <MetricCard title="Node Health" :value="nodeHealth" subtitle="Ready / Total" />
      <MetricCard title="Pod Health" :value="podHealth" subtitle="Pending / CrashLoop / OOM" />
      <MetricCard title="CPU Usage" :value="cpuUsage" subtitle="Used / Capacity" />
      <MetricCard title="Memory Usage" :value="memoryUsage" subtitle="Used / Capacity" />
      <MetricCard title="Open Alerts" :value="String(summary?.alerts_count ?? 0)" subtitle="K8s + Prometheus" />
    </section>

    <section class="charts-grid">
      <TrendChart title="CPU Trend" subtitle="cluster cpu usage" :x-axis="cpuXAxis" :values="cpuValues" />
      <TrendChart title="Memory Trend" subtitle="cluster memory usage" :x-axis="memXAxis" :values="memValues" color="#69bfa0" />
      <article class="card ns-card">
        <h3>Top Namespaces</h3>
        <ul>
          <li v-for="ns in summary?.top_namespaces ?? []" :key="ns.namespace">
            <span>{{ ns.namespace }}</span>
            <strong>{{ ns.pod_count }} pods</strong>
          </li>
        </ul>
      </article>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import MetricCard from '../components/MetricCard.vue'
import TrendChart from '../components/TrendChart.vue'
import { clearAuthAndRedirectToLogin, getOverviewSummary, getTimeseries, getWsOverviewUrl } from '../services/api'
import type { ClusterSummary } from '../types/api'

const summary = ref<ClusterSummary | null>(null)
const cpuXAxis = ref<string[]>([])
const memXAxis = ref<string[]>([])
const cpuValues = ref<number[]>([])
const memValues = ref<number[]>([])

const filters = reactive({
  range: 60,
  namespace: '',
  cluster_id: '',
  env: '',
})

let ws: WebSocket | null = null

const nodeHealth = computed(() => {
  if (!summary.value) return '-'
  return `${summary.value.nodes_ready}/${summary.value.nodes_total}`
})

const podHealth = computed(() => {
  if (!summary.value) return '-'
  return `${summary.value.pods_pending}/${summary.value.pods_crashloop}/${summary.value.pods_oomkilled}`
})

const cpuUsage = computed(() => {
  if (!summary.value) return '-'
  return `${summary.value.cpu_usage_cores.toFixed(1)} / ${summary.value.cpu_capacity_cores.toFixed(1)} cores`
})

const memoryUsage = computed(() => {
  if (!summary.value) return '-'
  const used = (summary.value.memory_usage_bytes / 1024 ** 3).toFixed(1)
  const total = (summary.value.memory_capacity_bytes / 1024 ** 3).toFixed(1)
  return `${used} / ${total} GiB`
})

function toAxis(ts: number): string {
  const d = new Date(ts * 1000)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

async function loadSummaryAndCharts() {
  const [summaryRes, cpu, mem] = await Promise.all([
    getOverviewSummary({ cluster_id: filters.cluster_id || undefined }),
    getTimeseries({
      metric: 'cpu_usage',
      range_minutes: filters.range,
      namespace: filters.namespace || undefined,
      cluster_id: filters.cluster_id || undefined,
    }),
    getTimeseries({
      metric: 'memory_usage',
      range_minutes: filters.range,
      namespace: filters.namespace || undefined,
      cluster_id: filters.cluster_id || undefined,
    }),
  ])

  summary.value = summaryRes

  const cpuPoints = cpu.series[0]?.points ?? []
  cpuXAxis.value = cpuPoints.map((p) => toAxis(p.ts))
  cpuValues.value = cpuPoints.map((p) => Number(p.value.toFixed(3)))

  const memPoints = mem.series[0]?.points ?? []
  memXAxis.value = memPoints.map((p) => toAxis(p.ts))
  memValues.value = memPoints.map((p) => Number((p.value / 1024 ** 3).toFixed(2)))
}

function connectWs() {
  const token = localStorage.getItem('kubeaico_token')
  if (!token) return

  ws = new WebSocket(getWsOverviewUrl(token, filters.cluster_id || undefined))
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data) as ClusterSummary
    summary.value = data
  }
  ws.onclose = (event) => {
    if (event.code === 4401 || event.code === 4403) {
      clearAuthAndRedirectToLogin()
    }
  }
}

async function updateFilters(next: { range: number; namespace?: string; cluster_id?: string; env?: string }) {
  const changedCluster = filters.cluster_id !== (next.cluster_id ?? '')
  filters.range = next.range
  filters.namespace = next.namespace ?? ''
  filters.cluster_id = next.cluster_id ?? ''
  filters.env = next.env ?? ''
  await loadSummaryAndCharts()
  if (changedCluster) {
    ws?.close()
    connectWs()
  }
}

onMounted(async () => {
  await loadSummaryAndCharts()
  connectWs()
})

onBeforeUnmount(() => {
  ws?.close()
})
</script>
