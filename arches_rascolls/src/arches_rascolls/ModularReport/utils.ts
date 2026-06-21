interface FieldGroupConfig {
    nodegroup_alias: string;
    custom_card_name?: string | null;
}

export function fieldGroupAnchorId(config: FieldGroupConfig): string {
    const name = config.custom_card_name ?? config.nodegroup_alias;
    return (
        "fg-" +
        `${config.nodegroup_alias}-${name}`
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
    );
}
