import { ref } from 'vue';
import AppShell from '../components/AppShell.vue';
import { createAnalyzeTask, getAnalyzeTask } from '../services/api';
const namespace = ref('default');
const workload = ref('');
const cpu = ref(65);
const memory = ref(72);
const restartRate = ref(0.02);
const errorRate = ref(0.01);
const loading = ref(false);
const taskStatus = ref('');
const result = ref(null);
let pollTimer = null;
function clearPoll() {
    if (pollTimer) {
        window.clearInterval(pollTimer);
        pollTimer = null;
    }
}
async function runAnalyze() {
    loading.value = true;
    result.value = null;
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
        });
        taskStatus.value = task.status;
        clearPoll();
        pollTimer = window.setInterval(async () => {
            const latest = await getAnalyzeTask(task.task_id);
            taskStatus.value = latest.status;
            if (latest.status === 'completed') {
                result.value = latest.result ?? null;
                loading.value = false;
                clearPoll();
            }
            if (latest.status === 'failed') {
                loading.value = false;
                clearPoll();
            }
        }, 1500);
    }
    catch {
        loading.value = false;
        clearPoll();
    }
}
function onFilters(payload) {
    namespace.value = payload.namespace || namespace.value;
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {[typeof AppShell, typeof AppShell, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AppShell, new AppShell({
    ...{ 'onFiltersChange': {} },
    title: "AI Analysis",
}));
const __VLS_1 = __VLS_0({
    ...{ 'onFiltersChange': {} },
    title: "AI Analysis",
}, ...__VLS_functionalComponentArgsRest(__VLS_0));
let __VLS_3;
let __VLS_4;
let __VLS_5;
const __VLS_6 = {
    onFiltersChange: (__VLS_ctx.onFilters)
};
var __VLS_7 = {};
__VLS_2.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "ai-layout" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
    ...{ class: "card ai-form" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    placeholder: "default",
});
(__VLS_ctx.namespace);
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    placeholder: "api",
});
(__VLS_ctx.workload);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "metric-inputs" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    type: "number",
    min: "0",
    max: "100",
});
(__VLS_ctx.cpu);
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    type: "number",
    min: "0",
    max: "100",
});
(__VLS_ctx.memory);
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    type: "number",
    min: "0",
    step: "0.01",
});
(__VLS_ctx.restartRate);
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    type: "number",
    min: "0",
    step: "0.01",
});
(__VLS_ctx.errorRate);
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (__VLS_ctx.runAnalyze) },
    ...{ class: "primary-btn" },
    disabled: (__VLS_ctx.loading),
});
(__VLS_ctx.loading ? 'Analyzing...' : 'Start Analysis');
if (__VLS_ctx.taskStatus) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "hint" },
    });
    (__VLS_ctx.taskStatus);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
    ...{ class: "card ai-result" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
if (__VLS_ctx.result) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "result-summary" },
    });
    (__VLS_ctx.result.summary);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.result.risk_level);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
    for (const [cause, idx] of __VLS_getVForSourceType((__VLS_ctx.result.root_causes))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            key: (idx),
        });
        (cause.cause);
        (Math.round(cause.confidence * 100));
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
    for (const [item, idx] of __VLS_getVForSourceType((__VLS_ctx.result.recommendations))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            key: (idx),
        });
        (item);
    }
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "hint" },
    });
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['ai-layout']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-form']} */ ;
/** @type {__VLS_StyleScopedClasses['metric-inputs']} */ ;
/** @type {__VLS_StyleScopedClasses['primary-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['hint']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['ai-result']} */ ;
/** @type {__VLS_StyleScopedClasses['result-summary']} */ ;
/** @type {__VLS_StyleScopedClasses['hint']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            AppShell: AppShell,
            namespace: namespace,
            workload: workload,
            cpu: cpu,
            memory: memory,
            restartRate: restartRate,
            errorRate: errorRate,
            loading: loading,
            taskStatus: taskStatus,
            result: result,
            runAnalyze: runAnalyze,
            onFilters: onFilters,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
