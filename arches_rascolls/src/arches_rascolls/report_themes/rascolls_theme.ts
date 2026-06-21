import { definePreset } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

import { compileGlobalCss } from "@/arches_modular_reports/utils.ts";

// The comps render at the browser-default 16px root font; arches sets
// html { font-size: 10px }, so the comps' rem values are restated here
// at 10px-root scale, scoped to the report mounting point.
const cssOverrides = {
    ".modular-report-mounting-point": {
        "font-family":
            '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif',
    },
    // comp: .data-table td { font-size: 0.85rem; color: #101828 }
    ".modular-report-mounting-point .p-datatable-tbody > tr > td": {
        "font-size": "1.36rem",
    },
    // comp: .data-table th { font-size: 0.68rem; uppercase; 0.05em; #475467;
    // background: #fafbfc } — background forced here because arches core
    // table styles outrank the datatable headerCell token
    ".modular-report-mounting-point .p-datatable-thead > tr > th": {
        "font-size": "1.1rem",
        "font-weight": "600",
        "text-transform": "uppercase",
        "letter-spacing": "0.05em",
        color: "var(--p-text-muted-color, #475467)",
        background: "#fafbfc !important",
    },
    // lifecycle chip and other tags read correctly at 10px root
    ".modular-report-mounting-point .p-tag": {
        "font-size": "1.2rem",
        padding: "0.35rem 0.9rem",
    },
    // comp: .section-card .p-button { font-size: 0.8rem }
    ".modular-report-mounting-point .p-button": {
        "font-size": "1.28rem",
    },
};

// Teal palette matching the RaSColls report comps (primary #0d9488 = teal-600).
const RascollsReportPreset = definePreset(Aura, {
    semantic: {
        primary: {
            50: "{teal.50}",
            100: "{teal.100}",
            200: "{teal.200}",
            300: "{teal.300}",
            400: "{teal.400}",
            500: "{teal.500}",
            600: "{teal.600}",
            700: "{teal.700}",
            800: "{teal.800}",
            900: "{teal.900}",
            950: "{teal.950}",
        },
        colorScheme: {
            light: {
                primary: {
                    color: "{teal.600}",
                    inverseColor: "#ffffff",
                    hoverColor: "{teal.800}",
                    activeColor: "{teal.700}",
                },
                highlight: {
                    background: "{teal.600}",
                    focusBackground: "{teal.700}",
                    color: "#ffffff",
                    focusColor: "#ffffff",
                },
            },
            dark: {
                primary: {
                    color: "{teal.300}",
                    inverseColor: "{teal.950}",
                    hoverColor: "{teal.100}",
                    activeColor: "{teal.200}",
                },
                highlight: {
                    background: "rgba(250, 250, 250, .16)",
                    focusBackground: "rgba(250, 250, 250, .24)",
                    color: "rgba(255,255,255,.87)",
                    focusColor: "rgba(255,255,255,.87)",
                },
            },
        },
    },
    components: {
        datatable: {
            rowToggleButton: {
                size: "2.5rem",
            },
            colorScheme: {
                light: {
                    headerCell: {
                        // comp: .data-table th background: #fafbfc (--empty-bg)
                        background: "#fafbfc",
                        hoverBackground: "{surface-100}",
                    },
                },
            },
        },
    },
    css: compileGlobalCss(cssOverrides),
});

export default {
    theme: {
        preset: RascollsReportPreset,
        options: {
            prefix: "p",
            darkModeSelector: ".arches-dark",
            cssLayer: false,
        },
    },
};
