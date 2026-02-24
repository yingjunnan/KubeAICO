<template>
  <aside class="side-nav">
    <div class="brand">
      <div class="brand-mark">K</div>
      <span>KubeAICO</span>
    </div>

    <nav>
      <RouterLink to="/" class="nav-item" :class="{ 'is-active': route.path === '/' }">
        <span class="nav-icon-wrap" aria-hidden="true">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none">
            <path
              v-for="(path, idx) in iconPaths.overview"
              :key="`overview-${idx}`"
              :d="path"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span>Overview</span>
      </RouterLink>

      <section class="nav-group">
        <button
          type="button"
          class="nav-item nav-group-header"
          :class="{ 'is-active': isWorkloadsGroupActive }"
          :aria-expanded="workloadsExpanded ? 'true' : 'false'"
          @click="toggleWorkloads"
        >
          <span class="nav-group-label">
            <span class="nav-icon-wrap" aria-hidden="true">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none">
                <path
                  v-for="(path, idx) in iconPaths.workloads"
                  :key="`workloads-${idx}`"
                  :d="path"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <span>Workloads</span>
          </span>
          <span class="nav-group-toggle" :class="{ expanded: workloadsExpanded }" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
        </button>

        <Transition name="nav-collapse">
        <div v-show="workloadsExpanded" class="nav-submenu">
          <RouterLink
            v-for="item in workloadChildren"
            :key="item.kind"
            :to="{ path: '/workloads', query: { kind: item.kind } }"
            class="nav-subitem"
            :class="{ 'is-active': isKindActive(item.kind) }"
          >
            <span class="nav-sub-icon-wrap" aria-hidden="true">
              <svg class="nav-sub-icon" viewBox="0 0 24 24" fill="none">
                <path
                  v-for="(path, idx) in iconPaths[item.icon]"
                  :key="`${item.kind}-${idx}`"
                  :d="path"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <span>{{ item.label }}</span>
          </RouterLink>
        </div>
        </Transition>
      </section>

      <section class="nav-group">
        <button
          type="button"
          class="nav-item nav-group-header"
          :class="{ 'is-active': isServicesGroupActive }"
          :aria-expanded="servicesExpanded ? 'true' : 'false'"
          @click="toggleServices"
        >
          <span class="nav-group-label">
            <span class="nav-icon-wrap" aria-hidden="true">
              <svg class="nav-icon" viewBox="0 0 24 24" fill="none">
                <path
                  v-for="(path, idx) in iconPaths.services"
                  :key="`services-${idx}`"
                  :d="path"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <span>Services</span>
          </span>
          <span class="nav-group-toggle" :class="{ expanded: servicesExpanded }" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M9 6l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
        </button>

        <Transition name="nav-collapse">
        <div v-show="servicesExpanded" class="nav-submenu">
          <RouterLink
            v-for="item in serviceChildren"
            :key="item.kind"
            :to="{ path: '/workloads', query: { kind: item.kind } }"
            class="nav-subitem"
            :class="{ 'is-active': isKindActive(item.kind) }"
          >
            <span class="nav-sub-icon-wrap" aria-hidden="true">
              <svg class="nav-sub-icon" viewBox="0 0 24 24" fill="none">
                <path
                  v-for="(path, idx) in iconPaths[item.icon]"
                  :key="`${item.kind}-${idx}`"
                  :d="path"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </span>
            <span>{{ item.label }}</span>
          </RouterLink>
        </div>
        </Transition>
      </section>

      <RouterLink to="/alerts" class="nav-item" :class="{ 'is-active': route.path === '/alerts' }">
        <span class="nav-icon-wrap" aria-hidden="true">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none">
            <path
              v-for="(path, idx) in iconPaths.alerts"
              :key="`alerts-${idx}`"
              :d="path"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span>Alerts</span>
      </RouterLink>

      <RouterLink to="/audit" class="nav-item" :class="{ 'is-active': route.path === '/audit' }">
        <span class="nav-icon-wrap" aria-hidden="true">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none">
            <path
              v-for="(path, idx) in iconPaths.audit"
              :key="`audit-${idx}`"
              :d="path"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span>Audit</span>
      </RouterLink>

      <RouterLink to="/ai" class="nav-item" :class="{ 'is-active': route.path === '/ai' }">
        <span class="nav-icon-wrap" aria-hidden="true">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none">
            <path
              v-for="(path, idx) in iconPaths.ai"
              :key="`ai-${idx}`"
              :d="path"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span>AI</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const iconPaths = {
  overview: ['M4 4h7v7H4z', 'M13 4h7v4h-7z', 'M13 10h7v10h-7z', 'M4 13h7v7H4z'],
  workloads: ['M4 7l8-4 8 4-8 4-8-4z', 'M4 12l8 4 8-4', 'M4 17l8 4 8-4'],
  deployment: ['M4 7l8-4 8 4-8 4-8-4z', 'M4 12l8 4 8-4', 'M4 17l8 4 8-4'],
  statefulset: ['M6 4h12v16H6z', 'M9 8h6', 'M9 12h6', 'M9 16h6'],
  daemonset: ['M12 3v4', 'M12 17v4', 'M3 12h4', 'M17 12h4', 'M6.5 6.5l2.8 2.8', 'M14.7 14.7l2.8 2.8', 'M17.5 6.5l-2.8 2.8', 'M9.3 14.7l-2.8 2.8', 'M12 15a3 3 0 1 0 0.01 0'],
  pod: ['M12 3l6 4v10l-6 4-6-4V7l6-4z', 'M12 7v10', 'M6 9l6 4 6-4'],
  services: ['M12 3v6', 'M8 9h8', 'M6 9v6', 'M18 9v6', 'M6 15h12', 'M12 15v6'],
  service: ['M12 3v6', 'M8 9h8', 'M6 9v6', 'M18 9v6', 'M6 15h12', 'M12 15v6'],
  ingress: ['M4 8h16', 'M7 8V5h10v3', 'M12 8v11', 'M9 16l3 3 3-3'],
  alerts: ['M18 8a6 6 0 1 0-12 0c0 7-3 6-3 8h18c0-2-3-1-3-8', 'M10 20a2 2 0 0 0 4 0'],
  audit: ['M9 4h6', 'M8 7h8', 'M7 4H6a1 1 0 0 0-1 1v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V5a1 1 0 0 0-1-1h-1', 'M9 14l2 2 4-4'],
  ai: [
    'M12 3l1.6 3.7L17 8.3l-3.4 1.6L12 13.6l-1.6-3.7L7 8.3l3.4-1.6L12 3z',
    'M19 14l.9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14z',
    'M5 15l.8 1.8L7.6 18l-1.8.8L5 20.6l-.8-1.8L2.4 18l1.8-.8L5 15z',
  ],
} as const

