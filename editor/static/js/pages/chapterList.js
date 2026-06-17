import { showFlashMessage } from "../ui/flashMessages.js";
import { showBootstrapConfirm, showNotifyModal, deleteClicked } from "../ui/modals.js";
import { handleAjaxError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";
import { delChapter, prtChapter } from "../api/listsAPI.js";

document.querySelectorAll('.delete-button').forEach(button => {
  button.addEventListener('click', event => {
    var id = button.dataset.id;
    const row = button.closest("tr");
    const title = row?.cells[2]?.textContent.trim();
    deleteClicked(id, deleteChapter, title);
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

async function deleteChapter(id) {
  const story_id=document.getElementById("form-data").dataset.storyId;
  let response;
  try {
    response = await delChapter(story_id, id );
  }
  catch (err) {
    handleAjaxError(err, "Delete Chapter");
  } finally {
    if (response && response.success){
      logger.log("Chapter deleted successfully!");
      const table = document.getElementById("chaptersTable");
      var i = table.querySelector('tr[data-id="' + id + '"]').rowIndex;
      table.deleteRow(i);
      if (response.messages) {
        response.messages.forEach(([category, message]) => {
          showFlashMessage(category, message);
        });
      }
    }
  }
};
//
// Catch the user pressing print
//
function printClicked(id) {
  logger.log("Print clicked for chapter id " + id);
  const story_id=document.getElementById("form-data").dataset.storyId;
  const story_title=document.getElementById("form-data").dataset.storyTitle;

  const table = document.getElementById("chaptersTable");
  const row = table.querySelector('tr[data-id="' + id + '"]');
  const title = row.cells[2].textContent.trim();
  showBootstrapConfirm((confirmed, opts) => {
    if (confirmed) {
      printChapter(story_id, id, story_title);
    }
    else {
      logger.log("Print Cancelled.");
    };
  }, {
    mode: 'print',
    title: story_title + " " + title
  });
};
//
// Process print chapter
//
async function printChapter(story_id ,id, story_title) {
  let response;
  try {
    response = await prtChapter(story_id, id, story_title);

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
    logger.error("Error occurred while printing chapter");
    logger.error(err);
    showNotifyModal(
      `Server error printing chapter: ${err}`,
      "Error"
      );
  }
} 