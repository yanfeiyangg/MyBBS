# celery任务
from __future__ import absolute_import
from MyBBS.celery import app
from django.core.mail import send_mail


@app.task
def send_email(title,msg,to_user):
    send_mail(
        title,  # 邮件标题，
        msg,  # 邮件内容
        "724028892@qq.com",  # 发件箱
        [to_user],  # 收件箱列表(可以发送给多个人)
        fail_silently=False  # 失败静默(若发送失败，报错提示我们)
    )
