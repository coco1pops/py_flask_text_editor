import { updateStory, postStory, deleteStoryPosts, getChar, addButtons } from '../api/storiesAPI.js';
import { updateChapter } from '../api/chaptersAPI.js';
import * as UI from '../ui/storiesUI.js';
import * as build from '../ui/storiesBuildTable.js';
import * as appState from '../state/appState.js';
import { initStories } from "../pages/stories.js";
import { logger } from '../utils/logger.js';
import { handleAjaxError } from '../utils/errors.js';
import { deleteClicked } from '../ui/modals.js';

// Startup Modules 
initPage();

document.addEventListener("DOMContentLoaded", function () {
        setFormMode("New", -1);

        const raw = document.getElementById('isadmin-data').dataset.isadmin;
        const isadmin = JSON.parse(raw);

        UI.displaySafetySettings(isadmin);
        UI.gotoBottom();
    });


export function initPage() {
    // Get the parent row details
  const formData=document.getElementById("form-data")
  const story_id=formData.dataset.storyId;
  const chapter_id=formData.dataset.chapterId;

  appState.setStory(story_id);
  appState.setChapter(chapter_id);

  initStories();
}

// Update story record

export async function handleInput(event) {
  //No loading state for now, but we can add one if we want to
  let response;
  try {
    
    response = await updateStory(appState.getState().story_id, event.target.id, event.target.value);

  } catch (err) {
    handleAjaxError(err, "Update Story");
    return

  }
  if (response && response.success) {
    // We could show a success message here if we wanted to, but for now we'll just log the response
    logger.log("Story updated successfully");
  }

}

export async function updateChapterField(event) {

  let response;
  try {
    response = await updateChapter(appState.getState().story_id, appState.getState().chapter_id, event.target.id, event.target.value);

  } catch (err) {
    handleAjaxError(err, "Update Chapter");
    return

  }
  if (response && response.success) {
    logger.log("Story updated successfully");
  }
}

export async function cancelUpdate() {
  let response;
  try {

    response = await updateStory(appState.getState().story_id, "newprompt", "");
  } catch (err) {
    handleAjaxError(err, "Cancel Update");
    return;
  }
  if (response && response.success) {
    logger.log("Story update cancelled successfully");
    appState.setFormMode("New");
    appState.setEditRow(-1);
    UI.clearNewPrompt();
  }
}

// Post prompt

export async function post() {
  const prompt = document.getElementById("newprompt").value; //The current value of the prompt field
  const tbody = document.getElementById("postsRows"); // The tbody element that contains the posts. We'll append new posts to this element

  UI.prePost();
  UI.startSpinner();

  let response;
  try {

    response = await postStory(
      appState.getState().story_id,
      appState.getState().chapter_id, 
      prompt, 
      appState.getState().formMode, 
      appState.getState().editRow, 
      appState.getState().chars);

  } catch (err) {
      handleAjaxError(err, "Post Prompt");
      logger.error(err);
    // Currently extracts data from the error object and shows a flash message.
      const messages = JSON.parse(err?.jqXHR?.responseText)?.messages;
      if (messages) {
        UI.displayMessages(messages);
      }        
  } finally {

    if (response && response.success) {
      logger.log(response);
      build.buildClearLastRowButtons(tbody);
      tbody.insertAdjacentHTML('beforeend', response.posts);
     
      UI.clearNewPrompt();
      UI.displayMessages(response.messages);
    }
    UI.postPost();
    UI.stopSpinner();
    setFormMode("New", -1);
}
}

// Update edited row

