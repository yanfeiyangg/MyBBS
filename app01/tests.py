from  MyBBS.settings import REDIS
from app01 import models
# 浏览数 + 1
def addView(article_id):
    s = "visit:%s:totals" % article_id
    # 增加点击量
    REDIS.zincrby("visit_rank",s)

# 删除文章的同时，删除点击数
def delView(article_id):
    s = "visit:%s:totals" % article_id
    REDIS.zrem("visit_rank",s)

# 获取文章点击数
def getView(article_id):
    s = "visit:%s:totals" % article_id
    return REDIS.zscore("visit_rank",s)

# 获取点击排行
def getRankView():
    return REDIS.zrevrange("visit_rank",0,-1)
# 获取文章点击数前10名
def getTop10View():
    lst =  REDIS.zscan("visit_rank")[1][::-1][:10]
    res = [(i[0].split(":")[1],int(i[1])) for i in lst]
    return res

if __name__ == '__main__':
    print(getTop10View())
    # print(REDIS.zscan("visit_rank")[1][::-1])