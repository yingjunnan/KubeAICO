<template>
  <article class="chart-card card">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <p>{{ subtitle }}</p>
    </div>
    <div ref="chartEl" class="chart-body" />
  </article>
</template>

<script setup lang="ts">
import type { ECharts } from 'echarts'
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  title: string
  subtitle: string
  xAxis: string[]
  values: number[]
  color?: string
}>()

const chartEl = ref<HTMLElement | null>(null)
let chart: ECharts | null = null

function render() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 12, right: 12, top: 12, bottom: 20, containLabel: true },
    xAxis: {
      type: 'category',
      data: props.xAxis,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#6B7280', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#E5E7EB' } },
      axisLabel: { color: '#9CA3AF', fontSize: 10 },
    },
    series: [
      {
        data: props.values,
        type: 'line',
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2, color: props.color ?? '#8FD3B6' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(143,211,182,0.35)' },
              { offset: 1, color: 'rgba(143,211,182,0.02)' },
            ],
          },
        },
      },
    ],
  })
}

onMounted(() => {
  render()
  window.addEventListener('resize', render)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', render)
  chart?.dispose()
})

watch(
  () => [props.xAxis, props.values],
  () => {
    render()
  },
)
</script>
