export function apiRequest(options) {
    return new Promise((resolve, reject) => {
        $.ajax(options)
            .done(resolve)
            .fail((jqXHR, textStatus, errorThrown) => {
                reject({ jqXHR, textStatus, errorThrown });
            });
    });
}

export function updateStory(story_id, field, new_value) {
    const options = {
        url: "/update_story",
        type: "post",
        data: { 'story_id': story_id, 'field': field, 'new value': new_value },
        dataType: 'json'
    };
    return apiRequest(options);
}

export function postStory(story_id,prompt, mode, row_id, chars) {
    const options = {
        url: "/generate",
        type: "post",
        data: { 'story_id': story_id, 'prompt': prompt, 'mode': mode, 'row_id': row_id, 'chars': JSON.stringify(chars) },
        dataType: 'json'
    };
    return apiRequest(options);
}

export function deleteStoryPosts(post_id, story_id) {
    const options = {
            url: "/deleteRows",
            type: "post",
            data: { 'post_id': post_id, "story_id" : story_id },
            dataType: "json"
    };
    return apiRequest(options);
}     

export function getChar(char_id) {
    const options = {
            url: "/assignChar",
            type: "post",
            data: { 'char_id': char_id },
            dataType: "json"
    };
    return apiRequest(options);
} 

export function getSysInt(sysint_id) {
    const options = {
            url: "/getSysInt",
            type: "post",
            data: { 'sysint_id': sysint_id },
            dataType: "json"
    };
    return apiRequest(options);
}