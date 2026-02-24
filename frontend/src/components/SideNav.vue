<template>
  <aside class="side-nav">
    <div class="brand">
      <div class="brand-mark">K</div>
      <span>KubeAICO</span>
    </div>
    <nav>
      <RouterLink v-for="item in items" :key="item.name" :to="item.to" class="nav-item">
        <span class="nav-icon-wrap" aria-hidden="true">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none">
            <path
              v-for="(path, idx) in iconPaths[item.icon]"
              :key="`${item.name}-${idx}`"
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
    </nav>
  </aside>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

const iconPaths = {
  overview: ['M4 4h7v7H4z', 'M13 4h7v4h-7z', 'M13 10h7v10h-7z', 'M4 13h7v7H4z'],
  workloads: ['M4 7l8-4 8 4-8 4-8-4z', 'M4 12l8 4 8-4', 'M4 17l8 4 8-4'],
  pods: [
    'M5 12a3 3 0 1 0 0.01 0',
    'M19 7a3 3 0 1 0 0.01 0',
    'M19 17a3 3 0 1 0 0.01 0',
    'M8 11l8-3',
    'M8 13l8 3',
  ],
  services: ['M12 3v6', 'M8 9h8', 'M6 9v6', 'M18 9v6', 'M6 15h12', 'M12 15v6'],
  alerts: ['M18 8a6 6 0 1 0-12 0c0 7-3 6-3 8h18c0-2-3-1-3-8', 'M10 20a2 2 0 0 0 4 0'],
  audit: ['M9 4h6', 'M8 7h8', 'M7 4H6a1 1 0 0 0-1 1v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V5a1 1 0 0 0-1-1h-1', 'M9 14l2 2 4-4'],
  ai: [
    'M12 3l1.6 3.7L17 8.3l-3.4 1.6L12 13.6l-1.6-3.7L7 8.3l3.4-1.6L12 3z',
    'M19 14l.9 2.1L22 17l-2.1.9L19 20l-.9-2.1L16 17l2.1-.9L19 14z',
    'M5 15l.8 1.8L7.6 18l-1.8.8L5 20.6l-.8-1.8L2.4 18l1.8-.8L5 15z',
  ],
} as const

type IconKey = keyof typeof iconPaths
type NavItem = {
  name: string
  label: string
  to: RouteLocationRaw
  icon: IconKey
}

const items: NavItem[] = [
  { name: 'overview', label: 'Overview', to: '/', icon: 'overview' },
  { name: 'workloads', label: 'Workloads', to: '/workloads', icon: 'workloads' },
  { name: 'pods', label: 'Pods', to: { path: '/workloads', query: { kind: 'pod' } }, icon: 'pods' },
  { name: 'services', label: 'Services', to: { path: '/workloads', query: { kind: 'service' } }, icon: 'services' },
  { name: 'alerts', label: 'Alerts', to: '/alerts', icon: 'alerts' },
  { name: 'audit', label: 'Audit', to: '/audit', icon: 'audit' },
  { name: 'ai', label: 'AI', to: '/ai', icon: 'ai' },
]
</script>
