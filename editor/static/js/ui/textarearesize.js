document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener('input', event => {
        if (event.target.classList.contains('entry-textarea')) {
            event.target.style.height = "auto";
            event.target.style.height = (event.target.scrollHeight) + "px";
        }
    });

    document.querySelectorAll(".entry-textarea")
        .forEach( el => el.dispatchEvent(new Event("input", { bubbles: true })));
})