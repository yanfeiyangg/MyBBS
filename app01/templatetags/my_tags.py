from django import template
from app01 import models
from django.db.models import Avg, Count
from MyBBS.settings import REDIS
register = template.Library()


@register.inclusion_tag("menu.html")
def get_menu(username):
    # 通过username找到对应的user对象
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


@register.filter
def getView(article_id):
    s = "visit:%s:totals" % article_id
    return REDIS.get(s)