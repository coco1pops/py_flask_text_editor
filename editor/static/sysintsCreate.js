$(".entry-textarea").on("input change", function () {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
});

$(document).ready(function () {
    $(".entry-textarea").trigger("input");
});