export async function updateRow(btn, mode) {
  const row = btn.closest("tr");
  const id = appState.getState().editRow;
  const spinner_id = 'loadingSpinner_' + id;
  UI.startSpinner(spinner_id);

  const prompt = document.getElementById("editBox").value;
  let response;
  try {
    response = await postStory(
        appState.getState().story_id,
        appState.getState().chapter_id, 
        prompt, 
        appState.getState().formMode, 
        appState.getState().editRow, 
        appState.getState().chars);


  } catch (err) {
      handleAjaxError(err, "Update Post");
      const messages = JSON.parse(err?.jqXHR?.responseText)?.messages;
      if (messages) {
        UI.displayMessages(messages);
      }       
      UI.stopSpinner(spinner_id);

    } finally {
    if (response && response.success) {
    // Remove subsequent rows
      if (mode == "Edit Prompt") {
        const tbody = row.parentElement;
        // if successful then the current row is delete along with all subsequent rows and replaced with the updated rows from the response
        build.buildDeleteNextRows(row);
        tbody.insertAdjacentHTML('beforeend', response.posts);
      }
      else {
        // if unsuccessful then the current row is reset to the original value and buttons are removed. The inner html is replaced, erasing the editbox
        const mdiv = "message_" + id;
        const cell = document.getElementById(mdiv);

        const updpost = response.posts[0];
        cell.innerHTML = updpost.message;
        cell.dataset.html = JSON.stringify(updpost.message);
        cell.dataset.markdown = JSON.stringify(updpost.message_md);
        UI.resetTableRow(row);
        UI.stopSpinner(spinner_id);
      };
      UI.clearNewPrompt();
      UI.postPost();
      logger.log(response);
      UI.displayMessages(response.messages);
      setFormMode("New", -1);
    }
  }
}

// delete edited row and subsequent rows 

export async function deleteRow() {

  let response;
  try {
    response = await deleteStoryPosts(
      appState.getState().editRow, 
      appState.getState().story_id,
      appState.getState().chapter_id);

  } catch (err) {
      handleAjaxError(err, "Delete Posts");

  } finally {
    if (response && response.success) {
      logger.log("Posts deleted successfully");
      const row_div = "row_" + appState.getState().editRow;
      const row = document.getElementById(row_div);
      build.buildDeleteNextRows(row);
      row.remove();
      addButtonsToLast();
      UI.postPost();
      UI.clearNewPrompt();
      UI.displayMessages(response.messages);
    }
  
  setFormMode("New", -1);
  }
}

async function addButtonsToLast() {
    const tbody = document.getElementById("postsRows");
    if (!tbody.rows.length) return; // No data rows

    const rows = tbody.rows;
    const row = rows[rows.length - 1]; // This is the last row. It should always be a 'model' row

    const id = row.cells[0].textContent;
    const message_id = "message_" + id;
    if (!document.getElementById(message_id).classList.contains("model")) {
        logger.error("Error - invalid table format");
        return false
    };

    const sel = "buttons_" + id;
    const target_div = document.getElementById(sel);

    let response;
    try {
        response = await addButtons(id);
    } catch (err) {
        handleAjaxError(err, "Add Buttons");
        return;
    } finally{
      if (response && response.success) {
        target_div.innerHTML = response.html;
      }
    }
  }

export async function addChar(char_id) {
  let response;
  try {
    response = await getChar(char_id);
  } catch (err) {
    handleAjaxError(err, "Assign Character");
    return
  }
  logger.log(response);
  if (response && response.success) {
    appState.addChar(char_id)
    build.buildAddChar(char_id, response.details['image_mime_type'], response.details['img'], response.details['text']);
    UI.gotoBottom();
  };
}

// Editor functions

// Puts a row into edit mode

export function editRow(btn, id, mode) {
  UI.prePost();

  const row = btn.closest("tr");
  UI.setRowInEditMode(row, mode);
  // Highlight the selected row

  setFormMode(mode, id);

};

// Takes a row out of edit mode and resets the content to the original value

export function cancelEditRow(btn, id) {
  const row = btn.closest("tr");
  UI.resetEdit(row, id);
  UI.postPost();

  setFormMode("New", -1);
};

// Prompts for confirmation and deletes the post (and subsequent posts). Called from the delete button in edit mode.

export function deleteEditRow() {
        deleteClicked(appState.getState().editRow, deleteRow, "this post");
    };

export function clearChar(id) {
    logger.log("Clearing char " + id);
      build.buildRemoveChar(id);
      appState.removeCharId(id); 
    };
 
// Utility functions

// Sets appState and updates the UI

function setFormMode(mode, id) {
  appState.setFormMode(mode);
  appState.setEditRow(id);
  appState.setChars([]);
  UI.setMode(mode);

};