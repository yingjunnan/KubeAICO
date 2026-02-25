<template>
  <AppShell title="Cluster Management" @filters-change="noopFilters">
    <section class="card toolbar">
      <div class="toolbar-title">
        <p class="eyebrow">Managed Clusters</p>
        <h3>{{ clusters.length }} configured</h3>
      </div>
      <div class="query-fields">
        <button class="primary-btn" type="button" @click="openCreate">Add Cluster</button>
      </div>
    </section>

    <section class="card">
      <table class="resource-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Cluster ID</th>
            <th>K8s API</th>
            <th>Prometheus</th>
            <th>Token</th>
            <th>Status</th>
            <th>Updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cluster in clusters" :key="cluster.id">
            <td>{{ cluster.name }}</td>
            <td>{{ cluster.cluster_id }}</td>
            <td>{{ cluster.k8s_api_url }}</td>
            <td>{{ cluster.prometheus_url || '-' }}</td>
            <td>{{ cluster.k8s_bearer_token_masked || '-' }}</td>
            <td>
              <span :class="['badge', cluster.is_active ? 'active' : 'paused']">
                {{ cluster.is_active ? 'ACTIVE' : 'DISABLED' }}
              </span>
            </td>
            <td>{{ formatTime(cluster.updated_at) }}</td>
            <td>
              <div class="action-row">
                <button type="button" @click="openEdit(cluster.id)">Edit</button>
                <button type="button" :disabled="savedTestingId === cluster.id" @click="testSavedConnection(cluster.id)">
                  {{ savedTestingId === cluster.id ? 'Testing...' : 'Detect' }}
                </button>
                <button type="button" @click="toggleStatus(cluster.id)">
                  {{ getCluster(cluster.id)?.is_active ? 'Disable' : 'Enable' }}
                </button>
                <button type="button" @click="openDelete(cluster.id)">Delete</button>
              </div>
              <p v-if="savedTestMessages[cluster.id]" class="hint">{{ savedTestMessages[cluster.id] }}</p>
            </td>
          </tr>
          <tr v-if="clusters.length === 0">
            <td colspan="8" class="empty-row">No clusters configured yet.</td>
          </tr>
        </tbody>
      </table>
    </section>

    <Teleport to="body">
      <div v-if="formVisible" class="theme-modal-backdrop" @click.self="closeForm">
        <section class="theme-modal cluster-form-modal">
          <header class="theme-modal-header">
            <h3>{{ editingId ? 'Edit Cluster' : 'Add Cluster' }}</h3>
            <button type="button" @click="closeForm">Close</button>
          </header>

          <div class="theme-modal-body cluster-form-grid">
            <label class="theme-modal-field">
              <span>Name</span>
              <input v-model="form.name" placeholder="Production Cluster" />
            </label>
            <label class="theme-modal-field">
              <span>Cluster ID</span>
              <input v-model="form.cluster_id" placeholder="cluster-prod" />
            </label>
            <label class="theme-modal-field">
              <span>K8s API URL</span>
              <input v-model="form.k8s_api_url" placeholder="https://api.k8s.local:6443" />
            </label>
            <label class="theme-modal-field">
              <span>Prometheus URL</span>
              <input v-model="form.prometheus_url" placeholder="http://prometheus.monitoring:9090" />
            </label>
            <label class="theme-modal-field">
              <span>Bearer Token</span>
              <input v-model="form.k8s_bearer_token" placeholder="Optional update" />
            </label>
            <label class="theme-modal-field">
              <span>Description</span>
              <input v-model="form.description" placeholder="Primary production environment" />
            </label>
            <label class="theme-modal-field checkbox-field">
              <input v-model="form.is_active" type="checkbox" />
              <span>Enable this cluster</span>
            </label>
            <p v-if="draftTestMessage" :class="draftTestPassedSignature ? 'hint' : 'error-text'">
              {{ draftTestMessage }}
            </p>
            <p v-if="formError" class="error-text">{{ formError }}</p>
          </div>

          <footer class="theme-modal-actions">
            <button type="button" :disabled="submitting" @click="closeForm">Cancel</button>
            <button type="button" :disabled="submitting || draftTesting" @click="testDraftConnection">
              {{ draftTesting ? 'Testing...' : 'Test Connection' }}
            </button>
            <button class="primary-btn" type="button" :disabled="submitting" @click="submitForm">
              {{ submitting ? 'Saving...' : editingId ? 'Save Changes' : 'Create Cluster' }}
            </button>
          </footer>
        </section>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="deleteModal.visible" class="theme-modal-backdrop" @click.self="closeDeleteModal">
        <section class="theme-modal">
          <header class="theme-modal-header">
            <h3>Delete Cluster</h3>
            <button type="button" @click="closeDeleteModal">Close</button>
          </header>

          <div class="theme-modal-body">
            <p v-if="deleteModal.target">
              This operation will remove
              <strong>{{ deleteModal.target.name }}</strong>
              from managed clusters.
            </p>
            <p class="hint">This only deletes saved connection metadata, not the real Kubernetes cluster.</p>
          </div>

          <footer class="theme-modal-actions">
            <button type="button" :disabled="deleteModal.submitting" @click="closeDeleteModal">Cancel</button>
            <button class="primary-btn" type="button" :disabled="deleteModal.submitting" @click="confirmDelete">
              {{ deleteModal.submitting ? 'Deleting...' : 'Confirm Delete' }}
            </button>
          </footer>
        </section>
      </div>
    </Teleport>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import {
  createCluster,
  deleteCluster,
  getClusters,
  testClusterConnection,
  testClusterConnectionDraft,
  updateCluster,
} from '../services/api'
import type { ClusterConnectionTestResponse, ManagedCluster } from '../types/api'

