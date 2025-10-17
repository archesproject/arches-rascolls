import arches from "arches";
import Cookies from "js-cookie";

import type { FeatureCollection } from "geojson";

function getToken() {
    const token = Cookies.get("csrftoken");
    if (!token) {
        throw new Error("Missing csrftoken");
    }
    return token;
}

export const fetchGeoJSONBounds = async (features: FeatureCollection) => {
    const response = await fetch(arches.urls["api-geojson-bounds"], {
        method: "POST",
        headers: { "X-CSRFTOKEN": getToken() },
        body: JSON.stringify(features),
    });
    try {
        const responseJson = await response.json();
        if (response.ok) {
            return responseJson;
        }
        throw new Error(responseJson.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const fetchDrawnFeaturesBuffer = async (features: FeatureCollection) => {
    const response = await fetch(arches.urls["api-feature-buffer"], {
        method: "POST",
        headers: { "X-CSRFTOKEN": getToken() },
        body: JSON.stringify({ features }),
    });
    try {
        const responseJson = await response.json();
        if (response.ok) {
            return responseJson;
        }
        throw new Error(responseJson.message);
    } catch (error) {
        throw new Error((error as Error).message || response.statusText);
    }
};

export const createRequest = (url: string) => {
    return async () => {
        const response = await fetch(url);
        try {
            const responseJson = await response.json();
            if (response.ok) {
                return responseJson;
            }
            throw new Error(responseJson.message);
        } catch (error) {
            throw new Error((error as Error).message || response.statusText);
        }
    };
};

export const fetchResourceData = (resourceId: string) => {
    const url = `${arches.urls["api_resources"](resourceId)}?format=json&v=beta&compact=false`;
    return createRequest(url)();
};

export const fetchImageData = (
    imageResourceIds: string[],
    isItem?: boolean,
) => {
    let url = `${arches.urls["api-file-data"]}?resourceids=${imageResourceIds.join(",")}`;
    if (isItem) {
        url += `&item=${isItem}`;
    }
    return createRequest(url)();
};

export const fetchResourceBounds = (resourceId: string) => {
    const url = arches.urls["api-resource-bounds"](resourceId);
    return createRequest(url)();
};

export const fetchResourceGeoJSON = (resourceId: string) => {
    const url = arches.urls["api-resource-geojson"](resourceId);
    return createRequest(url)();
};

export const fetchSettings = createRequest(arches.urls["api-settings"]);
export const fetchMapData = createRequest(arches.urls["api-map-data"]);
