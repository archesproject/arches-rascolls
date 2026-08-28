import { useGettext } from "vue3-gettext";

import type {
    LandingBranding,
    LandingTab,
} from "@/arches_search/SearchLanding/types.ts";

export function useLandingContent(): {
    branding: LandingBranding;
    tabs: LandingTab[];
} {
    const { $gettext } = useGettext();

    return {
        branding: {
            eyebrow: $gettext("Getty Conservation Institute"),
            title: $gettext("Reference and Sample Collections"),
            subtitle: $gettext(
                "Search across %{total} resources — collection items, people, places, and more.",
            ),
            aboutIcon: "pi pi-info-circle",
            aboutHeading: $gettext("About the Collection"),
            aboutBody: [
                $gettext(
                    "The Arches Reference and Sample Collections (RASCOLL) is a digital catalogue of conservation science materials assembled at the Straus Center for Conservation and Technical Studies at Harvard Art Museums. The database brings together over 15,000 records documenting pigments, binding media, minerals, resins, and other physical reference specimens, alongside the people, institutions, archival texts, and geographic places associated with them.",
                ),
                $gettext(
                    "The collection has its roots in the early twentieth century, drawing heavily on the Forbes Collection — a foundational set of reference specimens donated by Edward Waldo Forbes and colleagues beginning in the 1910s and 1920s. Since then, the holdings have grown through gifts, field acquisitions, and systematic sampling programs, making RASCOLL one of the most comprehensive records of conservation reference materials in North America.",
                ),
                $gettext(
                    "Records are managed using the Arches Heritage Data Management Platform and linked across resource types — connecting a pigment sample to its mineral source, the conservator who catalogued it, the collection it belongs to, and the technical literature that describes it. Use the search tools above to explore by resource type, geographic location, or your saved queries.",
                ),
            ],
        },
        tabs: [
            {
                slug: "featured-items",
                label: $gettext("Featured Items"),
                icon: "pi pi-star",
                component: "arches_rascolls/SearchLanding/tabs/FeaturedItemsTab",
            },
            {
                slug: "resource-types",
                label: $gettext("Resource Types"),
                icon: "pi pi-sitemap",
                component: "arches_search/SearchLanding/tabs/ResourceTypesTab",
            },
            {
                slug: "map",
                label: $gettext("Map"),
                icon: "pi pi-map",
                component: "arches_search/SearchLanding/tabs/MapTab",
            },
            {
                slug: "saved-searches",
                label: $gettext("Saved Searches"),
                icon: "pi pi-bookmark-fill",
                component: "arches_search/SearchLanding/tabs/SavedSearchesTab",
            },
        ],
    };
}