const clusters = ref<ManagedCluster[]>([])
const formVisible = ref(false)
const editingId = ref<number | null>(null)
const submitting = ref(false)
const formError = ref('')
const draftTesting = ref(false)
const draftTestMessage = ref('')
const draftTestPassedSignature = ref('')
const savedTestingId = ref<number | null>(null)
const savedTestMessages = ref<Record<number, string>>({})
const deleteModal = ref<{
  visible: boolean
  target: ManagedCluster | null
  submitting: boolean
}>({
  visible: false,
  target: null,
  submitting: false,
})

const form = reactive({
  name: '',
  cluster_id: '',
  k8s_api_url: '',
  prometheus_url: '',
  k8s_bearer_token: '',
  is_active: true,
  description: '',
})

async function loadClusters() {
  const response = await getClusters()
  clusters.value = response.items
}

function noopFilters() {
  return
}

function resetForm() {
  form.name = ''
  form.cluster_id = ''
  form.k8s_api_url = ''
  form.prometheus_url = ''
  form.k8s_bearer_token = ''
  form.is_active = true
  form.description = ''
  formError.value = ''
  draftTesting.value = false
  draftTestMessage.value = ''
  draftTestPassedSignature.value = ''
}

function closeForm() {
  if (submitting.value) return
  formVisible.value = false
  editingId.value = null
  resetForm()
}

function openCreate() {
  editingId.value = null
  resetForm()
  formVisible.value = true
}

function openEdit(id: number) {
  const row = getCluster(id)
  if (!row) return
  editingId.value = id
  form.name = row.name
  form.cluster_id = row.cluster_id
  form.k8s_api_url = row.k8s_api_url
  form.prometheus_url = row.prometheus_url || ''
  form.k8s_bearer_token = ''
  form.is_active = row.is_active
  form.description = row.description || ''
  formError.value = ''
  draftTesting.value = false
  draftTestMessage.value = ''
  draftTestPassedSignature.value = ''
  formVisible.value = true
}

