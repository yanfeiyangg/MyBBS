"""MyBBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from MyBBS import settings
from django.views.static import serve
from app01 import views

urlpatterns = [
    # 配置admin
    url(r'^admin/', admin.site.urls),
    # 配置media，存放用户的下载文件
    url(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),
    #

    url(r'^login/', views.login),
    url(r'^reg/', views.reg),
    url(r'^logout/', views.logout),
    url(r'^get_vaild_img/', views.get_vaild_img),
    # 加入 position 和 parameter ，用于首页筛选所有文章
    url(r'^index/(?P<position>cate|tag|date)/(?P<parameter>[\w\W]+)/', views.index),
    url(r'^$', views.index),
    url(r'^index/$', views.index),

    # 上传图片
    url(r'^upload/', views.upload),

    # 发送验证码到邮箱
    url(r'^send_codes/', views.sendVaildEmail),
    # app01
    url(r'^blog/', include("app01.urls"))
]
