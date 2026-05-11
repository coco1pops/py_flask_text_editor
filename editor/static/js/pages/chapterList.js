document.querySelectorAll('.delete-button').forEach(button => {
  button.addEventListener('click', event => {
    var id = button.dataset.id;
    const row = button.closest("tr");
    const title = row?.cells[2]?.textContent.trim();
    deleteClicked(id, deleteChapter, title);
  });
});

function deleteChapter(id) {
  story_id=document.getElementById("form-data").dataset.storyId;
  let response;
  $.ajax({
    url: "/delete_chapter",
    type: "post",
    data: { 'story_id': id, 'chapter_id' : id },
    dataType: 'json'
  }
  ).done(function (response) {
    console.log(response);
    if (response.success){
      const table = document.getElementById("chaptersTable");
      var i = table.querySelector('tr[data-id="' + id + '"]').rowIndex;
      table.deleteRow(i);
    }

    if (response.messages) {
      response.messages.forEach(([category, message]) => {
      showFlashMessage(category, message);
      });
    }

  }).fail(function (error) {
    console.log(error);
  })
};
//
// Add print functionality to print button
//
document.querySelectorAll('.print-button').forEach(button => {
  button.addEventListener('click', event => {
    var id = button.dataset.id;
    printClicked(id);
  });
});
//
// Catch the user pressing print
//
function printClicked(id) {

  story_id=document.getElementById("form-data").dataset.storyId;
  story_title=document.getElementById("form-data").dataset.storyTitle;

  const table = document.getElementById("chaptersTable");
  const row = table.querySelector('tr[data-id="' + id + '"]');
  const title = row.cells[2].textContent.trim();
  showBootstrapConfirm((confirmed, opts) => {
    if (confirmed) {
      printChapter(story_id, id, story_title);
    }
    else {
      console.log("Print Cancelled.");
    };
  }, {
    mode: 'print',
    title: story_title + " " + title
  });
};
//
// Process print story
//
function printChapter(story_id ,id, story_title) {
  $.ajax({
    url: "/print_chapter",
    type: "post",
    data: { 'story_id': story_id, 'chapter_id' : id},
    xhrFields: {
      responseType: 'blob'  // Expect binary data
    }
  }).done(function (blob, status, xhr) {
      if (xhr.status !== 200) {
        // Try to read error text from blob
        const reader = new FileReader();
        reader.onload = function () {
          console.error("Server error:", reader.result);
          showNotifyModal("Server error: " + reader.result, "Error");
        };
        reader.readAsText(blob);
        return;
    }
    // Create a temporary URL for the blob
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    const table = document.getElementById("chaptersTable");
    const title = table.querySelector('tr[data-id="' + id + '"]').cells[2].textContent.trim();
    a.download = title + ".docx";

    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);  // Clean up
    showNotifyModal("File created in Download folder", "Success");

  }).fail(function (jqXHR, textStatus, errorThrown) {
    showNotifyModal("Print - Something went wrong: " + errorThrown, "Error");
    console.log("AJAX Error", textStatus, errorThrown);
  });

}
