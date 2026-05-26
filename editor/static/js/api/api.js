export async function apiRequest(options) {
    const method = (options.type || "GET").toUpperCase(); // Default to GET if not specified
    const fetchOptions = {
        method,
        headers: {}
    };

    // Handle POST/PUT/PATCH body

    if (options.data instanceof FormData) {
        fetchOptions.body = options.data;
    }
    else if (options.data) {
        // Match jQuery default form behaviour
        const formData = new URLSearchParams();
        Object.entries(options.data).forEach(([key, value]) => {
            formData.append(key, value);
        });

        fetchOptions.body = formData;
    }

    let response;
    try {
        response = await fetch(options.url, fetchOptions);
    }
    catch (error) {
        throw {
            textStatus: "network error",
            errorThrown: error
        };
    }

    // Handle HTTP errors
    if (!response.ok) {
        let responseText = "";
        let errorData = null;
        try {
            responseText = await response.text();
       
            try {
                errorData = JSON.parse(responseText);
            }
            catch {
                errorData = responseText;
            }
        } catch {
            responseText = "";
        }

        throw {
            jqXHR: {status: response.status, "responseText": responseText},
            textStatus: "error",
            errorThrown: errorData.message || `HTTP ${response.status}`
        };
    }

    // Match jQuery dataType handling
    if (options.dataType === "json") {
        return await response.json();
    }

    if (options.dataType === "text") {
        return await response.text();
    }

    if (options.dataType === "blob") {
        return await response.blob();
    }

    // Default
    return await response.text();
}