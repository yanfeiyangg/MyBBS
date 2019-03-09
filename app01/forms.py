# form表单
from django import forms
from django.forms import widgets

from django.core.exceptions import ValidationError
from app01 import models

# Redis
from MyBBS.settings import REDIS


# 注册验证表单
class regForm(forms.Form):
    username = forms.CharField(
        min_length=5,
        label='用户名',
        widget=widgets.TextInput(attrs={"class": "form-control", "placeholder": "请输入用户名"}),
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户名长度必须超过6位",
        }
    )
    pwd = forms.CharField(
        min_length=8,
        label='密码',
        widget=widgets.PasswordInput(attrs={"class": "form-control", "placeholder": "至少8位，必须包括字母、数字、特殊字符"}),
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码长度必须超过8位",
        }
    )
    re_pwd = forms.CharField(
        min_length=8,
        label='确认密码',
        widget=widgets.PasswordInput(attrs={"class": "form-control", "placeholder": "请输入确认密码"}),
        error_messages={
            "required": "确认密码不能为空",
            "min_length": "确认密码长度必须超过8位",
        }
    )
    email = forms.EmailField(
        label='邮箱',
        widget=widgets.EmailInput(attrs={"class": "form-control", "placeholder": "请输入邮箱"}),
        error_messages={
            "required": "邮箱不能为空",
            "invalid": "邮箱格式错误"
        }
    )
    code = forms.CharField(
        label='邮箱验证码',
        widget=widgets.TextInput(attrs={"class": "form-control", "placeholder": "请输入邮箱验证码"}),
        error_messages={
            "required": "验证码不能为空",
        }
    )

    # 局部钩子函数，对某个字段自定义判断
    # 读取数据库，判断注册用户名是否已存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = models.UserInfo.objects.filter(username=username).first()
        if user:
            raise ValidationError("用户名已存在")
        else:
            return username

    # 读取数据库，判断邮箱是否已注册过
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user = models.UserInfo.objects.filter(email=email).first()
        if user:
            raise ValidationError("邮箱已注册过！")
        else:
            return email

    # 检查验证码是否正确
    def clean_code(self):
        code = self.cleaned_data.get('code')
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        key = "register:{0}:{1}".format(username, email)
        vaild_code = REDIS.get(key)
        if vaild_code:
            print("输入的注册验证码：",code)
            print("正确的注册验证码：",vaild_code)
            print("验证码比较结果：",vaild_code.upper() == code.upper())
        if vaild_code and vaild_code.upper() == code.upper():
            # 删除Redis缓存的验证码
            REDIS.delete(key)
            return code
        else:
            raise ValidationError('验证码错误')

    # 全局钩子函数，可以获得所有clean_data，并且进行判断两次密码是否正确
    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        if pwd == re_pwd:
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不正确")
