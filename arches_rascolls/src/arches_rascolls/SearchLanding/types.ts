export interface FeaturedItem {
    id: string;
    label: string;
    description: string;
    icon: string | null;
    color: string | null;
    saved_search_name: string;
    search_definition: Record<string, unknown>;
}
