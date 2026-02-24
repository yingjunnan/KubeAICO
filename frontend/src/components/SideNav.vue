<template>
  <aside class="side-nav">
    <div class="brand">
      <div class="brand-mark">K</div>
      <span>KubeAICO</span>
    </div>
    <nav>
      <RouterLink v-for="item in items" :key="item.name" :to="item.to" class="nav-item">
        <span class="icon">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<script setup lang="ts">
const items = [
  { name: 'overview', label: 'Overview', to: '/', icon: 'OV' },
  { name: 'workloads', label: 'Workloads', to: '/workloads', icon: 'WL' },
  { name: 'pods', label: 'Pods', to: { path: '/workloads', query: { kind: 'pod' } }, icon: 'PD' },
  { name: 'services', label: 'Services', to: { path: '/workloads', query: { kind: 'service' } }, icon: 'SV' },
  { name: 'alerts', label: 'Alerts', to: '/alerts', icon: 'AL' },
  { name: 'audit', label: 'Audit', to: '/audit', icon: 'AU' },
  { name: 'ai', label: 'AI', to: '/ai', icon: 'AI' },
]
</script>
