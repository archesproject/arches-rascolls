export const selectedLayerDefinition = [
    {
        id: "selected-resource-point-stroke",
        source: "selected-resource",
        type: "circle",
        filter: ["all", ["==", "$type", "Point"]],
        paint: {
            "circle-radius": 6,
            "circle-opacity": 1,
            "circle-color": "#f00",
        },
    },
    {
        id: "selected-resource-point",
        source: "selected-resource",
        type: "circle",
        filter: ["all", ["==", "$type", "Point"]],
        paint: {
            "circle-radius": 5,
            "circle-color": "#aaf",
        },
    },
    {
        id: "selected-resource-line",
        type: "line",
        paint: {
            "line-color": "#f00",
            "line-width": 5,
        },
        layout: {
            "line-cap": "round",
            "line-join": "round",
        },
        source: "selected-resource",
    },
    {
        id: "selected-resource-polygon-line",
        type: "line",
        paint: {
            "line-color": "#f00",
            "line-width": 5,
        },
        filter: ["==", "$type", "Polygon"],
        layout: {
            "line-cap": "round",
            "line-join": "round",
        },
        source: "selected-resource",
    },
    {
        id: "selected-resource-fill",
        type: "fill",
        paint: {
            "fill-color": "#f00",
            "fill-opacity": 0.1,
            "fill-outline-color": "#f00",
        },
        filter: ["==", "$type", "Polygon"],
        source: "selected-resource",
    },
];
