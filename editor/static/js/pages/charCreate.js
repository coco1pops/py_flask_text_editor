const urlParams = new URLSearchParams(window.location.search);
const char_id = urlParams.get('char_id');

const input = document.getElementById('imageUpload');
const fileName = document.getElementById('fileName');
const currentImage = document.getElementById('currentImage');


input.addEventListener('change', () => {
    fileName.textContent = input.files[0]?.name || 'No file chosen';
    if (input.files[0].name) {
        const formData = new FormData();
        formData.append("file", input.files[0]);  // input is your file input

        $.ajax({
            url: "/checkimage",
            type: "post",
            data: formData,
            processData: false,
            contentType: false
        }
        ).done(function (response) {
            const file = input.files[0];
            const reader = new FileReader();
            reader.onload = function (e) {
                currentImage.src = '';
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file)
        }
        ).fail(function (xhr, status, error) {
            fileName.textContent = 'No file chosen';
            input.value = ''
            if (xhr.status == "413") {
                showNotifyModal("File too large", "Error");
            }
            else {
                showNotifyModal("Invalid file type", "Error");
            };
        }
        );
    }
});

$(".entry-textarea").on("input change", function () {
    this.style.height = "auto";
    this.style.height = (this.scrollHeight) + "px";
});

$(document).ready(function () {
    $(".entry-textarea").trigger("input");
});
