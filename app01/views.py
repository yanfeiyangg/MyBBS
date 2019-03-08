from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models import F
from django.db.models import Avg, Count
import json
# 事务
from django.db import transaction
# 画图库
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random
# 用户
from django.contrib import auth
# 数据库models
from app01 import models
# form
from app01 import forms
# 时间函数
import datetime
# 分页
from app01.utils.pagination import Pagination
# redis
from MyBBS.settings import REDIS


# 浏览量对象
class ViewObj:
    # 对“新文章”初始化浏览数为0
    def initView(self, article_id):
        s = "visit:%s:totals" % article_id
        REDIS.set(s, 0)

    # 浏览数 + 1
    def addView(self, request, article_id):
        # 获取IP
        ip = get_ip(request)
        # 判断是否存在访问锁
        lock = self.getViewLock(article_id, ip)
        if not lock:
            s = "visit:%s:totals" % article_id
            # 增加点击量
            REDIS.incr(s)
            # 添加访问锁
            self.addViewLock(article_id, ip)

    # 删除文章的同时，删除点击数
    def delView(self, article_id):
        s = "visit:%s:totals" % article_id
        REDIS.delete(s)

    # 获取文章点击数
    def getView(self, article_id):
        s = "visit:%s:totals" % article_id
        return REDIS.get(s)

    # 添加访问锁，IP在30s内重复访问同一篇文章，只对浏览数+1
    def addViewLock(self, article_id, ip):
        # 加锁
        s = "visit:{0}:lock:{1}".format(article_id, ip)
        print(s)
        REDIS.setex(s, 30, 1)

    # 查看是否存在访问锁
    def getViewLock(self, article_id, ip):
        # 查询锁
        s = "visit:{}:lock:{}".format(article_id, ip)
        lock = REDIS.get(s)
        return lock


# 全局注册 浏览量对象
v = ViewObj()


# 注册
def reg(request):
    if request.is_ajax():
        # 获取表单对象信息
        form = forms.regForm(request.POST)
        res = {"user": None, "errors": None}
        if form.is_valid():
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('pwd')
            email = form.cleaned_data.get('email')
            avatar = request.FILES.get('avatar')
            # avtar的名字不能为中文名
            models.UserInfo.objects.create_user(username=username, password=pwd, email=email, avatar=avatar)
            return JsonResponse(res)
        else:
            print(form.cleaned_data)
            # 错误的数据
            res["errors"] = form.errors
            return JsonResponse(res)
    if request.method == 'GET':
        form = forms.regForm()
        return render(request, 'reg.html', {"form": form})


# 获得验证码
def get_vaild_img(request):
    # 获取随机（x,y,z）数字元组
    def get_random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # 图片背景随机颜色
    img = Image.new('RGB', (140, 32), get_random_color())
    # 画笔对象
    draw = ImageDraw.Draw(img)
    # 字体对象
    font = ImageFont.truetype('app01/static/font/KumoFont.ttf', size=32)
    # 验证码信息
    codes = ''
    # 创建随机验证码图片并且获得验证码字符串codes
    for i in range(5):
        low_letter = chr(random.randint(97, 122))
        up_letter = chr(random.randint(65, 90))
        digit = str(random.randint(0, 9))
        code = random.choice([low_letter, up_letter, digit])
        codes += code
        draw.text((5 + i * 25, 0), code, get_random_color(), font)

    # 保存图片
    f = BytesIO()
    img.save(f, 'png')
    img = f.getvalue()
    # 把验证码信息存入session
    request.session['codes'] = codes
    # 返回图片
    return HttpResponse(img)


# 登陆
def login(request):
    # 如果是ajax请求
    if request.is_ajax():
        # 返回信息
        data = {"state": False, "msg": None}
        # 获得正确验证码
        codes_values = request.session.get('codes', None)
        print("正确的验证码：", codes_values)
        # 获得POST信息
        username = request.POST.get('username', None)
        pwd = request.POST.get('pwd', None)
        code = request.POST.get('code', None)
        print("input:", code)
        # 验证码 校验
        if codes_values.upper() == code.upper():
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 修改state
                data["state"] = True
                # 用户组件 登陆，把用户信息保存至request
                auth.login(request, user)
                # 返回json
                return JsonResponse(data)
            else:
                data["msg"] = "用户名或密码错误"
                return JsonResponse(data)
        else:
            data["msg"] = "验证码错误"
            return JsonResponse(data)
    # GET请求
    if request.method == 'GET':
        return render(request, 'login.html')


# 注销
def logout(request):
    auth.logout(request)
    # request.session.flush()
    return redirect('/')


