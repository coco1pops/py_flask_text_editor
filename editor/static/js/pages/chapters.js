import { involvedHandler, overrideHandler, noteHandler, summaryHandler, completeHandler, updateSummaryHandler} from "../controller/chaptersController.js";
import * as UI from "../ui/chaptersUI.js";
import { gotoTop, gotoBottom } from "../ui/storiesUI.js";

export function addEventHandlers() {
    document.addEventListener('change', (event) => {
        const target=event.target;
        if (target.classList.contains('involved')) {
           involvedHandler(target);
        }
        else if (target.classList.contains('override')){
           overrideHandler(target); 
        }
        else if (target.classList.contains('entry-note')){
            noteHandler(target)
         }

    })

    const status=document.getElementById("status").dataset.status

    const summariseButton=document.getElementById('summarise');
    if (summariseButton) {
        summariseButton.addEventListener('click', event => {
            event.preventDefault();
            summaryHandler("draft");
        });
    }

    const completeButton=document.getElementById('complete');
    if (completeButton) {
        completeButton.addEventListener('click', event => {
            event.preventDefault();
            completeHandler();
        });
    }

    const editSummaryButton=document.getElementById('edit-summary');
    if (editSummaryButton) {
        editSummaryButton.addEventListener('click', event => {
            event.preventDefault();
            UI.editSummaryHandler(event.target);
        });
    }

    const cancelEditSummaryButton=document.getElementById('cancel-edit-summary');
    if (cancelEditSummaryButton) {
        cancelEditSummaryButton.addEventListener('click', event => {
            event.preventDefault();
            UI.cancelEditSummaryHandler(event.target);
        });
    }

    const updateSummaryButton=document.getElementById('update-summary');
    if (updateSummaryButton) {
        updateSummaryButton.addEventListener('click', event => {
            event.preventDefault();
            updateSummaryHandler();
        });
    }

    document.getElementById('gotoTop').addEventListener('click', event => {
        event.preventDefault();
        gotoTop();
    });

    document.getElementById('gotoBottom').addEventListener('click', event => {
        gotoBottom();
    });

    if (status=="complete"){
        UI.disableForm(true);
    }
}