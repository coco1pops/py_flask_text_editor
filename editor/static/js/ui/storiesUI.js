import {logger} from "../utils/logger.js";
import { showFlashMessage, clearFlashMessage } from "./flashMessages.js";
import { showNotifyModal } from "./modals.js";

export function showError(err) {
    // This is a very basic error display function. We can make it more sophisticated later if we want to
    const errorMessage = `${err.context}. An error occurred: ${err.statusCode} - ${err.message}`;
    logger.error(errorMessage);
    showNotifyModal(errorMessage, "Error")
};

export function displayMessages(messages) {
    if (messages) {
        messages.forEach(([category, message]) => {
            showFlashMessage(category, message);
        });
    };
}

export function clearNewPrompt() {
    const np = document.getElementById("newprompt");
    np.value = "";
    updateCount(np);
    clearFlashMessage();
}

export function updateCount(fld) {
    const text = fld.value;
    document.getElementById("charCount").textContent = text.length;
    document.getElementById('submit').disabled = text.length < 5;
    document.getElementById('cancel').disabled = text.length < 5;
    resizeTextarea(fld);
}

export function resizeTextarea(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
}

export function prePost() {
    clearFlashMessage();
    document.querySelectorAll('.actions').forEach(btn => {
        btn.disabled = true;
    }); // Disable all the actiobuttons on the form
    document.getElementById("newprompt").disabled = true;
};

export function postPost() {
    // Re-enable newprompt (cleared if post was successful, left as is if not)
    const np = document.getElementById("newprompt");
    np.disabled = false;
    // Re-enable the action buttons
    document.querySelectorAll('.actions').forEach(btn => {
        btn.disabled = false;
    });
    gotoBottom();
}

export function gotoTop() {
    document.getElementById("top").scrollIntoView({
        behavior: "smooth"
    });
};

export function gotoBottom() {
    document.getElementById("end-placeholder").scrollIntoView({
        behavior: "smooth"
    });
};

export function setRowInEditMode(row) {
    row.classList.add("highlighted");

    // retrieve markdown prompt and replace html with a textarea
    const id = row.cells[0].textContent;
    const mdiv = "message_" + id;
    const cell = document.getElementById(mdiv);
    const celldata = JSON.parse(cell.dataset.markdown);
    const md = "<textarea class='full-size-textarea edit-row' height='auto' id='editBox'>" + celldata + "</textarea>";

    cell.innerHTML = md;
    const editBox = document.getElementById('editBox')
    editBox.style.height = editBox.scrollHeight + "px"; // Set to content height
    // Enable the buttons for the row in edit mode
    document.querySelectorAll('#' + row.id + ' .row-button').forEach(btn => {
        btn.disabled = false;
        btn.classList.remove("d-none");
    });
};

export function resetTableRow(row) {
    row.classList.remove("highlighted");
    document.querySelectorAll('#' + row.id + ' .row-button').forEach(btn => {
        btn.disabled = true;
        btn.classList.add("d-none");
    });
};

export function resetEdit(row, id) {
    const mdiv = "message_" + id;
    const cell = document.getElementById(mdiv);
    // This statement erases the edit box and replaces it with the original html, effectively resetting the row to its original state
    cell.innerHTML = JSON.parse(cell.dataset.html);

    row.classList.remove("highlighted");
    document.querySelectorAll('#' + row.id + ' .row-button').forEach(btn => {
        btn.disabled = true;
        btn.classList.add("d-none");
    })
};

export function startSpinner(id = "loadingSpinner") {
    const spinner = document.getElementById(id);
    spinner.style.display = 'inline-block'; // Show spinner
};

export function stopSpinner(id = "loadingSpinner") {
    const spinner = document.getElementById(id);
    spinner.style.display = 'none'; // Hide spinner
}

export function setMode(mode) {
    document.getElementById("mode").textContent = mode + " Mode";
    const target = document.getElementById("placeholder");
    target.innerHTML = "";
}

export function updateLabel(target) {
    const val = document.getElementById(target);
    const label = target + "Val";
    document.getElementById(label).textContent = parseFloat(val.value).toFixed(2);
}

export function updateTitle(title) {
    document.getElementById("story-title").textContent = "Story: " + title;
};

export function displaySafetySettings(isadmin) {
    if (!isadmin) {
        // Maps for displaying safety settings in a more user-friendly way
        const thresholdMap = {
            "BLOCK_LOW_AND_ABOVE": "Strict",
            "BLOCK_MEDIUM_AND_ABOVE": "Moderate",
            "BLOCK_ONLY_HIGH": "Relaxed",
            "BLOCK_NONE": "Off"
        };

        document.getElementById("hate_speech_threshold").value = thresholdMap[document.getElementById("hate_speech_threshold").value];
        document.getElementById("harassment_threshold").value = thresholdMap[document.getElementById("harassment_threshold").value];
        document.getElementById("explicit_content_threshold").value = thresholdMap[document.getElementById("explicit_content_threshold").value];
        document.getElementById("dangerous_content_threshold").value = thresholdMap[document.getElementById("dangerous_content_threshold").value];
    }
}
