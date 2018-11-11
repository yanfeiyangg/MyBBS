$("#backend").click(function () {
    if (!"{{ request.user.username }}") {
        location.href = "/login/";
    } else {
        location.href = "/blog/backend/";
    }
})