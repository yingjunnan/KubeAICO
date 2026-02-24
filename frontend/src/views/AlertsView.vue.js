import { onMounted, ref } from 'vue';
import AppShell from '../components/AppShell.vue';
import { getAlerts } from '../services/api';
const alerts = ref([]);
const namespace = ref('');
async function loadAlerts() {
    const response = await getAlerts({ namespace: namespace.value || undefined, limit: 50 });
    alerts.value = response.items;
}
function onFilters(payload) {
    namespace.value = payload.namespace || '';
    void loadAlerts();
}
function formatTime(ts) {
    const date = new Date(ts);
    return date.toLocaleString();
}
onMounted(loadAlerts);
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {[typeof AppShell, typeof AppShell, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AppShell, new AppShell({
    ...{ 'onFiltersChange': {} },
    title: "Alerts & Fault Events",
}));
const __VLS_1 = __VLS_0({
    ...{ 'onFiltersChange': {} },
    title: "Alerts & Fault Events",
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
    ...{ class: "alerts-grid" },
});
for (const [item] of __VLS_getVForSourceType((__VLS_ctx.alerts))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({
        key: (item.id),
        ...{ class: "card alert-card" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "alert-head" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: (['badge', item.severity.toLowerCase()]) },
    });
    (item.severity);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "source" },
    });
    (item.source);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.time, __VLS_intrinsicElements.time)({});
    (__VLS_ctx.formatTime(item.start_time));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    (item.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    (item.message);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "recommendation" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (item.recommendation);
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['alerts-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['alert-card']} */ ;
/** @type {__VLS_StyleScopedClasses['alert-head']} */ ;
/** @type {__VLS_StyleScopedClasses['source']} */ ;
/** @type {__VLS_StyleScopedClasses['recommendation']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            AppShell: AppShell,
            alerts: alerts,
            onFilters: onFilters,
            formatTime: formatTime,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