# 首页
def index(request, **kwargs):
    # ************   获取所有标签、分类、日期归档等 *********************
    # 找到博客下的所有分类以及对应的文章数量
    cate_list = models.Category.objects.all().annotate(count=Count("article")).values_list("title", "count")
    # 找到博客下的所有标签以及对应的文章数量
    tag_list = models.Tag.objects.all().annotate(count=Count("article")).values_list("title", "count")
    # 日期归档
    date_list = models.Article.objects.all().extra(
        select={"create_ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}).values("create_ym").annotate(
        count=Count("*")).values_list("create_ym", "count")

    # *********************************************************************#
    # 获取筛选内容
    pos = kwargs.get('position', None)
    parameter = kwargs.get('parameter', None)
    # 获得文章
    article_list = models.Article.objects.all()
    if not pos:
        article_list = models.Article.objects.all()
    elif pos == 'cate':
        article_list = models.Article.objects.all().filter(category__title=parameter)
    elif pos == 'tag':
        article_list = models.Article.objects.all().filter(tags__title=parameter)
    elif pos == 'date':
        year, month = parameter.split('-')
        dayMax = 30
        months = [1, 3, 5, 7, 8, 10, 12]
        if int(month) in months:
            dayMax = 31
        # article_list = models.Article.objects.filter(user=user).filter(create_time__year=year)
        article_list = models.Article.objects.all().filter(
            create_time__range=(datetime.date(int(year), int(month), 1),
                                datetime.date(int(year), int(month), dayMax)
                                ))
    page = Pagination(request, article_list.count())
    article_list = article_list[page.start:page.end]
    return render(request, "index.html", locals())


# 个人主页
def homesite(request, **kwargs):
    username = kwargs.get('username')
    # 通过username找到对应的user对象
    user = models.UserInfo.objects.filter(username=username).first()
    # 通过博客，找到该博客的所有文章
    pos = kwargs.get('position', None)
    parameter = kwargs.get('parameter', None)
    # 获得文章
    article_list = models.Article.objects.filter(user=user)
    if not pos:
        article_list = models.Article.objects.filter(user=user)
    elif pos == 'cate':
        article_list = models.Article.objects.filter(user=user).filter(category__title=parameter)
    elif pos == 'tag':
        article_list = models.Article.objects.filter(user=user).filter(tags__title=parameter)
    elif pos == 'date':
        year, month = parameter.split('-')
        dayMax = 30
        months = [1, 3, 5, 7, 8, 10, 12]
        if int(month) in months:
            dayMax = 31
        # article_list = models.Article.objects.filter(user=user).filter(create_time__year=year)
        article_list = models.Article.objects.filter(user=user).filter(
            create_time__range=(datetime.date(int(year), int(month), 1),
                                datetime.date(int(year), int(month), dayMax)
                                ))
    page = Pagination(request, article_list.count(), per_page_num=4)
    article_list = article_list[page.start:page.end]
    return render(request, "homesite.html", locals())


# 文章详细页
def article_detail(request, username, article_id):
    # 通过username找到对应的user对象,作为参数传到base.html中
    if request.method == "GET":
        if not v.getView(article_id):
            v.initView(article_id)
        # 点击数 +1
        v.addView(request, article_id)
        click_count = v.getView(article_id)
        # 获取文章信息
        user = models.UserInfo.objects.filter(username=username).first()
        article = models.Article.objects.filter(pk=article_id).first()
        comment_list = models.Comment.objects.filter(article_id=article_id)
        return render(request, "article_detail.html", locals())


# 点赞
def poll(request):
    # 默认请求成功
    res = {"state": True, "is_up": None}
    is_up = json.loads(request.POST.get('is_up'))
    article_id = request.POST.get('article_id')
    user_id = request.user.pk
    try:
        models.ArticleUpDown.objects.create(is_up=is_up, article_id=article_id, user_id=user_id)
        if is_up:
            models.Article.objects.filter(pk=article_id).update(up_count=F("up_count") + 1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except Exception as e:
        print(e)
        # 点赞失败
        res["state"] = False
        # 获得第一次请求信息，是点赞还是反对
        is_up = models.ArticleUpDown.objects.filter(article_id=article_id, user_id=user_id).first().is_up
        res["is_up"] = is_up

    return JsonResponse(res)


# 评论
def comment(request):
    res = {"state": True}
    user_id = request.user.pk
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    pid = request.POST.get("pid")
    # 判断内容是否为空
    if not len(content):
        res["state"] = False
        res["msg"] = "评论内容不能为空！"
        return JsonResponse(res)
    else:
        if pid:
            ret = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                                parent_comment_id=pid)
        else:
            ret = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content)
        # 评论数加1
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)
        print(ret.create_time)
        res["create_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        res["username"] = ret.user.username
        res["pk"] = ret.pk
        res["content"] = ret.content
    return JsonResponse(res)


#  后台管理界面
def backend(request):
    # 判断是否登录
    if not request.user.username:
        return redirect("/login/")
    # 查询所有文章
    user_id = request.user.pk
    article_list = models.Article.objects.filter(user_id=user_id)
    page = Pagination(request, article_list.count())
    article_list = article_list[page.start:page.end]
    return render(request, "backend.html", locals())


#  后台 ——> 添加文章
def add_article(request):
    if request.method == "GET":
        user_id = request.user.pk
        cate_list = models.Category.objects.all()
        tag_list = models.Tag.objects.filter(blog__userinfo__nid=user_id)
        return render(request, "add_article.html", locals())
    if request.method == "POST":
        # 获取文章信息
        title = request.POST.get("title")
        cate = request.POST.get("choice_cate")
        cate = cate if cate != -1 else None
        tag_lst = request.POST.getlist("choice_tag")
        article_content = request.POST.get("article_content")
        # 获得desc
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(article_content, "html.parser")
        desc = bs.text[0:150] + "..."
        user = request.user
        # 内容过滤(去除script、css标签)
        for tag in bs.find_all():
            if tag.name in ["script", "link"]:
                tag.decompose()
        # 保存至数据库
        try:
            # 把添加文章步骤封装为 事务，保证原子性
            with transaction.atomic():
                article = models.Article.objects.create(user=user, title=title, desc=desc, category_id=cate)
                models.ArticleDetail.objects.create(article=article, content=str(bs))
                if len(tag_lst) > 0:
                    tag_obj_list = models.Tag.objects.filter(nid__in=tag_lst)
                    # 有多个标签，循环依次添加标签
                    for i in tag_obj_list:
                        models.Article2Tag.objects.create(article=article, tag=i)

        except Exception:
            return render(request, "400.html")
        return redirect("/blog/backend/")


#  后台 ——> 删除文章
def delete_article(request, article_id):
    if request.method == "GET":
        print(article_id)
        article = models.Article.objects.filter(pk=article_id).first()
        print(article)
        if article:
            article.delete()
            # # article.delete()
            return JsonResponse({"status": "0"})
        else:
            return JsonResponse({"status": "1"})


#  后台 ——> 编辑文章
def edit_article(request, article_id):
    if request.method == "GET":
        # 文章的 标题、文章详细内容、分类id
        article = models.Article.objects.filter(pk=article_id).values_list("title", "articledetail__content",
                                                                           "category__nid")
        # 该文章的标签
        tag_choice_list = [i[0] for i in
                           models.Article2Tag.objects.filter(article_id=article_id).values_list("tag__nid")]
        # 所有分类
        cate_list = models.Category.objects.all()
        # 所有标签
        tag_list = models.Tag.objects.filter(blog__userinfo__nid=request.user.pk)
        data = {
            "title": article[0][0],
            "content": article[0][1],
            "category": article[0][2],
        }
        return render(request, "edit_article.html", locals())
    if request.method == "POST":
        # 获取表单信息
        title = request.POST.get("title")
        article_content = request.POST.get("article_content")
        cate = request.POST.get("choice_cate")
        cate = cate if cate != -1 else None
        tag_lst = request.POST.getlist("choice_tag")
        username = request.user.username
        # 获得desc
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(article_content, "html.parser")
        desc = bs.text[0:150] + "..."
        user = request.user
        # 内容过滤(去除script、css标签)
        for tag in bs.find_all():
            if tag.name in ["script", "link"]:
                tag.decompose()
        # 获取文章对象
        article = models.Article.objects.filter(pk=article_id)
        # 更改文章内容
        try:
            # 封装成事务，保证原子性
            with transaction.atomic():
                article.update(title=title, desc=desc, category_id=cate)
                # 更改文章详细内容
                articleDetail = models.ArticleDetail.objects.filter(article_id=article_id).update(content=str(bs))
                # 先删除原标签，添加新标签
                for i in models.Article2Tag.objects.filter(article_id=article_id):
                    i.delete()
                for i in tag_lst:
                    models.Article2Tag.objects.create(article_id=article_id, tag_id=i)
        except Exception:
            return render(request, "400.html")
        return redirect("/blog/" + username + "/articles/" + article_id)


# 富文本编译器，上传图片并显示
def upload(request):
    import os
    from MyBBS import settings
    # 获取img对象
    obj_img = request.FILES.get('upload_img')
    # 获取保存文件路径以及图片名
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", obj_img.name)
    # 保存图片
    with open(path, "wb") as f:
        for line in obj_img:
            f.write(line)
    # 返回图片url
    url = "/media/add_article_img/" + obj_img.name
    res = {
        "error": 0,
        "url": url
    }
    return JsonResponse(res)


# 获取客户端IP
def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
    return ip
