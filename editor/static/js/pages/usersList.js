  import { deleteClicked } from "../ui/modals.js";
  import { showFlashMessage } from "../ui/flashMessages.js";
  import { logger } from "../utils/logger.js";
  import { deleteUser } from "../api/paramsAPI.js";
  import { handleAjaxError } from "../utils/errors.js";
  
  document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', event => {
      var id = button.dataset.id;
      const row = button.closest("tr");
      const title = row?.cells[1]?.textContent.trim();
      deleteClicked(id, delUser, title);
    });
  });

   export async function delUser(id) {
    let response;
    try {
      response = await deleteUser(id);
  
    } catch (err) {
        handleAjaxError(err, "Delete User");
  
    } finally {
      if (response && response.success) {
        logger.log(response.messages[0][0] + ": " + response.messages[0][1]);
        const table = document.getElementById("userTable");
        var i = table.querySelector('tr[data-id="' + id + '"]').rowIndex;
        table.deleteRow(i);
        if (response?.messages) {
          response.messages.forEach(([category, message]) => {
            showFlashMessage(category, message);
          });
        }
      }
    }
   }