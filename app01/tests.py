from django.test import TestCase
from MyBBS.settings import REDIS


# Create your tests here.
# 对“新文章”初始化浏览数为0
def initView(article_id):
    s = "visit:%s:totals" % article_id
    REDIS.set(s, 0)


# 浏览数 + 1
def addView(article_id):
    s = "visit:%s:totals" % article_id
    REDIS.incr(s)


# 删除文章的同时，删除点击数
def delView(article_id):
    s = "visit:%s:totals" % article_id
    REDIS.delete(s)

# 获取文章点击数
def getView(article_id):
    s = "visit:%s:totals" % article_id
    return REDIS.get(s)


if __name__ == '__main__':
    res = getView(5)
    print(res)
