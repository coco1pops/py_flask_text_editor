import {logger} from "../utils/logger.js";

export function buildClearLastRowButtons(tbody) {

    if (!tbody || !tbody.rows.length) return; // No data rows

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

    if (target_div) {
        target_div.innerHTML = ''; // Clear the div's content
    }
    else {
        logger.error("Error - cannot find target");
    }
}

export function buildDeleteNextRows(row) {
    let current = row;

    while (current) {
        const next = current.nextElementSibling;
        current.remove();
        current = next;
    };
};

export function buildAddChar(id, mime_type, img, text) {
    const outHTML = buildChar(id, mime_type, img, text);
    let target = document.getElementById("placeholder");
    target.innerHTML += outHTML;

    document.getElementById("charSelect").value="";
    document.getElementById("charDropdown").innerText="-- Select a character --";
    const modal = bootstrap.Modal.getInstance(document.getElementById('charPicker'));
    modal.hide();
};
// TODO: Replace with a server-side render of the char block
function buildChar(id, mime_type, img, text) {
    // 1. Create the container

    let outHTML = `
        <div id="Container_${id}" class="row border p-3 mb-3 align-items-start characters">
            `;
    // 2. Create the image
    if (mime_type != "") {
        outHTML += `
            <div class="col-auto">
                <img src=${img} alt="Preview" style="width: 200px; class="img-fluid">
            </div>` ;
    }

    // 3. Create the text
    outHTML += `
            <div class="col">
                <div class="d-flex flex-column h-100 justify-content-between">
                    <p class="mt-2 text-muted">${text}</p>
                    <div class="text-end">
                        <button class="btn btn-secondary clear-char" type="button" data-id="${id}" id="clear_${id}">Clear</button>
                    </div>
                </div>
            </div>
        </div>`;

    return outHTML;
};

export function buildRemoveChar(id) {
        const contdel = "Container_" + id;
        document.getElementById(contdel).remove();
}