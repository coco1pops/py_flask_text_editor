import "../ui/textarearesize.js";
import { getImageUploadURL } from "../api/paramsAPI.js";
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
                handleAjaxError({err, context: "Upload Image"});
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