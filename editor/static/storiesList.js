document.querySelectorAll('.delete-button').forEach(button => {
  button.addEventListener('click', event => {
    var id = button.dataset.id;
    const row = button.closest("tr");
    const title = row?.cells[1]?.textContent.trim();
    deleteClicked(id, deleteStory, title);
  });
});

function deleteStory(id) {
  $.ajax({
    url: "/delete_story",
    type: "post",
    data: { 'story_id': id },
    dataType: 'json'
  }
  ).done(function (response) {
    console.log(response);

    const table = document.getElementById("storiesTable");
    var i = table.querySelector('tr[data-id="' + id + '"]').rowIndex;
    table.deleteRow(i);
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

  const table = document.getElementById("storiesTable");
  const row = table.querySelector('tr[data-id="' + id + '"]');
  const title = row.cells[1].textContent.trim();
  showBootstrapConfirm((confirmed, opts) => {
    if (confirmed) {
      printStory(id);
    }
    else {
      console.log("Print Cancelled.");
    };
  }, {
    mode: 'print',
    title: title
  });
};
//
// Process print story
//
function printStory(id) {
  $.ajax({
    url: "/print_story",
    type: "post",
    data: { 'story_id': id },
    xhrFields: {
      responseType: 'blob'  // Expect binary data
    }
  }).done(function (blob) {
    // Create a temporary URL for the blob
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    const table = document.getElementById("storiesTable");
    const title = table.querySelector('tr[data-id="' + id + '"]').cells[1].textContent.trim();
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
