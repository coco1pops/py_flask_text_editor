//
// Used to delete all post table rows after the row passed as a parameter
//  
function deleteNextRows(row) {
    let current = row;

    while (current) {
        const next = current.nextElementSibling;
        current.remove();
        current = next;
    };
};
//
// Builds the post table on the tbody passed as a parameter using 
// the posts structure as input. It has replaced the build using jinja
// Adds records to the tbody
//
function addNewRows(tbody, posts) {
    posts.forEach((post, index)=> {
    const is_last = index == posts.length - 1;
    const row = tbody.insertRow();
    row.id=`row_${post.post_id}`
    var secondCell="";
    var imgHTML="";
    var btnHTML="";
    const firstCell = `
        <td class = "hide">${post.part_type == "text" ? "None" : post.post_id }</td>
        `;
    if (post.part_type == "text"){
        imgHTML="";
        if (post.image_mime_type != ""){
            imgHTML=`<div class="col-auto">
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
        secondCell= `
            <div id="message_${post.post_id}"
                    class="${post.creator == 'model' ? 'model' : 'user'} border-top border-secondary" data-markdown="${escapeHtmlAttr(post.message_md)}" 
                        data-html="${escapeHtmlAttr(post.message)}">
                    ${post.message}
                </div>
                <div class="row" align-items-center>`;
        
        edit_buttons = addRowButtons(post.post_id, post.creator);
        extra_buttons = "";
        if (post.creator=="user") {
            extra_buttons = `
            <button class='btn btn-primary d-none row-button' type="button" id="delete_${post.post_id}"
                onclick="deleteEditRow(this, 'Edit Prompt')">Delete</button>
            `;
        }
        if (post.creator=="user" || (post.creator=="model" && is_last)) {
            btnHTML = `
                    <div class="col-6 d-flex justify-content-start gap-2" id="buttons_${post.post_id}">
                ` + edit_buttons + extra_buttons + `</div>`;
        }
        else {
            btnHTML= `<div class="col-6 dflex" id="buttons_${post.post_id}"></div>`;
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
//
// Populates standard buttons on a table row. After a delete, adds buttons to the previous (model) row to allow edit
// Returns html 
//
function addRowButtons(post_id, creator){
    html= `             
        <button class='btn btn-primary actions' type="button" id="${post_id}"
            onclick="editRow(this, '${creator=='user' ? 'Edit Prompt' : 'Edit Response'}')">Edit</button>
        <button class='btn btn-primary d-none row-button' type="button" id="update_${post_id}"
            onclick="updateRow(this, '${creator=='user' ? 'Edit Prompt' : 'Edit Response'}')">Update</button>
        <button class='btn btn-primary d-none row-button' type="button" id="cancel_${post_id}"
            onclick="cancelEditRow(this, '${creator=='user' ? 'Edit Prompt' : 'Edit Response'}')">Cancel</button> 
            `;
    return html;
};
//
// After add, removes the edit response from the previous last element.
// Not needed after update as rows recreated
//
function clearLastRowButtons(tbody) {

    if (!tbody || !tbody.rows.length) return; // No data rows

    const rows = tbody.rows;
    const row = rows[rows.length-1]; // This is the last row. It should always be a 'model' row

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
        console.log ("Error - cannot find target");
    }
}
//
// After delete, adds the standard buttons to the new last (model) post
//
function resetLastRowButtons(){
    tbody=document.getElementById("postsRows");
    if (!tbody.rows.length) return; // No data rows

    const rows = tbody.rows;
    const row = rows[rows.length-1]; // This is the last row. It should always be a 'model' row

    const id = row.cells[0].textContent;
    const message_id = "message_" + id;
    if (!document.getElementById(message_id).classList.contains("model")) {
        console.log("Error - invalid table format");
        return false
    };

    const sel = "buttons_" + id;
    const target_div = document.getElementById(sel);

    html=addRowButtons(id,"model");
    target_div.innerHTML = html;

};
//
// Used to create and display a container with a character and the associated text. Returns html
//
function buildChar(id, mime_type, img, text) {
    // 1. Create the container

    var outHTML= `
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
                        <button class="btn btn-secondary" type="button" id="clear_${id}" onclick="processClearChar(event)">Clear</button>
                    </div>
                </div>
            </div>
        </div>`;

    return outHTML;
};
//
// Used to display flash messages
//
function showMessages(messages){
    if (messages) {
        messages.forEach(([category, message]) => {
            showFlashMessage(category, message);
        });      
    };
}