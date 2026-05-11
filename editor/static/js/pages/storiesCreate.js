import { resizeTextarea, updateLabel, displaySafetySettings } from "../ui/storiesUI.js";
import { pickSysInt, buildSysIntOptions, addStoryChar, openEditModal, deleteStoryChar, updateCharNotes, generateSummary } from "../controller/storiesAddController.js";

export function initStoriesAdd() {
    // Initialization logic for stories add page
    const raw = document.getElementById('isadmin-data').dataset.isadmin;
    const isadmin = JSON.parse(raw);

    displaySafetySettings(isadmin);

    document.getElementById('applySysInt').addEventListener('click', event => {
        pickSysInt();
    });

    document.getElementById('addChar').addEventListener('click', event => {
        const story_id = event.target.dataset.id;
        addStoryChar(story_id);
        event.preventDefault();
    });

    document.addEventListener('click', (event) => {

        const updateBtn = event.target.closest('.update-button');
        const deleteBtn = event.target.closest('.delete-button');

        if (updateBtn) {
            // Need to trigger display of modal window
            // Then prevent default form submission
            openEditModal(updateBtn.dataset.id);
            event.preventDefault();
        }
        else if (deleteBtn) {
            console.log("Delete button clicked with id:", deleteBtn.dataset.id);
            deleteStoryChar(deleteBtn.dataset.id);
            // Handle delete button click
        }   
        else if (event.target.id === 'saveCharBtn') {
            updateCharNotes(event.target.dataset.id);
        }
    });

    document.addEventListener('input', event => {
        if (event.target.classList.contains('entry-textarea')) {
            resizeTextarea(event.target);
        }
        else if (event.target.classList.contains('form-range')) {
            updateLabel(event.target.id);
            generateSummary();
        }
    });

    document.getElementById('closeModal').addEventListener('click', event => {
        buildSysIntOptions();
    });

}   
