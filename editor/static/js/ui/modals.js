import { logger } from "../utils/logger.js";

export function showBootstrapConfirm(callback, options={}) {
  logger.log("Showing confirm modal with options: ", options);
  const modalEl = document.getElementById("confirmModal");
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

  const confirmBtn = document.getElementById('confirmBtn');
  const cancelBtn = document.getElementById('cancelBtn');

  confirmBtn.addEventListener('click', onConfirm);
  cancelBtn.addEventListener('click', onCancel);
  
  const title = document.getElementById('confirmTitle');
  const txt = document.getElementById('confirmText');
  if (options.mode == "print") {
    title.innerHTML = "Confirm Print"
    txt.innerHTML = "Are you sure you want to print " + options.title + "?"
    confirmBtn.classList.toggle('btn-secondary', true);
    confirmBtn.classList.toggle('btn-danger', false);
  }
  else if (options.mode == "complete") {
    title.innerHTML = "Confirm Complete"
    txt.innerHTML = "Are you sure you want to complete " + options.title + " ? This will prevent further edits"
    confirmBtn.classList.toggle('btn-secondary', true);
    confirmBtn.classList.toggle('btn-danger', false);  
  }
  else {
    title.innerHTML = "Confirm Delete"
    txt.innerHTML = "Are you sure you want to delete " + options.title + "?"
    confirmBtn.classList.toggle('btn-secondary', false);
    confirmBtn.classList.toggle('btn-danger', true);
  }
  modal.show();

  function onConfirm() {
      cleanup();
      modal.hide();
      callback(true);
  }

  function onCancel() {
      cleanup();
      modal.hide();
      callback(false);
  }

  function cleanup() {
      confirmBtn.removeEventListener('click', onConfirm);
      cancelBtn.removeEventListener('click', onCancel);
  }
} 

export function deleteClicked(id, func, title){
  const options={'mode': 'delete', 'title': title}
  showBootstrapConfirm((confirmed) => {
    if (confirmed) {
      logger.log("Confirmed delete "+ id + "!");
      func(id);
    }
    else {logger.log("Delete cancelled.");

    };
  },options
);
};

export function showNotifyModal(message, severity) {  
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

