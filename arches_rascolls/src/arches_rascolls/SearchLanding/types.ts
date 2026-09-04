export interface FeaturedItem {
    id: string;
    label: string;
    description: string;
    icon: string | null;
    color: string | null;
    search_definition: Record<string, unknown>;
}
