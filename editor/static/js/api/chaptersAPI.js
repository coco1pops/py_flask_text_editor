import { apiRequest } from "./api.js";

export function updateChapter(story_id, chapter_id, field, new_value) {
    const options = {
        url: "/update_chapter",
        type: "post",
        data: { 'story_id': story_id, 'chapter_id' : chapter_id, 'field': field, 'new value': new_value },
        dataType: 'json'
    };
    return apiRequest(options);
}

export function addChapterCharacter(story_id, chapter_id, char_id) {     
    const options = {
            url: "/addChapterCharacter",
            type: "post",
            data: { 'story_id': story_id, 'chapter_id' : chapter_id, 'char_id': char_id },
            dataType: "json"
    };
    return apiRequest(options);
}

export function deleteChapterCharacter(id) {     
    const options = {
            url: "/deleteChapterCharacter",
            type: "post",
            data: { 'id': id },
            dataType: "json"
    };
    return apiRequest(options);
}

export function updateChapterCharacter(id, field, value) {     
    const options = {
            url: "/updateChapterCharacter",
            type: "post",
            data: { 'id': id, 'field' : field, 'value' : value },
            dataType: "json"
    };
    return apiRequest(options);
}

export function generateChapterSummary(story_id, chapter_id, status) {
    const options = {
            url: "/summarise_chapter",
            type: "post",
            data: { 'story_id': story_id, 'chapter_id' : chapter_id, 'status' : status },
            dataType: "json"
    };
    return apiRequest(options);
}
