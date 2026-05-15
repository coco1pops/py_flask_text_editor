export function buildClearLastRowButtons(tbody) {

    if (!tbody || !tbody.rows.length) return; // No data rows

    const rows = tbody.rows;
    const row = rows[rows.length - 1]; // This is the last row. It should always be a 'model' row

    const id = row.cells[0].textContent;
    const message_id = "message_" + id;
    if (!document.getElementById(message_id).classList.contains("model")) {
        console.log("Error - invalid table format");
        return false
    };

    const sel = "buttons_" + id;
    const target_div = document.getElementById(sel);

    if (target_div) {
        target_div.innerHTML = ''; // Clear the div's content
    }
    else {
        console.log("Error - cannot find target");
    }
}

//
// Builds the post table on the tbody passed as a parameter using 
// the posts structure as input. It has replaced the build using jinja
// Adds records to the tbody
//
export function buildAddNewRows(tbody, posts) {
    posts.forEach((post, index) => {
        const is_last = index == posts.length - 1;
        const row = tbody.insertRow();
        row.id = `row_${post.post_id}`
        let secondCell = "";
        let imgHTML = "";
        let btnHTML = "";
        const firstCell = `
        <td class = "hide">${post.part_type == "text" ? "None" : post.post_id}</td>
        `;
        if (post.part_type == "text") {
            imgHTML = "";
            if (post.image_mime_type != "") {
                imgHTML = `<div class="col-auto">
                        <img src="${post.image_data}" class="img-fluid"
                        style="max-width:300px; vertical-align: middle;" />
                    </div>`
            };
            secondCell = `
                <div class="row border p-3 mb-3 align-items-start">` + imgHTML +
                `<div class="col d-flex flex-column h-100 justify-content-between" data-markdown="${escapeHtmlAttr(post.message_md)}" data-html="${escapeHtmlAttr(post.message)}">
                    ${post.message}
                </div>
            </div>
            `;
        }
        else {
            secondCell = `
            <div id="message_${post.post_id}"
                    class="${post.creator == 'model' ? 'model' : 'user'} border-top border-secondary" data-markdown="${escapeHtmlAttr(post.message_md)}" 
                        data-html="${escapeHtmlAttr(post.message)}">
                    ${post.message}
                </div>
                <div class="row" align-items-center>`;

            let edit_buttons = buildAddRowButtons(post.post_id, post.creator);
            let extra_buttons = "";
            if (post.creator == "user") {
                extra_buttons = `
            <button class='btn btn-primary d-none row-button delete-button' type="button" id="delete_${post.post_id}">Delete</button>
            `;
            }
            if (post.creator == "user" || (post.creator == "model" && is_last)) {
                btnHTML = `
                    <div class="col-6 d-flex justify-content-start gap-2" id="buttons_${post.post_id}">
                ` + edit_buttons + extra_buttons + `</div>`;
            }
            else {
                btnHTML = `<div class="col-6 dflex" id="buttons_${post.post_id}"></div>`;
            };

            secondCell = secondCell + btnHTML + `
            <div class="col-2 dflex"> </div>

            <div class="col-4 d-flex justify-content-end align-items-center gap-2">
                <div id="loadingSpinner_${post.post_id}" class="spinner-border text-primary" role="status" style="display: none;">
                    <span class="visually-hidden">Loading...</span>
                </div>

            <span class="created">Created ${formatDate(post.created)}</span>
        </div>`;
        }
        row.innerHTML = firstCell + "<td>" + secondCell + "</td>";
    })
};
function buildAddRowButtons(post_id, creator) {
    const html = `             
        <button class='btn btn-primary actions edit-button' type="button" 
        data-id="${post_id}" data-mode="${creator == 'user' ? 'Edit Prompt' : 'Edit Response'}" id="edit_${post_id}">
            Edit</button>
        <button class='btn btn-primary d-none row-button update-button' type="button" 
            data-id="${post_id}" data-mode="${creator == 'user' ? 'Edit Prompt' : 'Edit Response'}" id="update_${post_id}">Update</button>
        <button class='btn btn-primary d-none row-button cancel-button' type="button" 
            data-id="${post_id}" data-mode="${creator == 'user' ? 'Edit Prompt' : 'Edit Response'}" id="cancel_${post_id}">Cancel</button>
            `;
    return html;
};

export function buildDeleteNextRows(row) {
    let current = row;

    while (current) {
        const next = current.nextElementSibling;
        current.remove();
        current = next;
    };
};

export function buildResetLastRowButtons() {
    const tbody = document.getElementById("postsRows");
    if (!tbody.rows.length) return; // No data rows

    const rows = tbody.rows;
    const row = rows[rows.length - 1]; // This is the last row. It should always be a 'model' row

    const id = row.cells[0].textContent;
    const message_id = "message_" + id;
    if (!document.getElementById(message_id).classList.contains("model")) {
        console.log("Error - invalid table format");
        return false
    };

    const sel = "buttons_" + id;
    const target_div = document.getElementById(sel);

    let html = buildAddRowButtons(id, "model");
    target_div.innerHTML = html;

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