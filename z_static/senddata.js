function sendData() {
    var value = document.getElementById('input').value;
    $.ajax({
        url: '/process',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ 'value': value }),
        success: function (response) {
            document.getElementById('output').innerHTML = response.result;
        },
        error: function (error) {
            console.log(error);
        }
    });
}