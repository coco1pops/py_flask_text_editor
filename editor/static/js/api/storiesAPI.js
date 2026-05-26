import { apiRequest } from "./api.js";


export function updateStory(story_id, field, new_value) {
    const options = {
        url: "/update_story",
        type: "post",
        data: { 'story_id': story_id, 'field': field, 'new value': new_value },
        dataType: 'json'
    };
    return apiRequest(options);
}

export function postStory(story_id, chapter_id, prompt, mode, row_id, chars) {
    const options = {
        url: "/generate",
        type: "post",
        data: { 'story_id': story_id, 'chapter_id' : chapter_id, 'prompt': prompt, 'mode': mode, 'row_id': row_id, 'chars': JSON.stringify(chars) },
        dataType: 'json'
    };
    return apiRequest(options);
}

export function deleteStoryPosts(post_id, story_id, chapter_id) {
    const options = {
            url: "/deleteRows",
            type: "post",
            data: { 'post_id': post_id, "story_id" : story_id, "chapter_id" : chapter_id },
            dataType: "json"
    };
    return apiRequest(options);
}     

export function addStoryCharacter(story_id, char_id, char_notes) {
    const options = {
            url: "/addStoryCharacter",
            type: "post",
            data: { 'story_id': story_id, 'char_id': char_id, 'char_notes': char_notes },
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

export function getStoryCharacter(id) {
    const options = {
            url: "/getStoryCharacter",
            type: "post",
            data: { 'id': id },
            dataType: "json"
    };
    return apiRequest(options);
}

export function updateStoryCharacter(id, note) {
    const options = {
            url: "/updateStoryCharacter",
            type: "post",
            data: { 'id': id, 'note': note },
            dataType: "json"
    };
    return apiRequest(options);
}

export function deleteStoryCharacter(id) {
    const options = {
            url: "/deleteStoryCharacter",
            type: "post",
            data: { 'id': id },
            dataType: "json"
    };
    return apiRequest(options);
}

export function getListItem(char_id, input_name, dropdown_id) {
    const options = {
            url: "/build_char_list_item",
            type: "post",
            data: { 'char_id': char_id, 'input_name': input_name, 'dropdown_id': dropdown_id },
            dataType: "json"
    };
    return apiRequest(options);
}

export function addButtons(post_id) {
    const options = {
            url: "/addButtons",
            type: "post",
            data: { 'post_id': post_id },
            dataType: "json"
    };
    return apiRequest(options);
}