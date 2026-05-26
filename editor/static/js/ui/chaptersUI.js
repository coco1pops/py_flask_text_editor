import { resizeTextarea, displayMessages, gotoBottom } from "./storiesUI.js";

export function editSummaryHandler(but) {
    but.classList.add("d-none");
    const html=document.getElementById("summary-box-display");
    html.classList.add("d-none");
    const cancelEditButton=document.getElementById("cancel-edit-summary");
    cancelEditButton.classList.remove("d-none");
    const updateSummaryButton=document.getElementById("update-summary");
    updateSummaryButton.classList.remove("d-none");
    const summary=document.getElementById("summary");
    summary.classList.remove("d-none");
    disableForSummary(true);
    summary.dispatchEvent(new Event("input", { bubbles: true }));
}

export function cancelEditSummaryHandler(but) {
    const summaryBox=document.getElementById("summary-box");
    const summary=document.getElementById("summary");
    const html=document.getElementById("summary-box-display");

    summary.value=summaryBox.dataset.summary;
    html.innerHTML=JSON.parse(summaryBox.dataset.dispSummary);
    html.classList.remove("d-none");
    summary.classList.add("d-none");

    but.classList.add("d-none");
    const cancelEditButton=document.getElementById("edit-summary");
    cancelEditButton.classList.remove("d-none");
    const updateSummaryButton=document.getElementById("update-summary");
    updateSummaryButton.classList.add("d-none");

    disableForSummary(false);
    summary.dispatchEvent(new Event("input", { bubbles: true }));
}

export function disableForm(flag){
    const form = document.querySelector("#input-area");

    form.querySelectorAll("input, select, textarea, button").forEach(el => {
        if (el.id !="gotoTop"){
            el.disabled = flag;
        }
    });
}

export function displaySummary(disp_summary, raw_summary, status, newStatus, messages) {
    const summaryBoxDisplay=document.getElementById("summary-box-display");
    summaryBoxDisplay.innerHTML=disp_summary;
    summaryBoxDisplay.classList.remove("d-none");

    const summaryBox=document.getElementById("summary-box");
    summaryBox.dataset.dispSummary=JSON.stringify(disp_summary);
    summaryBox.dataset.summary=raw_summary;

    const summary=document.getElementById("summary");
    summary.value=raw_summary;
    
    const statusSpan=document.getElementById("statusSpan");
    if (status == "in_progress"){
        summaryBox.classList.remove("d-none");}

    const statusField=document.getElementById("status");
    statusField.dataset.status=newStatus;

    let statusText="Draft";
    if (newStatus == "complete"){
        statusText="Complete"
    }
    if (statusText=="Draft") {
        disableForm(false);
    }
    statusSpan.innerHTML="<b>Status:</b> " + statusText;
    gotoBottom();
    displayMessages(messages);
}

export function displayUpdatedSummary(disp_summary, raw_summary, messages) {
    const summaryBoxDisplay=document.getElementById("summary-box-display");
    summaryBoxDisplay.innerHTML=disp_summary;
    summaryBoxDisplay.classList.remove("d-none");

    const summaryBox=document.getElementById("summary-box");
    summaryBox.dataset.dispSummary=JSON.stringify(disp_summary);
    summaryBox.dataset.summary=raw_summary;

    const summaryField=document.getElementById("summary");
    summaryField.classList.add("d-none");

    const cancelEditButton=document.getElementById("cancel-edit-summary");
    cancelEditButton.classList.add("d-none");
    const updateSummaryButton=document.getElementById("update-summary");
    updateSummaryButton.classList.add("d-none");
    const editButton=document.getElementById("edit-summary");
    editButton.classList.remove("d-none");

    displayMessages(messages);
    disableForSummary(false);
}

function disableForSummary(flag){
    const form = document.querySelector("#input-area");

    form.querySelectorAll("input, select, textarea, button").forEach(el => {
        if (el.id !="gotoTop" && el.id !="update-summary" && el.id !="cancel-edit-summary" && el.id !="summary"){
            el.disabled = flag;
        }
    });
}