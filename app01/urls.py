from django.conf.urls import url
from django.contrib import admin
from MyBBS import settings
from django.views.static import serve
from app01 import views

urlpatterns = [
    # 添加文章
    url(r'backend/add_article/', views.add_article),
    # 删除文章
    url(r'backend/delete_article/(?P<article_id>\d+)$', views.delete_article),
    # 编辑文章
    url(r'backend/edit_article/(?P<article_id>\d+)$', views.edit_article),
    # 文章后台管理
    url(r'backend/', views.backend),
    # 点赞
    url(r'poll/', views.poll),
    # 评论
    url(r'comment/', views.comment),
    # 文章详细页路由
    url(r'(?P<username>\w+)/articles/(?P<article_id>\w+)/', views.article_detail),
    # 分类、标签路由
    url(r'(?P<username>\w+)/(?P<position>cate|tag|date)/(?P<parameter>[\w\W]+)/$', views.homesite),
    # 个人主页首页
    url(r'(?P<username>\w+)/$', views.homesite),
]