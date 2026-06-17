  import { deleteClicked } from '../ui/modals.js';
  import { deleteSysInt} from '../api/paramsAPI.js';
  import {logger, config} from '../utils/logger.js';
  import {handleAjaxError} from '../utils/errors.js';
  import {showFlashMessage} from '../ui/flashMessages.js';

  document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', event => {
      var id = button.dataset.id;
      const row = button.closest("tr");
      const title = row?.cells[1]?.textContent.trim();
      deleteClicked(id, delSysint, title);
    });
  });

  export async function delSysint(id) {
    let response;

    try {
        response = await deleteSysInt(id);

    } catch (err) {
        handleAjaxError(err, "Delete System Instruction");
    } finally {
        if (response && response.messages) {
        logger.log(response.messages[0][0] + ": " + response.messages[0][1]);
        const table = document.getElementById("sysintTable");
        var i = table.querySelector('tr[data-id="' + id + '"]').rowIndex;
        table.deleteRow(i);
        if (response.messages) {
            response.messages.forEach(([category, message]) => {
                showFlashMessage(category, message);
            });
        }
      }
    }
  }

