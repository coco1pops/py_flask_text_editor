let state = {
        story_id: null,
        chapter_id : null,
        formMode: "New",
        editRow: -1,
        chars: []
};

export function getState() {
    return state;
};   

export function setStory(story_id) {
    state.story_id = story_id ;
}  

export function setChapter(chapter_id) {
    state.chapter_id = chapter_id ;
}  

export function setFormMode(mode) {
    state.formMode = mode;
}

export function setEditRow(row) {
    state.editRow = row;
}
export function setChars(chars) {
    state.chars = chars;
}   

export function addChar(char) {
    state.chars.push(char);
}   

export function removeCharId(char) {
    const index = state.chars.indexOf(char);
    if (index !== -1) {
        state.chars.splice(index, 1);
    }
}   