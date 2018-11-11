$(".deleteBtn").click(function () {
            var article_id = $(this)[0].getAttribute("article_id");
            swal({
                    title: "确定删除吗？",
                    text: "你将无法恢复该文章！",
                    type: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#DD6B55",
                    confirmButtonText: "确定删除！",
                    cancelButtonText: "取消删除！",
                    closeOnConfirm: false,
                    closeOnCancel: false
                },
                function (isConfirm) {
                    if (isConfirm) {
                        $.ajax({
                            method: "get",
                            url: "delete_article/" + article_id,
                            dataType: "json",
                            success: function (data) {
                                if (data["status"] == "0") {
                                    swal({
                                            title: "删除！",
                                            text: "文章已经被删除。",
                                            type: "success"
                                        },
                                        function () {
                                            location.reload();
                                        });

                                } else {
                                    swal("失败！", "删除操作异常，失败！", "error");
                                }
                            }
                        });
                    } else {
                        swal("取消！", "删除操作已撤回", "error");
                    }
                });
        })