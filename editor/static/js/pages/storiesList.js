import { showFlashMessage } from "../ui/flashMessages.js";
import { showBootstrapConfirm, showNotifyModal, deleteClicked } from "../ui/modals.js";
import { handleAjaxError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import { delStory, prtStory } from "../api/listsAPI.js";

document.querySelectorAll('.delete-button').forEach(button => {
  button.addEventListener('click', event => {
    var id = button.dataset.id;
    const row = button.closest("tr");
    const title = row?.cells[2]?.textContent.trim();
    deleteClicked(id, deleteStory, title);
  });
});

//
// Add print functionality to print button
//
document.querySelectorAll('.print-button').forEach(button => {
  button.addEventListener('click', event => {
    var id = button.dataset.id;
    printClicked(id);
  });
});

async function deleteStory(id) {

  let response;
  try {
    response = await delStory(id);
  }
  catch (err) {
    handleAjaxError(err, "Delete Story");
  } finally {
    if (response && response.success){
      const table = document.getElementById("storiesTable");
      var i = table.querySelector('tr[data-id="' + id + '"]').rowIndex;
      table.deleteRow(i);
      if (response.messages) {
        response.messages.forEach(([category, message]) => {
        showFlashMessage(category, message);
      });
      }
      logger.log("Story deleted successfully!");
    }
  }
};  
//
// Catch the user pressing print
//
function printClicked(id) {

  const table = document.getElementById("storiesTable");
  const row = table.querySelector('tr[data-id="' + id + '"]');
  const title = row.cells[2].textContent.trim();
  showBootstrapConfirm((confirmed, opts) => {
    if (confirmed) {
      printStory(id, title);
    }
    else {
      logger.log("Print Cancelled.");
    };
  }, {
    mode: 'print',
    title: title
  });
};
//
// Process print story
//
async function printStory(story_id, story_title) {
  let response;
  try {
    response = await prtStory(story_id, story_title);

    const url = window.URL.createObjectURL(response.blob);
    const a = document.createElement("a");
    a.href = url;

    a.download = response.filename;

    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    showNotifyModal("File created in Download folder", "Success");
  }
  catch (err) {
    logger.error("Error occurred while printing story");
    logger.error(err);
    showNotifyModal(
      `Server error printing story: ${err}`,
      "Error"
      );
  }
} 