type SubNavItem = {
  kind: string
  label: string
  icon: keyof typeof iconPaths
}

const workloadChildren: SubNavItem[] = [
  { kind: 'deployment', label: 'Deployment', icon: 'deployment' },
  { kind: 'statefulset', label: 'StatefulSet', icon: 'statefulset' },
  { kind: 'daemonset', label: 'DaemonSet', icon: 'daemonset' },
  { kind: 'pod', label: 'Pods', icon: 'pod' },
]

const serviceChildren: SubNavItem[] = [
  { kind: 'service', label: 'Service', icon: 'service' },
  { kind: 'ingress', label: 'Ingress', icon: 'ingress' },
]

const workloadKinds = new Set(workloadChildren.map((item) => item.kind))
const serviceKinds = new Set(serviceChildren.map((item) => item.kind))

const currentKind = computed(() => String(route.query.kind ?? '').toLowerCase())

const isWorkloadsGroupActive = computed(
  () =>
    route.path === '/workloads' &&
    (currentKind.value.length === 0 || workloadKinds.has(currentKind.value)),
)

const isServicesGroupActive = computed(
  () => route.path === '/workloads' && serviceKinds.has(currentKind.value),
)

const workloadsExpanded = ref(true)
const servicesExpanded = ref(true)

watch([isWorkloadsGroupActive, isServicesGroupActive], ([workloadsActive, servicesActive]) => {
  if (workloadsActive) workloadsExpanded.value = true
  if (servicesActive) servicesExpanded.value = true
}, { immediate: true })

function isKindActive(kind: string): boolean {
  return route.path === '/workloads' && currentKind.value === kind
}

function toggleWorkloads(): void {
  workloadsExpanded.value = !workloadsExpanded.value
}

function toggleServices(): void {
  servicesExpanded.value = !servicesExpanded.value
}
</script>
