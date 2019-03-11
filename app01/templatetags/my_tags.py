from django import template
from app01 import models
from django.db.models import Avg, Count
from app01.views import v

register = template.Library()


@register.inclusion_tag("menu.html")
def get_menu(username=None):
    if username == None:
        # ************   获取所有标签、分类、日期归档等 *********************
        # 找到博客下的所有分类以及对应的文章数量
        cate_list = models.Category.objects.all().annotate(count=Count("article")).values_list("title", "count")
        # 找到博客下的所有标签以及对应的文章数量
        tag_list = models.Tag.objects.all().annotate(count=Count("article")).values_list("title", "count")
        # 日期归档
        date_list = models.Article.objects.all().extra(
            select={"create_ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values("create_ym").annotate(
            count=Count("*")).values_list("create_ym", "count")
    else:
        # 通过username找到对应的user对象
        print(username)
        user = models.UserInfo.objects.filter(username=username).first()
        # 通过一对一关系，找到user对象的博客
        blog = user.blog
        # 找到博客下的所有分类以及对应的文章数量
        cate_list = models.Category.objects.filter(blog=blog).annotate(count=Count("article")).values_list("title",
                                                                                                           "count")  # 找到博客下的所有分类以及对应的文章数量
        # 找到博客下的所有标签以及对应的文章数量
        tag_list = models.Tag.objects.filter(blog=blog).annotate(count=Count("article")).values_list("title", "count")
        # 日期归档
        date_list = models.Article.objects.filter(user=user).extra(
            select={"create_ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values("create_ym").annotate(
            count=Count("*")).values_list("create_ym", "count")
    return locals()


@register.inclusion_tag("top10.html")
def get_top10():
    '''获取点击量前10的“文章id”以及“点击量”'''
    data_list = v.getTop10View()
    return locals()


@register.filter
def getView(article_id):
    '''通过文章id，查看该文章的点击数'''
    return v.getView(article_id)


@register.filter
def getArticleTitle(id):
    '''通过文章id，获取文章的标题'''
    return models.Article.objects.filter(pk=id).first().title


@register.filter
def getArticleUsername(id):
    '''通过文章id，获取文章的标题'''
    return models.Article.objects.filter(pk=id).values_list("user__username")[0][0]
