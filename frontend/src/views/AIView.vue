<template>
  <AppShell title="AI Analysis" @filters-change="onFilters">
    <section class="ai-layout">
      <article class="card ai-form">
        <h3>Run Cluster Analysis</h3>
        <p>Submit current operational snapshot for rule-based diagnosis and LLM extension interface.</p>

        <label>
          <span>Namespace</span>
          <input v-model="namespace" placeholder="default" />
        </label>
        <label>
          <span>Workload (optional)</span>
          <input v-model="workload" placeholder="api" />
        </label>

        <div class="metric-inputs">
          <label><span>CPU Utilization %</span><input v-model.number="cpu" type="number" min="0" max="100" /></label>
          <label><span>Memory Utilization %</span><input v-model.number="memory" type="number" min="0" max="100" /></label>
          <label><span>Restart Rate</span><input v-model.number="restartRate" type="number" min="0" step="0.01" /></label>
          <label><span>Error Rate</span><input v-model.number="errorRate" type="number" min="0" step="0.01" /></label>
        </div>

        <button class="primary-btn" :disabled="loading" @click="runAnalyze">
          {{ loading ? 'Analyzing...' : 'Start Analysis' }}
        </button>

        <p v-if="taskStatus" class="hint">Task status: {{ taskStatus }}</p>
      </article>

      <article class="card ai-result">
        <h3>Analysis Result</h3>
        <template v-if="result">
          <p class="result-summary">{{ result.summary }}</p>
          <p><strong>Risk Level:</strong> {{ result.risk_level }}</p>

          <h4>Root Causes</h4>
          <ul>
            <li v-for="(cause, idx) in result.root_causes" :key="idx">
              {{ cause.cause }} (confidence {{ Math.round(cause.confidence * 100) }}%)
            </li>
          </ul>

          <h4>Recommendations</h4>
          <ul>
            <li v-for="(item, idx) in result.recommendations" :key="idx">{{ item }}</li>
          </ul>
        </template>
        <p v-else class="hint">No analysis yet.</p>
      </article>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { createAnalyzeTask, getAnalyzeTask } from '../services/api'
import type { AIAnalyzeResult } from '../types/api'

const namespace = ref('default')
const workload = ref('')
const cpu = ref(65)
const memory = ref(72)
const restartRate = ref(0.02)
const errorRate = ref(0.01)

const loading = ref(false)
const taskStatus = ref('')
const result = ref<AIAnalyzeResult | null>(null)

let pollTimer: number | null = null

function clearPoll() {
  if (pollTimer) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
}

async function runAnalyze() {
  loading.value = true
  result.value = null

  try {
    const task = await createAnalyzeTask({
      namespace: namespace.value || undefined,
      workload: workload.value || undefined,
      metrics: [
        { name: 'cpu_utilization', value: cpu.value },
        { name: 'memory_utilization', value: memory.value },
        { name: 'restart_rate', value: restartRate.value },
        { name: 'error_rate', value: errorRate.value },
      ],
      events: [],
    })

    taskStatus.value = task.status

    clearPoll()
    pollTimer = window.setInterval(async () => {
      const latest = await getAnalyzeTask(task.task_id)
      taskStatus.value = latest.status
      if (latest.status === 'completed') {
        result.value = latest.result ?? null
        loading.value = false
        clearPoll()
      }
      if (latest.status === 'failed') {
        loading.value = false
        clearPoll()
      }
    }, 1500)
  } catch {
    loading.value = false
    clearPoll()
  }
}

function onFilters(payload: { range: number; namespace?: string; env: string }) {
  namespace.value = payload.namespace || namespace.value
}
</script>
