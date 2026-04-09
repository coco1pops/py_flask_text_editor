import { updateStory, postStory, deleteStoryPosts, getChar } from '../api/storiesAPI.js';
import * as UI from '../ui/storiesUI.js';
import * as build from '../ui/storiesBuildTable.js';
import * as appState from '../state/appState.js';
import { initStories } from "../pages/stories.js";

// Startup Modules 
initPage();

document.addEventListener("DOMContentLoaded", function () {
        setFormMode("New", -1);
        const raw = document.getElementById('posts-data').dataset.posts;
        const posts = JSON.parse(raw);

        const tbody=document.getElementById("postsRows");
        build.buildAddNewRows(tbody,posts);

        // Maps for displaying safety settings in a more user-friendly way
        const thresholdMap = {
            "BLOCK_LOW_AND_ABOVE": "Strict",
            "BLOCK_MEDIUM_AND_ABOVE": "Moderate",
            "BLOCK_ONLY_HIGH": "Relaxed",
            "BLOCK_NONE": "Off"
        };

        const isAdmin = JSON.parse(document.getElementById('isadmin-data').dataset.isadmin);

        if (!isAdmin) {
            document.getElementById("hate_speech_threshold").value = thresholdMap[document.getElementById("hate_speech_threshold").value];
            document.getElementById("harassment_threshold").value = thresholdMap[document.getElementById("harassment_threshold").value];
            document.getElementById("explicit_content_threshold").value = thresholdMap[document.getElementById("explicit_content_threshold").value];
            document.getElementById("dangerous_content_threshold").value = thresholdMap[document.getElementById("dangerous_content_threshold").value];
        };

        UI.gotoBottom();

    });


export function initPage() {
  //setFormMode("New", -1);

  const urlParams = new URLSearchParams(window.location.search);
  const story_id = urlParams.get('story_id');
  appState.setStory(story_id);

  initStories();
}

// Wrappers for API calls

// Update story record

export async function handleInput(event) {
  //No loading state for now, but we can add one if we want to
  let response;
  try {
    response = await updateStory(appState.getState().story_id, event.target.id, event.target.value);

    // No need to update the UI with the new value, since it's already there. But we can check if the update 
    // was successful and show an error if it wasn't

  } catch (err) {
    handleAjaxError(err, "Update Story");

  }
  if (response && response.success) {
    // We could show a success message here if we wanted to, but for now we'll just log the response
    console.log("Story updated successfully");
  }

  // No end loading state to clear, but we could do that here if we had one
}

export async function cancelUpdate() {
  let response;
  try {
    response = await updateStory(appState.getState().story_id, "newprompt", "");
  } catch (err) {
    handleAjaxError(err, "Cancel Update");
  }
  if (response && response.success) {
    console.log("Story update cancelled successfully");
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
    response = await postStory(appState.getState().story_id, prompt, appState.getState().formMode, appState.getState().editRow, appState.getState().chars);
  } catch (err) {
      handleAjaxError(err, "Post Prompt");
    // Currently extracts data from the error object and shows a flash message.
  }
  if (response && response.success) {
    // Currently:
    // 1. Takes the buttons off the last row (if there is one)
    // 2. Appends the new post to the end of the table
    // 3. Blanks out newprompt (Done)
    // 4. Shows the message from the server in a flash message
    console.log(response);
    build.buildClearLastRowButtons(tbody);
    build.buildAddNewRows(tbody, response.posts);
    UI.clearNewPrompt();
    UI.displayMessages(response.messages);
  }
  // Even after an error we want to clear the loading state and set the form back to New mode.

  // Also calls resetEdit which is a multipurpose function that is either called with a row or all. In this case it is called with all. It:
  // 1. Enables all the action buttons (Done)
  // 2. Enables the prompt field (Done)
  // 3. Resets the form mode to New and row to -1 in the app state (Done)
  // 4. Updates the counts (Done)
  // 5. Scrolls to the bottom of the page (Done)
  UI.postPost();
  UI.stopSpinner();
  setFormMode("New", -1);
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
    response = await postStory(appState.getState().story_id, prompt, appState.getState().formMode, appState.getState().editRow, appState.getState().chars);
  } catch (err) {
    handleAjaxError(err, "Update Post");
    UI.stopSpinner(spinner_id);
  }
  if (response && response.success) {
    // Remove subsequent rows
    if (mode == "Edit Prompt") {
      const tbody = row.parentElement;
      build.buildDeleteNextRows(row);
      build.buildAddNewRows(tbody, response.posts);
    }
    else {
      const mdiv = "message_" + id;
      const cell = document.getElementById(mdiv);

      const updpost = response.posts[0];
      cell.innerHTML = updpost.message;
      cell.dataset.html = updpost.message;
      cell.dataset.markdown = updpost.message_md;
      UI.resetTableRow(row);
      UI.stopSpinner(spinner_id);
    };
    UI.clearNewPrompt();
    UI.postPost();
    console.log(response);
    UI.displayMessages(response.messages);
    setFormMode("New", -1);
  }

}

// delete edited row and subsequent rows 

export async function deleteRow() {
  let response;
  try {
    response = await deleteStoryPosts(appState.getState().editRow, appState.getState().story_id);
  } catch (err) {
    handleAjaxError(err, "Delete Posts");
  }

  if (response && response.success) {
    console.log("Posts deleted successfully");
    const row_div = "row_" + appState.getState().editRow;
    const row = document.getElementById(row_div);
    build.buildDeleteNextRows(row);
    row.remove();
    build.buildResetLastRowButtons();
    UI.postPost();
    UI.clearNewPrompt();
    UI.displayMessages(response.messages);
  }
  setFormMode("New", -1);
}

export async function addChar(char_id) {
  let response;
  try {
    response = await getChar(char_id);
  } catch (err) {
    handleAjaxError(err, "Assign Character");
  }
  console.log(response);
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
    console.log("Clearing char " + id);
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

// Utility function for handling ajax errors in a consistent way across the module. 

function handleAjaxError({ err, context }) {
    // Extract useful info
    const statusCode = err.jqXHR?.status;
    const responseText = err.jqXHR?.responseText;
    const textStatus = err.textStatus;
    const errorThrown = err.errorThrown;  

    // Log (centralised)
    console.error("AJAX Error:", {
        statusCode,
        textStatus,
        errorThrown,
        responseText,
        context
    });

    // Delegate UI update
    UI.showError({
        statusCode,
        message: errorThrown || "An unexpected error occurred",
        context
    });
}