function getCluster(id: number): ManagedCluster | undefined {
  return clusters.value.find((item) => item.id === id)
}

async function submitForm() {
  formError.value = ''
  if (!form.name.trim() || !form.cluster_id.trim() || !form.k8s_api_url.trim()) {
    formError.value = 'Name, Cluster ID, and K8s API URL are required.'
    return
  }

  if (!editingId.value) {
    const signature = getDraftSignature()
    if (!draftTestPassedSignature.value || draftTestPassedSignature.value !== signature) {
      formError.value = 'Please run Test Connection successfully before creating a new cluster.'
      return
    }
  }

  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(),
      cluster_id: form.cluster_id.trim(),
      k8s_api_url: form.k8s_api_url.trim(),
      prometheus_url: form.prometheus_url.trim() || undefined,
      k8s_bearer_token: form.k8s_bearer_token.trim() || undefined,
      is_active: form.is_active,
      description: form.description.trim() || undefined,
    }

    if (editingId.value) {
      await updateCluster({ cluster_pk: editingId.value, payload })
    } else {
      await createCluster(payload)
    }

    await loadClusters()
    closeForm()
  } catch (error: any) {
    formError.value = error?.response?.data?.detail || 'Failed to save cluster.'
  } finally {
    submitting.value = false
  }
}

async function toggleStatus(id: number) {
  const row = getCluster(id)
  if (!row) return
  await updateCluster({ cluster_pk: id, payload: { is_active: !row.is_active } })
  await loadClusters()
}

function getDraftPayload() {
  return {
    k8s_api_url: form.k8s_api_url.trim(),
    prometheus_url: form.prometheus_url.trim() || undefined,
    k8s_bearer_token: form.k8s_bearer_token.trim() || undefined,
  }
}

function getDraftSignature() {
  return JSON.stringify(getDraftPayload())
}

function formatTestMessage(result: ClusterConnectionTestResponse) {
  const state = result.ok ? 'PASS' : 'FAIL'
  return `${state} [${result.mode}] K8s: ${result.kubernetes.message} | Prometheus: ${result.prometheus.message}`
}

async function testDraftConnection() {
  formError.value = ''
  if (!form.k8s_api_url.trim()) {
    formError.value = 'K8s API URL is required before test.'
    return
  }

  draftTesting.value = true
  const signature = getDraftSignature()
  try {
    const result = await testClusterConnectionDraft(getDraftPayload())
    draftTestMessage.value = formatTestMessage(result)
    draftTestPassedSignature.value = result.ok ? signature : ''
  } catch (error: any) {
    draftTestPassedSignature.value = ''
    draftTestMessage.value = error?.response?.data?.detail || 'Connection test failed.'
  } finally {
    draftTesting.value = false
  }
}

async function testSavedConnection(id: number) {
  savedTestingId.value = id
  try {
    const result = await testClusterConnection(id)
    savedTestMessages.value = {
      ...savedTestMessages.value,
      [id]: formatTestMessage(result),
    }
  } catch (error: any) {
    savedTestMessages.value = {
      ...savedTestMessages.value,
      [id]: error?.response?.data?.detail || 'Connection test failed.',
    }
  } finally {
    savedTestingId.value = null
  }
}

function openDelete(id: number) {
  const row = getCluster(id)
  if (!row) return
  deleteModal.value.visible = true
  deleteModal.value.target = row
  deleteModal.value.submitting = false
}

function closeDeleteModal() {
  if (deleteModal.value.submitting) return
  deleteModal.value.visible = false
  deleteModal.value.target = null
}

async function confirmDelete() {
  const target = deleteModal.value.target
  if (!target) return
  deleteModal.value.submitting = true
  try {
    await deleteCluster(target.id)
    await loadClusters()
    closeDeleteModal()
  } finally {
    deleteModal.value.submitting = false
  }
}

function formatTime(ts: string) {
  return new Date(ts).toLocaleString()
}

onMounted(loadClusters)
</script>
