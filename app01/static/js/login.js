$('#btn_submit').on('click', function () {
    $.ajax({
        url: '/login/',
        type: 'post',
        dataType: 'json',
        data: {
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
            "username": $('#username').val(),
            "pwd": $('#pwd').val(),
            "code": $('#code').val()
        },
        success: function (data) {
            if (data.state) {
                location.href = '/'
            } else {
                $('#error').text(data.msg);
            }
        }
    })
});
$('#code11').on('click', function () {
    $(this)[0].src += '?';
});