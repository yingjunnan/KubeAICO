import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import AppShell from '../components/AppShell.vue';
import MetricCard from '../components/MetricCard.vue';
import TrendChart from '../components/TrendChart.vue';
import { getOverviewSummary, getTimeseries, getWsOverviewUrl } from '../services/api';
const summary = ref(null);
const cpuXAxis = ref([]);
const memXAxis = ref([]);
const cpuValues = ref([]);
const memValues = ref([]);
const filters = reactive({
    range: 60,
    namespace: '',
    env: 'prod',
});
let ws = null;
const nodeHealth = computed(() => {
    if (!summary.value)
        return '-';
    return `${summary.value.nodes_ready}/${summary.value.nodes_total}`;
});
const podHealth = computed(() => {
    if (!summary.value)
        return '-';
    return `${summary.value.pods_pending}/${summary.value.pods_crashloop}/${summary.value.pods_oomkilled}`;
});
const cpuUsage = computed(() => {
    if (!summary.value)
        return '-';
    return `${summary.value.cpu_usage_cores.toFixed(1)} / ${summary.value.cpu_capacity_cores.toFixed(1)} cores`;
});
const memoryUsage = computed(() => {
    if (!summary.value)
        return '-';
    const used = (summary.value.memory_usage_bytes / 1024 ** 3).toFixed(1);
    const total = (summary.value.memory_capacity_bytes / 1024 ** 3).toFixed(1);
    return `${used} / ${total} GiB`;
});
function toAxis(ts) {
    const d = new Date(ts * 1000);
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}
async function loadSummaryAndCharts() {
    const [summaryRes, cpu, mem] = await Promise.all([
        getOverviewSummary(),
        getTimeseries({ metric: 'cpu_usage', range_minutes: filters.range, namespace: filters.namespace || undefined }),
        getTimeseries({ metric: 'memory_usage', range_minutes: filters.range, namespace: filters.namespace || undefined }),
    ]);
    summary.value = summaryRes;
    const cpuPoints = cpu.series[0]?.points ?? [];
    cpuXAxis.value = cpuPoints.map((p) => toAxis(p.ts));
    cpuValues.value = cpuPoints.map((p) => Number(p.value.toFixed(3)));
    const memPoints = mem.series[0]?.points ?? [];
    memXAxis.value = memPoints.map((p) => toAxis(p.ts));
    memValues.value = memPoints.map((p) => Number((p.value / 1024 ** 3).toFixed(2)));
}
function connectWs() {
    const token = localStorage.getItem('kubeaico_token');
    if (!token)
        return;
    ws = new WebSocket(getWsOverviewUrl(token));
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        summary.value = data;
    };
}
async function updateFilters(next) {
    filters.range = next.range;
    filters.namespace = next.namespace ?? '';
    filters.env = next.env;
    await loadSummaryAndCharts();
}
onMounted(async () => {
    await loadSummaryAndCharts();
    connectWs();
});
onBeforeUnmount(() => {
    ws?.close();
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {[typeof AppShell, typeof AppShell, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AppShell, new AppShell({
    ...{ 'onFiltersChange': {} },
    title: "Cluster Overview",
    range: (__VLS_ctx.filters.range),
    namespace: (__VLS_ctx.filters.namespace),
}));
const __VLS_1 = __VLS_0({
    ...{ 'onFiltersChange': {} },
    title: "Cluster Overview",
    range: (__VLS_ctx.filters.range),
    namespace: (__VLS_ctx.filters.namespace),
}, ...__VLS_functionalComponentArgsRest(__VLS_0));
let __VLS_3;
let __VLS_4;
let __VLS_5;
const __VLS_6 = {
    onFiltersChange: (__VLS_ctx.updateFilters)
};
var __VLS_7 = {};
__VLS_2.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "hero card" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "hero-copy" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "eyebrow" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "hero-visual" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "bubble bubble-lg" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "bubble bubble-md" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "bubble bubble-sm" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "risk-pill" },
});
(__VLS_ctx.summary?.risk_score ?? '-');
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "stats-grid" },
});
/** @type {[typeof MetricCard, ]} */ ;
// @ts-ignore
const __VLS_8 = __VLS_asFunctionalComponent(MetricCard, new MetricCard({
    title: "Node Health",
    value: (__VLS_ctx.nodeHealth),
    subtitle: "Ready / Total",
}));
const __VLS_9 = __VLS_8({
    title: "Node Health",
    value: (__VLS_ctx.nodeHealth),
    subtitle: "Ready / Total",
}, ...__VLS_functionalComponentArgsRest(__VLS_8));
/** @type {[typeof MetricCard, ]} */ ;
// @ts-ignore
const __VLS_11 = __VLS_asFunctionalComponent(MetricCard, new MetricCard({
    title: "Pod Health",
    value: (__VLS_ctx.podHealth),
    subtitle: "Pending / CrashLoop / OOM",
}));
const __VLS_12 = __VLS_11({
    title: "Pod Health",
    value: (__VLS_ctx.podHealth),
    subtitle: "Pending / CrashLoop / OOM",
}, ...__VLS_functionalComponentArgsRest(__VLS_11));
/** @type {[typeof MetricCard, ]} */ ;
// @ts-ignore
const __VLS_14 = __VLS_asFunctionalComponent(MetricCard, new MetricCard({
    title: "CPU Usage",
    value: (__VLS_ctx.cpuUsage),
    subtitle: "Used / Capacity",
}));
const __VLS_15 = __VLS_14({
    title: "CPU Usage",
    value: (__VLS_ctx.cpuUsage),
    subtitle: "Used / Capacity",
}, ...__VLS_functionalComponentArgsRest(__VLS_14));
/** @type {[typeof MetricCard, ]} */ ;
// @ts-ignore
const __VLS_17 = __VLS_asFunctionalComponent(MetricCard, new MetricCard({
    title: "Memory Usage",
    value: (__VLS_ctx.memoryUsage),
    subtitle: "Used / Capacity",
}));
const __VLS_18 = __VLS_17({
    title: "Memory Usage",
    value: (__VLS_ctx.memoryUsage),
    subtitle: "Used / Capacity",
}, ...__VLS_functionalComponentArgsRest(__VLS_17));
/** @type {[typeof MetricCard, ]} */ ;
// @ts-ignore
const __VLS_20 = __VLS_asFunctionalComponent(MetricCard, new MetricCard({
    title: "Open Alerts",
    value: (String(__VLS_ctx.summary?.alerts_count ?? 0)),
    subtitle: "K8s + Prometheus",
}));
const __VLS_21 = __VLS_20({
    title: "Open Alerts",
    value: (String(__VLS_ctx.summary?.alerts_count ?? 0)),
    subtitle: "K8s + Prometheus",
}, ...__VLS_functionalComponentArgsRest(__VLS_20));
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "charts-grid" },
});
/** @type {[typeof TrendChart, ]} */ ;
// @ts-ignore
const __VLS_23 = __VLS_asFunctionalComponent(TrendChart, new TrendChart({
    title: "CPU Trend",
    subtitle: "cluster cpu usage",
    xAxis: (__VLS_ctx.cpuXAxis),
    values: (__VLS_ctx.cpuValues),
}));
const __VLS_24 = __VLS_23({
    title: "CPU Trend",
    subtitle: "cluster cpu usage",
    xAxis: (__VLS_ctx.cpuXAxis),
    values: (__VLS_ctx.cpuValues),
}, ...__VLS_functionalComponentArgsRest(__VLS_23));
/** @type {[typeof TrendChart, ]} */ ;
// @ts-ignore
const __VLS_26 = __VLS_asFunctionalComponent(TrendChart, new TrendChart({
    title: "Memory Trend",
    subtitle: "cluster memory usage",
    xAxis: (__VLS_ctx.memXAxis),
    values: (__VLS_ctx.memValues),
    color: "#69bfa0",
}));
const __VLS_27 = __VLS_26({
    title: "Memory Trend",
    subtitle: "cluster memory usage",
    xAxis: (__VLS_ctx.memXAxis),
    values: (__VLS_ctx.memValues),
    color: "#69bfa0",
}, ...__VLS_functionalComponentArgsRest(__VLS_26));
__VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
    ...{ class: "card ns-card" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
for (const [ns] of __VLS_getVForSourceType((__VLS_ctx.summary?.top_namespaces ?? []))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
        key: (ns.namespace),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (ns.namespace);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (ns.pod_count);
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['hero']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['hero-copy']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['hero-visual']} */ ;
/** @type {__VLS_StyleScopedClasses['bubble']} */ ;
/** @type {__VLS_StyleScopedClasses['bubble-lg']} */ ;
/** @type {__VLS_StyleScopedClasses['bubble']} */ ;
/** @type {__VLS_StyleScopedClasses['bubble-md']} */ ;
/** @type {__VLS_StyleScopedClasses['bubble']} */ ;
/** @type {__VLS_StyleScopedClasses['bubble-sm']} */ ;
/** @type {__VLS_StyleScopedClasses['risk-pill']} */ ;
/** @type {__VLS_StyleScopedClasses['stats-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['charts-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['ns-card']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            AppShell: AppShell,
            MetricCard: MetricCard,
            TrendChart: TrendChart,
            summary: summary,
            cpuXAxis: cpuXAxis,
            memXAxis: memXAxis,
            cpuValues: cpuValues,
            memValues: memValues,
            filters: filters,
            nodeHealth: nodeHealth,
            podHealth: podHealth,
            cpuUsage: cpuUsage,
            memoryUsage: memoryUsage,
            updateFilters: updateFilters,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
