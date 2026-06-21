import arches from "arches";
import Cookies from "js-cookie";

export const fetchResourceLastEdited = async (resourceInstanceId: string) => {
    const response = await fetch(
        arches.urls["api-resource-last-edited"](resourceInstanceId),
    );
    if (!response.ok) {
        throw new Error(response.statusText);
    }
    return await response.json();
};

export const fetchLifecycleState = async (resourceInstanceId: string) => {
    const response = await fetch(
        arches.urls.api_resource_instance_lifecycle_state(resourceInstanceId),
    );
    if (!response.ok) {
        throw new Error(response.statusText);
    }
    return await response.json();
};

export const updateLifecycleState = async (
    resourceInstanceId: string,
    lifecycleStateId: string,
) => {
    const response = await fetch(
        arches.urls.api_resource_instance_lifecycle_state(resourceInstanceId),
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": Cookies.get("csrftoken") as string,
            },
            body: JSON.stringify(lifecycleStateId),
        },
    );
    const parsed = await response.json();
    if (!response.ok) {
        throw new Error(parsed.message || response.statusText);
    }
    return parsed;
};
