//
// Common UI Functions
//
function showFlashMessage(category, message) {
      const alertClass = {
      success: "alert-success",
      error: "alert-danger",
      warning: "alert-warning",
      info: "alert-info"
      }[category] || "alert-secondary";

      const alert = `<div class="alert ${alertClass}" role="alert">${category} - ${message}</div>`;
      $("#flash-container").html(alert);  // Or append if you want multiple
    };

  function clearFlashMessage(){
    $("#flash-container").html("");
  }

function showBootstrapConfirm(callback, options={}) {
  const modal = new bootstrap.Modal(document.getElementById("confirmModal"));
  const button = document.getElementById('confirmBtn');
  const title = document.getElementById('confirmTitle');
  const txt = document.getElementById('confirmText');
  if (options.mode == "print") {
    title.innerHTML = "Confirm Print"
    txt.innerHTML = "Are you sure you want to print " + options.title + "?"
    button.classList.toggle('btn-secondary', true);
    button.classList.toggle('btn-danger', false);
  }
  else {
    title.innerHTML = "Confirm Delete"
    txt.innerHTML = "Are you sure you want to delete " + options.title + "?"
    button.classList.toggle('btn-secondary', false);
    button.classList.toggle('btn-danger', true);
  }
  modal.show();

  // Remove previous handlers to avoid stacking
  $('#confirmBtn').off('click').on('click', function () {
    $('#confirmModal').modal('hide');
    callback(true);
  });

  $('#cancelBtn').off('click').on('click', function () {
    $('#confirmModal').modal('hide');
    callback(false);
  });
} 

function deleteClicked(id, func, title){
  const options={'mode': 'delete', 'title': title}
  showBootstrapConfirm((confirmed) => {
    if (confirmed) {
      console.log("Confirmed delete "+ id + "!");
      func(id);
    }
    else {console.log ("Delete cancelled.");

    };
  },options
);
};

function showNotifyModal(message, severity) {  
  const modal = new bootstrap.Modal(document.getElementById('Notify'));

  document.querySelector('#Notify .modal-body').textContent = message;
  const modalTitle = document.getElementById('myModalLabel');
  modalTitle.textContent = severity;

  const modalColour = document.getElementById('myModalHeader');
  const modalBorder = document.getElementById('myModalBorder');
  if (severity == "Error") {
    modalColour.classList.toggle("bg-danger", true);
    modalColour.classList.toggle("bg-success", false);
    modalBorder.classList.toggle("border-danger", true);
    modalBorder.classList.toggle("border-success", false);
  }
  else {
    modalColour.classList.toggle("bg-danger", false);
    modalColour.classList.toggle("bg-success", true);
    modalBorder.classList.toggle("border-danger", false);
    modalBorder.classList.toggle("border-success", true);
  };
  modal.show();
}
//
// Utilities
//
function formatDate(rawdate) {
  console.log(rawdate);
  const date = new Date(rawdate);

  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  const month = months[date.getMonth()];
  const day = String(date.getDate()).padStart(2, '0');
  const year = date.getFullYear();

  let hour = date.getHours();
  const minute = String(date.getMinutes()).padStart(2, '0');
  const ampm = hour >= 12 ? 'PM' : 'AM';

  hour = hour % 12;
  hour = hour === 0 ? 12 : hour;
  const hourStr = String(hour).padStart(2, '0');

  return `${month} ${day}, ${year} at ${hourStr}:${minute}${ampm}`;
};

function normalizeQuotes(str) {
  return str
  .replace(/[\u201C\u201D]/g, '"')  // Replace curly double quotes
  .replace(/[\u2018\u2019]/g, "'"); // Replace curly single quotes
};

function escapeHtmlAttr(str) {
  return normalizeQuotes(str)
  .replace(/&/g, '&amp;')   // Must go first!
  .replace(/"/g, '&quot;')  // Escape double quotes
  .replace(/'/g, '&#39;')   // Escape single quotes
  .replace(/</g, '&lt;')    // Optional: escape <
  .replace(/>/g, '&gt;');   // Optional: escape >
};