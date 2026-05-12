import { handleInput, updateChapterField, post, cancelUpdate, editRow, updateRow, cancelEditRow, deleteEditRow, addChar, clearChar } from "../controller/storiesController.js";
import { resizeTextarea, updateCount, gotoTop, gotoBottom, updateLabel, updateTitle } from "../ui/storiesUI.js";


export function initStories() {
    bindEvents();
    hideStudioElements();
};

function bindEvents() {


    document.addEventListener('input', event => {
        if (event.target.classList.contains('edit-row') || 
            event.target.classList.contains('chapter-record') ||  
            event.target.classList.contains('story-record')) {
            resizeTextarea(event.target);
        }
        else if (event.target.classList.contains('form-range')) {
            updateLabel(event.target.id);
        }
    });

    document.querySelectorAll(".chapter-record, .story-record").forEach(el => {
        el.dispatchEvent(new Event("input", { bubbles: true }));
    });

        
    // Add an event listener to every story field
    document.addEventListener('change', event => {
        if (event.target.classList.contains('story-record') || event.target.classList.contains('story-select')) {
            handleInput(event);
        }
        else if (event.target.classList.contains('chapter-record')) {
            updateChapterField(event);
        }
    });

    document.addEventListener('click', (event) => {
        const target = event.target;

        if (target.classList.contains('edit-button')) {
            editRow(target, target.dataset.id, target.dataset.mode);
        } else if (target.classList.contains('update-button')) {
            updateRow(target, target.dataset.mode);
        } else if (target.classList.contains('cancel-button')) {
            cancelEditRow(target, target.dataset.id);
        } else if (target.classList.contains('delete-button')) {
            deleteEditRow();
        } else if (target.classList.contains('clear-char')) {
            clearChar(target.dataset.id);  
        }

    });

    document.getElementById('newprompt').addEventListener('input', event => {
        updateCount(event.target);
    });

    document.getElementById('cancel').addEventListener('click', event => {
        cancelUpdate();
    });

    document.getElementById('submit').addEventListener('click', event => {
        post();
    });

    document.getElementById('gotoTop').addEventListener('click', event => {
        gotoTop();
    });

    document.getElementById('gotoBottom').addEventListener('click', event => {
        gotoBottom();
    });

    document.getElementById('assignCharForm').addEventListener('submit', function (e) {
        e.preventDefault();
        clearFlashMessage();
        const id = document.getElementById("charSelect").value;
        addChar(id);
    });

    document.getElementById('title').addEventListener('change', event => {
        updateTitle(event.target.value);
    });

    window.addEventListener("load", gotoBottom());
}
function hideStudioElements() {
    // Hide elements that are only relevant for the story studio page
    const elementsToHide = document.querySelectorAll('.create-only');
    elementsToHide.forEach(el => el.style.display = 'none');
}