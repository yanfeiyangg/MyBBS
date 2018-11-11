# form表单
from django import forms
from django.forms import widgets

from django.core.exceptions import ValidationError
from app01 import models
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
            "required": "确认密码不能为空",
            "invalid": "邮箱格式错误"
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

    # 全局钩子函数，可以获得所有clean_data，并且进行判断两次密码是否正确
    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        if pwd == re_pwd:
            return self.cleaned_data
        else:
            raise ValidationError("两次密码不正确")