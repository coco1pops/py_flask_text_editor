import "../ui/textarearesize.js";
import { getImageUploadURL, getFormattedText } from "../api/paramsAPI.js";
import { handleAjaxError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import { showNotifyModal } from "../ui/modals.js";

const urlParams = new URLSearchParams(window.location.search);
const char_id = urlParams.get('char_id');

const input = document.getElementById('imageUpload');
const fileName = document.getElementById('fileName');
const currentImage = document.getElementById('currentImage');


input.addEventListener('change', () => {
    uploadImage();

});

document.getElementById('edit-desc').addEventListener('click', event => {
    editDesc();
});

document.getElementById('edit-ok').addEventListener('click', event => {
    confEdit();
});

document.getElementById('edit-cancel').addEventListener('click', event => {
    cancelEdit();
});

async function uploadImage() {
    const urlParams = new URLSearchParams(window.location.search);
    const char_id = urlParams.get('char_id');

    const input = document.getElementById('imageUpload');
    const fileName = document.getElementById('fileName');
    const currentImage = document.getElementById('currentImage');

    fileName.textContent = input.files[0]?.name || 'No file chosen';
    if (input.files[0].name) {
        const formData = new FormData();
        formData.append("file", input.files[0]);  // input is your file input

        let response;
        try {
            response = await getImageUploadURL(formData);
        } catch (err) {
            logger.warn("Error getting upload URL:", err);
            fileName.textContent = 'No file chosen';
            input.value = '';
            if (err.jqXHR.status == "413") {
                showNotifyModal("File too large", "Error");
            }
            else if (err.jqXHR.status == "400") {
                showNotifyModal("Invalid file type", "Error");
            }
            else {
                handleAjaxError(err, "Upload Image");
            }
  
        } finally {
            if (response && response.success) {
                logger.log("Upload URL obtained successfully:", response.upload_url);
                const file = input.files[0];
                const reader = new FileReader();
                reader.onload = function (e) {
                    currentImage.src = '';
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };

                reader.readAsDataURL(file);
                uploadImage(formData, response.upload_url);
            }
        }
    }
}

function editDesc() {
    // Need to hide the button and display the other buttons
    const edit = document.getElementById("edit-desc");
    edit.classList.add("d-none");
    const ok = document.getElementById("edit-ok");
    ok.classList.remove("d-none");
    const cancel=document.getElementById("edit-cancel");
    cancel.classList.remove("d-none");
    // Need to swap text area and span
    const span = document.getElementById("summary-box-display");
    span.classList.add("d-none");
    const txt = document.getElementById("image-description");
    txt.classList.remove("d-none");
    txt.dispatchEvent(new Event("input", { bubbles: true }));
}

async function confEdit(){
    // Need to copy the contents of the text area to data-description
    // Need to call the server to get the markdown version
    // Need to apply the return value to data-display-description
    const txt = document.getElementById("image-description").value;

    let response;
    try {
        response = await getFormattedText(txt);
    } catch (err) {
        logger.error("Error getting formatted text:", err);
        handleAjaxError(err, "Formatting Description");
    } finally {
        if (response && response.success) {
            logger.log("Text received successfully");
            process_edit(txt, response.text);
        }
    }
}

function process_edit(unf_txt, f_txt) {

    const summaryBox=document.getElementById("summary-box");
    summaryBox.dataset.displayDescription = f_txt;
    summaryBox.dataset.description = unf_txt;
    const span = document.getElementById("summary-box-display");
    span.innerHTML=f_txt;

    // Need to reset the buttons
    const edit = document.getElementById("edit-desc");
    edit.classList.remove("d-none");
    const ok = document.getElementById("edit-ok");
    ok.classList.add("d-none");
    const cancel=document.getElementById("edit-cancel");
    cancel.classList.add("d-none");
    // Need to swap text area and span
    span.classList.remove("d-none");
    const txt = document.getElementById("image-description");
    txt.classList.add("d-none") 
    
}

function cancelEdit(){
    
    // Need to reset the text area to data-description
    const edit = document.getElementById("edit-desc");
    edit.classList.remove("d-none");
    const ok = document.getElementById("edit-ok");
    ok.classList.add("d-none");
    const cancel=document.getElementById("edit-cancel");
    cancel.classList.add("d-none");
    // Need to swap text area and span
    const summaryBox=document.getElementById("summary-box");
    const displayDesc=summaryBox.dataset.displayDescription;
    const imageDesc=summaryBox.dataset.description;
    
    const span = document.getElementById("summary-box-display");
    span.classList.remove("d-none");
    const txt = document.getElementById("image-description");
    txt.value=imageDesc;
    txt.classList.add("d-none");
}