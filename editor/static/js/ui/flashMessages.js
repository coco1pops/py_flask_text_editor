export function showFlashMessage(category, message) {
      const alertClass = {
      success: "alert-success",
      error: "alert-danger",
      warning: "alert-warning",
      info: "alert-info"
      }[category] || "alert-secondary";

      const alert = `<div class="alert ${alertClass}" role="alert">${category} - ${message}</div>`;
      document.getElementById("flash-container").innerHTML = alert;
    };

  export function clearFlashMessage(){
    document.getElementById("flash-container").innerHTML = "";
  }