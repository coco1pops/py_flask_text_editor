import { apiRequest } from "./api.js";

export function deleteSysInt(id) {
    const options = {
            url: "/deletesysint",
            type: "post",
            data: { 'sysint_id': id },
            dataType: "json"
    };
    return apiRequest(options);
}
export function getImageUploadURL(formData) {
    const options = {
            url: "/checkimage",
            type: "post",
            data: formData,
            processData: false,
            contentType: false,
            dataType: "blob"
    };
    return apiRequest(options);
}

export function deleteChar(id) {
    const options = {
            url: "/deletechar",
            type: "post",
            data: { 'char_id': id },
            dataType: "json"
    };
    return apiRequest(options);
}

export function deleteUser(id) {
    const options = {
            url: "/deleteuser",
            type: "post",
            data: { 'user_id': id },
            dataType: "json"
    };
    return apiRequest(options);
}

