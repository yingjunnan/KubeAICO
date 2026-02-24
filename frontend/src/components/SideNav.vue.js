import { computed } from 'vue';
import { useRoute } from 'vue-router';
const route = useRoute();
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
};
const workloadChildren = [
    { kind: 'deployment', label: 'Deployment', icon: 'deployment' },
    { kind: 'statefulset', label: 'StatefulSet', icon: 'statefulset' },
    { kind: 'daemonset', label: 'DaemonSet', icon: 'daemonset' },
    { kind: 'pod', label: 'Pods', icon: 'pod' },
];
const serviceChildren = [
    { kind: 'service', label: 'Service', icon: 'service' },
    { kind: 'ingress', label: 'Ingress', icon: 'ingress' },
];
const workloadKinds = new Set(workloadChildren.map((item) => item.kind));
const serviceKinds = new Set(serviceChildren.map((item) => item.kind));
const currentKind = computed(() => String(route.query.kind ?? '').toLowerCase());
const isWorkloadsGroupActive = computed(() => route.path === '/workloads' &&
    (currentKind.value.length === 0 || workloadKinds.has(currentKind.value)));
const isServicesGroupActive = computed(() => route.path === '/workloads' && serviceKinds.has(currentKind.value));
function isKindActive(kind) {
    return route.path === '/workloads' && currentKind.value === kind;
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
const __VLS_ctx = {};
let __VLS_components;
let __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.aside, __VLS_intrinsicElements.aside)({
    ...{ class: "side-nav" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "brand" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "brand-mark" },
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.nav, __VLS_intrinsicElements.nav)({});
const __VLS_0 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
const __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({
    to: "/",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/' }) },
}));
const __VLS_2 = __VLS_1({
    to: "/",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/' }) },
}, ...__VLS_functionalComponentArgsRest(__VLS_1));
__VLS_3.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "nav-icon-wrap" },
    'aria-hidden': "true",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    ...{ class: "nav-icon" },
    viewBox: "0 0 24 24",
    fill: "none",
});
for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths.overview))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
        key: (`overview-${idx}`),
        d: (path),
        stroke: "currentColor",
        'stroke-width': "1.8",
        'stroke-linecap': "round",
        'stroke-linejoin': "round",
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_3;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "nav-group" },
});
const __VLS_4 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
const __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4({
    to: ({ path: '/workloads', query: { kind: 'deployment' } }),
    ...{ class: "nav-item nav-group-header" },
    ...{ class: ({ 'is-active': __VLS_ctx.isWorkloadsGroupActive }) },
}));
const __VLS_6 = __VLS_5({
    to: ({ path: '/workloads', query: { kind: 'deployment' } }),
    ...{ class: "nav-item nav-group-header" },
    ...{ class: ({ 'is-active': __VLS_ctx.isWorkloadsGroupActive }) },
}, ...__VLS_functionalComponentArgsRest(__VLS_5));
__VLS_7.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "nav-icon-wrap" },
    'aria-hidden': "true",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    ...{ class: "nav-icon" },
    viewBox: "0 0 24 24",
    fill: "none",
});
for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths.workloads))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
        key: (`workloads-${idx}`),
        d: (path),
        stroke: "currentColor",
        'stroke-width': "1.8",
        'stroke-linecap': "round",
        'stroke-linejoin': "round",
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_7;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "nav-submenu" },
});
for (const [item] of __VLS_getVForSourceType((__VLS_ctx.workloadChildren))) {
    const __VLS_8 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    const __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8({
        key: (item.kind),
        to: ({ path: '/workloads', query: { kind: item.kind } }),
        ...{ class: "nav-subitem" },
        ...{ class: ({ 'is-active': __VLS_ctx.isKindActive(item.kind) }) },
    }));
    const __VLS_10 = __VLS_9({
        key: (item.kind),
        to: ({ path: '/workloads', query: { kind: item.kind } }),
        ...{ class: "nav-subitem" },
        ...{ class: ({ 'is-active': __VLS_ctx.isKindActive(item.kind) }) },
    }, ...__VLS_functionalComponentArgsRest(__VLS_9));
    __VLS_11.slots.default;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "nav-sub-icon-wrap" },
        'aria-hidden': "true",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
        ...{ class: "nav-sub-icon" },
        viewBox: "0 0 24 24",
        fill: "none",
    });
    for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths[item.icon]))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
            key: (`${item.kind}-${idx}`),
            d: (path),
            stroke: "currentColor",
            'stroke-width': "1.8",
            'stroke-linecap': "round",
            'stroke-linejoin': "round",
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (item.label);
    var __VLS_11;
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    ...{ class: "nav-group" },
});
const __VLS_12 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
const __VLS_13 = __VLS_asFunctionalComponent(__VLS_12, new __VLS_12({
    to: ({ path: '/workloads', query: { kind: 'service' } }),
    ...{ class: "nav-item nav-group-header" },
    ...{ class: ({ 'is-active': __VLS_ctx.isServicesGroupActive }) },
}));
const __VLS_14 = __VLS_13({
    to: ({ path: '/workloads', query: { kind: 'service' } }),
    ...{ class: "nav-item nav-group-header" },
    ...{ class: ({ 'is-active': __VLS_ctx.isServicesGroupActive }) },
}, ...__VLS_functionalComponentArgsRest(__VLS_13));
__VLS_15.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "nav-icon-wrap" },
    'aria-hidden': "true",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    ...{ class: "nav-icon" },
    viewBox: "0 0 24 24",
    fill: "none",
});
for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths.services))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
        key: (`services-${idx}`),
        d: (path),
        stroke: "currentColor",
        'stroke-width': "1.8",
        'stroke-linecap': "round",
        'stroke-linejoin': "round",
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_15;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    ...{ class: "nav-submenu" },
});
for (const [item] of __VLS_getVForSourceType((__VLS_ctx.serviceChildren))) {
    const __VLS_16 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    const __VLS_17 = __VLS_asFunctionalComponent(__VLS_16, new __VLS_16({
        key: (item.kind),
        to: ({ path: '/workloads', query: { kind: item.kind } }),
        ...{ class: "nav-subitem" },
        ...{ class: ({ 'is-active': __VLS_ctx.isKindActive(item.kind) }) },
    }));
    const __VLS_18 = __VLS_17({
        key: (item.kind),
        to: ({ path: '/workloads', query: { kind: item.kind } }),
        ...{ class: "nav-subitem" },
        ...{ class: ({ 'is-active': __VLS_ctx.isKindActive(item.kind) }) },
    }, ...__VLS_functionalComponentArgsRest(__VLS_17));
    __VLS_19.slots.default;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
        ...{ class: "nav-sub-icon-wrap" },
        'aria-hidden': "true",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
        ...{ class: "nav-sub-icon" },
        viewBox: "0 0 24 24",
        fill: "none",
    });
    for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths[item.icon]))) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
            key: (`${item.kind}-${idx}`),
            d: (path),
            stroke: "currentColor",
            'stroke-width': "1.8",
            'stroke-linecap': "round",
            'stroke-linejoin': "round",
        });
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (item.label);
    var __VLS_19;
}
const __VLS_20 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
const __VLS_21 = __VLS_asFunctionalComponent(__VLS_20, new __VLS_20({
    to: "/alerts",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/alerts' }) },
}));
const __VLS_22 = __VLS_21({
    to: "/alerts",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/alerts' }) },
}, ...__VLS_functionalComponentArgsRest(__VLS_21));
__VLS_23.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "nav-icon-wrap" },
    'aria-hidden': "true",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    ...{ class: "nav-icon" },
    viewBox: "0 0 24 24",
    fill: "none",
});
for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths.alerts))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
        key: (`alerts-${idx}`),
        d: (path),
        stroke: "currentColor",
        'stroke-width': "1.8",
        'stroke-linecap': "round",
        'stroke-linejoin': "round",
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_23;
const __VLS_24 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
const __VLS_25 = __VLS_asFunctionalComponent(__VLS_24, new __VLS_24({
    to: "/audit",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/audit' }) },
}));
const __VLS_26 = __VLS_25({
    to: "/audit",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/audit' }) },
}, ...__VLS_functionalComponentArgsRest(__VLS_25));
__VLS_27.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "nav-icon-wrap" },
    'aria-hidden': "true",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    ...{ class: "nav-icon" },
    viewBox: "0 0 24 24",
    fill: "none",
});
for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths.audit))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
        key: (`audit-${idx}`),
        d: (path),
        stroke: "currentColor",
        'stroke-width': "1.8",
        'stroke-linecap': "round",
        'stroke-linejoin': "round",
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_27;
const __VLS_28 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
const __VLS_29 = __VLS_asFunctionalComponent(__VLS_28, new __VLS_28({
    to: "/ai",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/ai' }) },
}));
const __VLS_30 = __VLS_29({
    to: "/ai",
    ...{ class: "nav-item" },
    ...{ class: ({ 'is-active': __VLS_ctx.route.path === '/ai' }) },
}, ...__VLS_functionalComponentArgsRest(__VLS_29));
__VLS_31.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
    ...{ class: "nav-icon-wrap" },
    'aria-hidden': "true",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)({
    ...{ class: "nav-icon" },
    viewBox: "0 0 24 24",
    fill: "none",
});
for (const [path, idx] of __VLS_getVForSourceType((__VLS_ctx.iconPaths.ai))) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.path)({
        key: (`ai-${idx}`),
        d: (path),
        stroke: "currentColor",
        'stroke-width': "1.8",
        'stroke-linecap': "round",
        'stroke-linejoin': "round",
    });
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_31;
/** @type {__VLS_StyleScopedClasses['side-nav']} */ ;
/** @type {__VLS_StyleScopedClasses['brand']} */ ;
/** @type {__VLS_StyleScopedClasses['brand-mark']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-item']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-group']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-item']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-group-header']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-submenu']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-subitem']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-sub-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-sub-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-group']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-item']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-group-header']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-submenu']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-subitem']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-sub-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-sub-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-item']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-item']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-item']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon-wrap']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-icon']} */ ;
var __VLS_dollars;
const __VLS_self = (await import('vue')).defineComponent({
    setup() {
        return {
            route: route,
            iconPaths: iconPaths,
            workloadChildren: workloadChildren,
            serviceChildren: serviceChildren,
            isWorkloadsGroupActive: isWorkloadsGroupActive,
            isServicesGroupActive: isServicesGroupActive,
            isKindActive: isKindActive,
        };
    },
});
export default (await import('vue')).defineComponent({
    setup() {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
