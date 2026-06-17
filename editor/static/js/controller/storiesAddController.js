import { getSysInt, addStoryCharacter, updateStoryCharacter, deleteStoryCharacter, getStoryCharacter, getListItem } from "../api/storiesAPI.js";
import { initStoriesAdd } from "../pages/storiesCreate.js";
import { handleAjaxError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import "../ui/textarearesize.js";

document.addEventListener("DOMContentLoaded", function () {
    initStoriesAdd();
});

//
// Takes data from the studio settings and builds a system instruction that incorporates the various settings in a human-readable way, to guide the model's output.
//
export function buildSysIntOptions(sysInt) {
    const repetition = parseFloat(document.getElementById("repetition").value);
    const pacing = parseFloat(document.getElementById("pacing").value);
    const style = parseFloat(document.getElementById("style").value);  

    // Add repetition guidance

    if (repetition > 1.3) {
        sysInt = sysInt + "\nAvoid repeating distinctive words or imagery."
    }
    else if (repetition < 0.7) {
        sysInt = sysInt + "\nRepetition is acceptable for thematic effect."
    }

    // Add pacing guidance

    if (pacing > 1.3) {
        sysInt = sysInt + "\nUse shorter sentences and increase narrative momentum."
    } else if (pacing < 0.7) {
        sysInt = sysInt + "\nUse richer description and slower scene development."
    }

    // Add Style strength guidance
    if (style > 1.3) {
        sysInt = sysInt + "\nLean strongly into a distinctive narrative voice."
    } else if (style < 0.7) {
        sysInt = sysInt + "\nKeep the prose neutral and unobtrusive."
    }
    return sysInt;
}
//
// Generates a summary of the current studio settings to provide user feedback on how the model's output may be influenced by the current settings.
//
export function generateSummary() {
    const temp = parseFloat(document.getElementById("temperature").value);
    const rep = parseFloat(document.getElementById("repetition").value);
    const pace = parseFloat(document.getElementById("pacing").value);

    let creativity =
        temp < 0.6 ? "Controlled" :
            temp < 0.95 ? "Balanced" :
                "Highly creative";

    let repText =
        rep < 0.7 ? "may reuse phrasing" :
            rep < 1.3 ? "moderate variation" :
                "actively avoids repetition";

    let pacingText =
        pace < 0.7 ? "slow and descriptive" :
            pace < 1.3 ? "steady pacing" :
                "fast and dynamic";

    summaryBox.textContent =
        `${creativity} prose, ${pacingText}, ${repText}.`;
}
//
// This function applies the studio settings to the SysInt selected, raises an event to update the filed and sets a flag to indicate that the settings have been applied, 
// so that the user is aware that the SysInt and defaults have been modified from the defaults will not be applied when the story is added. 
//
export async function pickSysInt() {
    const id = document.getElementById("sysIntSelect").value;
    let sysInt;
    if (!id) {
        sysInt="";
    }
    else {
        let response;
        try {
            response = await getSysInt(id);
            if (response && response.success) {  
                sysInt = response.instruction;
            }
        } catch (err) {
            handleAjaxError(err, "Get System Instruction");
        }
    }
    document.getElementById("studio_temperature").value = document.getElementById("temperature").value;
    document.getElementById("studio_top_p").value = document.getElementById("top_p").value;
    document.getElementById("studio_harassment_threshold").value = document.getElementById("harassment_threshold").value;
    document.getElementById("studio_hate_speech_threshold").value = document.getElementById("hate_speech_threshold").value;
    document.getElementById("studio_dangerous_content_threshold").value = document.getElementById("dangerous_content_threshold").value;
    document.getElementById("studio_explicit_content_threshold").value = document.getElementById("explicit_content_threshold").value;
    document.getElementById("studio_model").value = document.getElementById("model").value;

    const updatedSysInt = buildSysIntOptions(sysInt);
    const systemInstructionField = document.getElementById("systeminstruction");
    systemInstructionField.value = updatedSysInt;
    systemInstructionField.dispatchEvent(new Event('input', { bubbles: true }));

    document.getElementById('paramsSaved').value = "True";      

}
//
// This function adds a character to the story based on the character selected in the add character dropdown also adds the notes provided, then clears the form fields.
//
export async function addStoryChar(story_id) {
    const charId = document.getElementById("charSelect").value;
    if (!charId) {
        return
    }
    const charNotes = document.getElementById("charNotes").value;
    let response;
    try {
        response= await addStoryCharacter(story_id, charId, charNotes);
    }
    catch (err) {
        handleAjaxError(err, "Add Story Character");
    }
    finally{
        if (response && response.success) {
            // Clear form fields
            document.getElementById('charSelect').value = ""; 
            document.getElementById('charDropdown').innerText = "-- Select a character --";
            document.getElementById('charNotes').value = ""; 
            
            const id = response.id;
            const name = response.storyChar.name;
            const description = response.storyChar.description;
            const charNotes = response.storyChar.note;
            // Remove the character from the dropdown
            const li_id=`pick-${charId}`;
            const optionToRemove = document.getElementById(li_id);
            if (optionToRemove) {
                optionToRemove.remove();
            }
            addStoryCharsRow(id, name, description, charNotes);   
        }
    }
}

export async function openEditModal(id) {
    const modalElement = document.getElementById('editCharModal');
    let modal = bootstrap.Modal.getInstance(modalElement);

    if (!modal) {
        modal = new bootstrap.Modal(modalElement);
    }

    let response;
    try{
            response= await getStoryCharacter(id);

        if (response && response.success) {
            const saveButton = document.getElementById('saveCharBtn')
            saveButton.setAttribute('data-id', id);
            document.getElementById('editTitle').textContent = `Edit Notes for Character: ${response.storyChar.name}`;
            document.getElementById('editCharDescription').innerText = response.storyChar.description;
            document.getElementById('editCharNotes').value = response.storyChar.note;
            modal.show();
        }

    } catch (err) {
        handleAjaxError(err, "Get Story Character");
    }  
}   

export async function updateCharNotes(id) {
    const newNotes = document.getElementById('editCharNotes').value;
    let response;
    try{
        response= await updateStoryCharacter(id, newNotes);
    } catch (err) {
        handleAjaxError(err, "Update Story Character");
    } finally {
        if (response && response.success) {
            const table = document.getElementById("storyCharsTable");
            const row = table.querySelector('tr[data-id="' + id + '"]');
            row.cells[3].textContent = newNotes;
  
            const modalElement = document.getElementById('editCharModal');
            let modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
        }
    }
}

export async function deleteStoryChar(id) {
    const modal = document.getElementById('editCharModal');
    logger.log("Attempting to delete story char with id:", id);

    let response;
    try{
        response= await deleteStoryCharacter(id)
    } catch (err) {
        handleAjaxError(err, "Delete Story Character");
    } finally {  

        if (response && response.success) {
            const table = document.getElementById("storyCharsTable");
            var i = table.querySelector('tr[data-id="' + id + '"]').rowIndex;
            table.deleteRow(i);
            addBackToDropdown(response.char_id);
        }
    }

}   
function addStoryCharsRow(id, name, description, notes) {
    const table = document.getElementById('storyCharsTable');
    const tbody = table.querySelector('tbody');
    const row = document.createElement('tr');
    row.setAttribute('data-id', id);
    const html = buildRow(id, name, description, notes);
    row.innerHTML = html;
    tbody.appendChild(row);
}

function buildRow(id, name, description, notes) {

    const html = `
        <td class="d-none" id="${id}>"</td>
        <td>${name}</td>
        <td style="max-width: 400px;">${description}</td>
        <td>${notes}</td>
        <td class="button_col">
            <form method="post">
                <button type="submit" name="action" value="${id}"                    
                    class="btn btn-secondary update-button" data-id="${id}">
                    <i class="bi bi-pen-fill"></i>
                </button>
            </form>
        </td>
        <td class="button_col">
            <button class="btn btn-danger delete-button" type="button" data-id="${id}">
                <i class="bi bi-trash-fill"></i>
            </button>
        </td>
    </tr>   `;
    return html;

}   
async function addBackToDropdown(charId,  input_name="charSelect", dropdownId="charDropdown") {
    let response;
    try {
        response = await getListItem(charId, input_name, dropdownId);

    } catch (err) {
        handleAjaxError(err, "Get Character for Dropdown");
    } finally {
        if (response && response.success) {
            dropdownId = `ul-${dropdownId}`;
            const ul=document.getElementById(dropdownId);
            ul.insertAdjacentHTML('beforeend', response.listItem);
        }
    }
}