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
$("#username").blur(function () {
    $username = $("#username")[0].value;
    $.ajax({
        url:'/getAvatar/',
        type:'get',
        dataType:'json',
        data:{
            'username':$username
        },
        success:function (data) {
            console.log(data);
            $("#img_label")[0].src = "/media/"+data["data"];
        }

    })
});