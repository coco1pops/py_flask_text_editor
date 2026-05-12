import { updateChapter, addChapterCharacter, deleteChapterCharacter, updateChapterCharacter, generateChapterSummary} from '../api/storiesAPI.js';
import { resizeTextarea, displayMessages, startSpinner, stopSpinner, gotoTop, gotoBottom } from "../ui/storiesUI.js";
import * as UI from '../ui/chaptersUI.js' ;
import {addEventHandlers} from '../pages/chapters.js';

$(".entry-textarea").on("input change", function () {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
});

$(document).ready(function () {
    $(".entry-textarea").trigger("input");
});

document.addEventListener("DOMContentLoaded", function () {
    addEventHandlers();
});

export async function involvedHandler(chk){
    // Get the parent row details
    const formData=document.getElementById("form-data")
    const story_id=formData.dataset.storyId;
    const chapter_id=formData.dataset.chapterId;

    const row = chk.closest("tr");
    const characterId = row.dataset.characterId;
    const id = row.dataset.chapterCharId
    console.log("Retrieved story " + story_id + ", chapter " + chapter_id + ", character " + characterId )
    const override=row.querySelector(".override");

    if (chk.checked) {
        let response;
        try {
            response = await addChapterCharacter(story_id, chapter_id, characterId);
        }
        catch (err) {
            handleAjaxError({err, context: "Add Chapter Character"});
        }
        finally{
            if (response && response.success) {
                override.disabled=false;
                row.dataset.chapterCharId=response.row_id;            
            }   
        }   
    } else {
        let response;
        try {
            response=await deleteChapterCharacter(id);
        }
        catch (err) {
            handleAjaxError({err, context: "Delete Chapter Character"});
        } finally {
            if (response && response.success){
                override.disabled=true;
                row.dataset.chapterCharId="";
            }
        }
    }
}

export async function overrideHandler(chk){

    const row = chk.closest("tr");
    const id = row.dataset.chapterCharId;
    const noteText = row.querySelector(".display-note");
    const noteTextArea = row.querySelector(".entry-note");

    let response;
    try {
        response = await updateChapterCharacter(id, "override", chk.checked);
    }
    catch (err) {
        handleAjaxError({err, context: "Update Chapter Character"});
    }
    finally{
        if (response && response.success) {
            if (chk.checked) {
                noteText.classList.add("d-none");
                noteTextArea.classList.remove("d-none");
                resizeTextarea(noteTextArea);
            } else {
                noteText.classList.remove("d-none");
                noteTextArea.classList.add("d-none");
                noteTextArea.value=""
            }
        }   
    }   
}

export async function noteHandler(txt){
    const note=txt.value
    const row = txt.closest("tr");
    const id = row.dataset.chapterCharId;

    let response;
    try {
        response = await updateChapterCharacter(id, "note", note)
    }
    catch (err){
        handleAjaxError({err, context: "Update Chapter Character"});
    }
}

export async function summaryHandler(newStatus){

    const formData=document.getElementById("form-data")
    const story_id=formData.dataset.storyId;
    const chapter_id=formData.dataset.chapterId;

    const statusField=document.getElementById("status");
    const status=statusField.dataset.status

    // Disable form and make timer visible
    startSpinner("loading-spinner");
    UI.disableForm(true);
    
    let response;
    try {
        response = await generateChapterSummary(story_id, chapter_id, newStatus);
    } catch (err) {
        handleAjaxError({err, context: "Generate Summary"});
    } finally {
        // Hide timer
        stopSpinner("loading-spinner");
        if (response && response.success){
            UI.displaySummary(response.disp_summary, response.summary, status, newStatus, response.messages);
        }
    }
} 

export function completeHandler(){
    const title=document.getElementById("title").value;
    const options={'mode': 'complete', 'title': title};
    showBootstrapConfirm((confirmed) => {
        if (confirmed) {
            summaryHandler("complete");
            console.log("Confirmed complete!");
            }
        else {console.log ("Confirm cancelled.");
            };
        },options
    );
};

export async function updateSummaryHandler() {
    const formData=document.getElementById("form-data")
    const story_id=formData.dataset.storyId;
    const chapter_id=formData.dataset.chapterId;

    const summary = document.getElementById("summary").value;

    let response;
    try {
        response = await updateChapter(story_id, chapter_id, "summary", summary);
    }
    catch (err) {
        handleAjaxError({err, context: "Update Chapter"});
    }
    finally{
        if (response && response.success) {
            UI.displayUpdatedSummary(response.disp_summary, summary);
        }   
    }   
}