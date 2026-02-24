import * as echarts from 'echarts';
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
const props = defineProps();
const chartEl = ref(null);
let chart = null;
function render() {
    if (!chartEl.value)
        return;
    if (!chart)
        chart = echarts.init(chartEl.value);
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
    });
}
onMounted(() => {
    render();
    window.addEventListener('resize', render);
});
onBeforeUnmount(() => {
    window.removeEventListener('resize', render);
    chart?.dispose();
});
watch(() => [props.xAxis, props.values], () => {
    render();
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
    ...{ class: "chart-card card" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "chart-header" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
(__VLS_ctx.title);
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
(__VLS_ctx.subtitle);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div)({
    ref: "chartEl",
    ...{ class: "chart-body" },
});
/** @type {typeof __VLS_ctx.chartEl} */ ;
/** @type {__VLS_StyleScopedClasses['chart-card']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['chart-header']} */ ;
/** @type {__VLS_StyleScopedClasses['chart-body']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            chartEl: chartEl,
        };
    },
    __typeProps: {},
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
