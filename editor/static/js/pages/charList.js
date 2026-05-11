  document.querySelectorAll('.delete-button').forEach(button => {
    button.addEventListener('click', event => {
      var id = button.dataset.id;
      const row = button.closest("tr");
      const title = row?.cells[1]?.textContent.trim();
      deleteClicked(id, deleteChar, title);
    });
  });

  function deleteChar(id) {
    $.ajax({
      url: "/deletechar",
      type: "post",
      data: { 'char_id': id },
      dataType: 'json'
    }
    ).done(function (response) {
      console.log(response);
 
      if (response.success) {
        const table = document.getElementById("charTable");
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
