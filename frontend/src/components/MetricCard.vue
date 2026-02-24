<template>
  <article class="metric-card card">
    <p class="metric-title">{{ title }}</p>
    <p class="metric-value">{{ value }}</p>
    <p class="metric-sub">{{ subtitle }}</p>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  value: string
  subtitle?: string
}>()
</script>
