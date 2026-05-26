import { apiRequest } from "./api.js";

export function delChapter(story_id, chapter_id) {
    const options = {
            url: "/delete_chapter",
            type: "post",
            data: { 'story_id': story_id, 'chapter_id': chapter_id },
            dataType: 'json'
    };
    return apiRequest(options);
}

export async function prtChapter(story_id, chapter_id, story_title) {
 const response = await fetch("/print_chapter", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        story_id,
        chapter_id,
        story_title
    })
    });

    // Handle server errors
    if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
            // Try JSON first
            const data = await response.json();
            errorMessage = data.error || errorMessage;
        } catch {
            try {
                // Fallback to plain text
                errorMessage = await response.text();
            } catch {
                // keep default
            }
        }
        throw new Error(errorMessage);
    }

    // Successful file response
    const blob = await response.blob();

    // Extract filename if supplied
    let filename = "chapter.docx";

    const disposition = response.headers.get("Content-Disposition");

    if (disposition) {
        const match = disposition.match(/filename="?(.+?)"?$/);
        if (match) {
            filename = match[1];
        }
    }

    return {
        blob,
        filename
    };
}

export function delStory(story_id) {
    const options = {
            url: "/delete_story",
            type: "post",
            data: { 'story_id': story_id },
            dataType: 'json'
        };
 
    return apiRequest(options);
}

export async function prtStory(story_id, story_title) {
 const response = await fetch("/print_story", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        story_id,
        story_title
    })
    });

    // Handle server errors
    if (!response.ok) {
        let errorMessage = `HTTP ${response.status}`;
        try {
            // Try JSON first
            const data = await response.json();
            errorMessage = data.error || errorMessage;
        } catch {
            try {
                // Fallback to plain text
                errorMessage = await response.text();
            } catch {
                // keep default
            }
        }
        throw new Error(errorMessage);
    }

    // Successful file response
    const blob = await response.blob();

    // Extract filename if supplied
    let filename = "story.docx";

    const disposition = response.headers.get("Content-Disposition");

    if (disposition) {
        const match = disposition.match(/filename="?(.+?)"?$/);
        if (match) {
            filename = match[1];
        }
    }

    return {
        blob,
        filename
    };
}