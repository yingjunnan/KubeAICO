import { onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AppShell from '../components/AppShell.vue';
import { getResourceDetail, getResources, rolloutRestart, scaleResource } from '../services/api';
const route = useRoute();
const router = useRouter();
const validKinds = ['deployment', 'statefulset', 'daemonset', 'pod', 'service', 'ingress'];
const scalableKinds = new Set(['deployment', 'statefulset', 'daemonset']);
const kind = ref('deployment');
const namespace = ref('');
const statusFilter = ref('');
const labelSelector = ref('');
const resources = ref([]);
const detail = ref(null);
const scaleReplicas = ref(1);
const operationModal = ref({
    visible: false,
    type: 'scale',
    target: null,
    error: '',
    submitting: false,
});
async function loadResources() {
    const response = await getResources({
        kind: kind.value,
        namespace: namespace.value || undefined,
        status: statusFilter.value || undefined,
        label_selector: labelSelector.value || undefined,
    });
    resources.value = response.items;
}
async function syncKindFromRoute(nextKindRaw) {
    const nextKind = String(nextKindRaw || '').toLowerCase();
    if (!validKinds.includes(nextKind)) {
        kind.value = 'deployment';
        await router.replace({ path: '/workloads', query: { kind: 'deployment' } });
        return;
    }
    kind.value = nextKind;
}
function openScale(name, targetNamespace, currentReplica) {
    scaleReplicas.value = currentReplica;
    operationModal.value = {
        visible: true,
        type: 'scale',
        target: { name, namespace: targetNamespace },
        error: '',
        submitting: false,
    };
}
function restart(name, targetNamespace) {
    operationModal.value = {
        visible: true,
        type: 'restart',
        target: { name, namespace: targetNamespace },
        error: '',
        submitting: false,
    };
}
function closeOperationModal() {
    if (operationModal.value.submitting)
        return;
    operationModal.value.visible = false;
    operationModal.value.error = '';
}
async function submitOperation() {
    const target = operationModal.value.target;
    if (!target)
        return;
    operationModal.value.error = '';
    operationModal.value.submitting = true;
    try {
        if (operationModal.value.type === 'scale') {
            if (!Number.isInteger(scaleReplicas.value) || scaleReplicas.value < 0 || scaleReplicas.value > 1000) {
                operationModal.value.error = 'Replicas must be an integer between 0 and 1000.';
                return;
            }
            await scaleResource({
                kind: kind.value,
                name: target.name,
                namespace: target.namespace,
                replicas: scaleReplicas.value,
            });
        }
        else {
            await rolloutRestart({
                kind: kind.value,
                name: target.name,
                namespace: target.namespace,
            });
        }
        operationModal.value.visible = false;
        await loadResources();
    }
    catch (error) {
        operationModal.value.error = 'Operation failed. Please retry.';
    }
    finally {
        operationModal.value.submitting = false;
    }
}
async function openDetail(name, targetNamespace) {
    detail.value = await getResourceDetail({
        kind: kind.value,
        name,
        namespace: targetNamespace,
        log_lines: 120,
    });
}
async function onFilters(payload) {
    namespace.value = payload.namespace || '';
    await loadResources();
}
onMounted(async () => {
    await syncKindFromRoute(route.query.kind);
    await loadResources();
});
watch(() => route.query.kind, async (nextKind) => {
    await syncKindFromRoute(nextKind);
    await loadResources();
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
/** @type {[typeof AppShell, typeof AppShell, ]} */ ;
// @ts-ignore
const __VLS_0 = __VLS_asFunctionalComponent(AppShell, new AppShell({
    ...{ 'onFiltersChange': {} },
    title: "Resource Management",
}));
const __VLS_1 = __VLS_0({
    ...{ 'onFiltersChange': {} },
    title: "Resource Management",
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
    ...{ class: "card toolbar" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "toolbar-title" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
    ...{ class: "eyebrow" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
(__VLS_ctx.kind);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "query-fields" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    ...{ onKeyup: (__VLS_ctx.loadResources) },
    placeholder: "namespace",
});
(__VLS_ctx.namespace);
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    ...{ onKeyup: (__VLS_ctx.loadResources) },
    placeholder: "status",
});
(__VLS_ctx.statusFilter);
__VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
    ...{ onKeyup: (__VLS_ctx.loadResources) },
    placeholder: "label app=xxx",
});
(__VLS_ctx.labelSelector);
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
    ...{ onClick: (__VLS_ctx.loadResources) },
    ...{ class: "primary-btn" },
    type: "button",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "card" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.table, __VLS_intrinsicElements.table)({
    ...{ class: "resource-table" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.thead, __VLS_intrinsicElements.thead)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.tbody, __VLS_intrinsicElements.tbody)({});
for (const [item] of __VLS_getVForSourceType((__VLS_ctx.resources))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({
        key: (`${item.namespace}-${item.name}`),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
    (item.name);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
    (item.namespace);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
    (item.status);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
    (item.replicas ?? '-');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
    (item.available_replicas ?? '-');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
    (item.restarts);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "action-row" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                __VLS_ctx.openDetail(item.name, item.namespace);
            } },
        type: "button",
    });
    if (__VLS_ctx.scalableKinds.has(__VLS_ctx.kind)) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.scalableKinds.has(__VLS_ctx.kind)))
                        return;
                    __VLS_ctx.openScale(item.name, item.namespace, item.replicas ?? 1);
                } },
            type: "button",
        });
    }
    if (__VLS_ctx.scalableKinds.has(__VLS_ctx.kind)) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
            ...{ onClick: (...[$event]) => {
                    if (!(__VLS_ctx.scalableKinds.has(__VLS_ctx.kind)))
                        return;
                    __VLS_ctx.restart(item.name, item.namespace);
                } },
            type: "button",
        });
    }
}
if (__VLS_ctx.detail) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "card detail-panel" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "detail-header" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    (__VLS_ctx.detail.item.kind);
    (__VLS_ctx.detail.item.name);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (...[$event]) => {
                if (!(__VLS_ctx.detail))
                    return;
                __VLS_ctx.detail = null;
            } },
        type: "button",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
        ...{ class: "hint" },
    });
    (__VLS_ctx.detail.item.namespace);
    (__VLS_ctx.detail.item.status);
    (__VLS_ctx.detail.item.restarts);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "detail-grid" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
    for (const [event, idx] of __VLS_getVForSourceType((__VLS_ctx.detail.events))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            key: (`${event.reason}-${idx}`),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (event.type);
        (event.reason);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (event.message);
    }
    if (__VLS_ctx.detail.events.length === 0) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            ...{ class: "hint" },
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h4, __VLS_intrinsicElements.h4)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.pre, __VLS_intrinsicElements.pre)({});
    (__VLS_ctx.detail.logs.join('\n') || 'No logs available.');
}
const __VLS_8 = {}.Teleport;
/** @type {[typeof __VLS_components.Teleport, typeof __VLS_components.Teleport, ]} */ ;
// @ts-ignore
const __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8({
    to: "body",
}));
const __VLS_10 = __VLS_9({
    to: "body",
}, ...__VLS_functionalComponentArgsRest(__VLS_9));
__VLS_11.slots.default;
if (__VLS_ctx.operationModal.visible) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ onClick: (__VLS_ctx.closeOperationModal) },
        ...{ class: "theme-modal-backdrop" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
        ...{ class: "theme-modal" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)({
        ...{ class: "theme-modal-header" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    (__VLS_ctx.operationModal.type === 'scale' ? 'Scale Workload' : 'Rollout Restart');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.closeOperationModal) },
        type: "button",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
        ...{ class: "theme-modal-body" },
    });
    if (__VLS_ctx.operationModal.target) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (__VLS_ctx.kind);
        (__VLS_ctx.operationModal.target.name);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (__VLS_ctx.operationModal.target.namespace);
    }
    if (__VLS_ctx.operationModal.type === 'scale') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
            ...{ class: "theme-modal-field" },
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            type: "number",
            min: "0",
            max: "1000",
            step: "1",
        });
        (__VLS_ctx.scaleReplicas);
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
            ...{ class: "hint" },
        });
    }
    if (__VLS_ctx.operationModal.error) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
            ...{ class: "error-text" },
        });
        (__VLS_ctx.operationModal.error);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.footer, __VLS_intrinsicElements.footer)({
        ...{ class: "theme-modal-actions" },
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.closeOperationModal) },
        type: "button",
        disabled: (__VLS_ctx.operationModal.submitting),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)({
        ...{ onClick: (__VLS_ctx.submitOperation) },
        ...{ class: "primary-btn" },
        type: "button",
        disabled: (__VLS_ctx.operationModal.submitting),
    });
    (__VLS_ctx.operationModal.submitting
        ? 'Submitting...'
        : __VLS_ctx.operationModal.type === 'scale'
            ? 'Apply Scale'
            : 'Confirm Restart');
}
var __VLS_11;
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['toolbar']} */ ;
/** @type {__VLS_StyleScopedClasses['toolbar-title']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['query-fields']} */ ;
/** @type {__VLS_StyleScopedClasses['primary-btn']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['resource-table']} */ ;
/** @type {__VLS_StyleScopedClasses['action-row']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-header']} */ ;
/** @type {__VLS_StyleScopedClasses['hint']} */ ;
/** @type {__VLS_StyleScopedClasses['detail-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['hint']} */ ;
/** @type {__VLS_StyleScopedClasses['theme-modal-backdrop']} */ ;
/** @type {__VLS_StyleScopedClasses['theme-modal']} */ ;
/** @type {__VLS_StyleScopedClasses['theme-modal-header']} */ ;
/** @type {__VLS_StyleScopedClasses['theme-modal-body']} */ ;
/** @type {__VLS_StyleScopedClasses['theme-modal-field']} */ ;
/** @type {__VLS_StyleScopedClasses['hint']} */ ;
/** @type {__VLS_StyleScopedClasses['error-text']} */ ;
/** @type {__VLS_StyleScopedClasses['theme-modal-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['primary-btn']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            AppShell: AppShell,
            scalableKinds: scalableKinds,
            kind: kind,
            namespace: namespace,
            statusFilter: statusFilter,
            labelSelector: labelSelector,
            resources: resources,
            detail: detail,
            scaleReplicas: scaleReplicas,
            operationModal: operationModal,
            loadResources: loadResources,
            openScale: openScale,
            restart: restart,
            closeOperationModal: closeOperationModal,
            submitOperation: submitOperation,
            openDetail: openDetail,
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
