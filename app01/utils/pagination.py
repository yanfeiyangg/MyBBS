"""
    分页
"""
from django.utils.safestring import mark_safe
from django.http import QueryDict


class Pagination:
    def __init__(self, request, data_length, page_num=11, per_page_num=5):
        self.urlDict = self.get_urlencode(request)
        self.path_info = request.path_info
        self.per_page_num = per_page_num  # 每页显示的数目
        self.page_num = page_num  # 页面标签数量
        self.half_page_num = self.page_num // 2  # 半个页面数量
        # 避免传入的参数有误
        try:
            self.current_page = int(request.GET.get("page"))  # 获取当前页数
            if self.current_page <= 0:
                self.current_page = 1
        except Exception:
            self.current_page = 1

        # 2.把所有页数显示出来(页总数，余数)
        self.page_total, more = divmod(data_length, self.per_page_num)
        if more:
            self.page_total += 1

        # 如果当前只分了8页，而最大显示的页数为11，则需要修改最大显示页数为 当前可分页的页数
        if self.page_total < self.page_num:
            self.page_num = self.page_total

    @property
    def start(self):
        '''数据区间[start:end]'''
        return (self.current_page - 1) * self.per_page_num

    @property
    def end(self):
        '''数据区间[start:end]'''
        return self.current_page * self.per_page_num

    @property
    def show(self):
        '''显示分页的HTML标签'''
        # 当左边不足 half_page_num 时，显示固定长度
        if self.current_page - self.half_page_num <= 0:
            page_range = range(1, self.page_num + 1)
        # 当右边不足 half_page_num 时，显示固定长度
        elif self.current_page + self.half_page_num + 1 > self.page_total:
            page_range = range(self.page_total - self.page_num + 1, self.page_total + 1)
        # 正常中间情况
        else:
            page_range = range(self.current_page - self.half_page_num, self.current_page + self.half_page_num + 1)

        # 返回页面的html集合
        html_page = []

        # 前一页以及第一页
        if self.current_page == 1:
            # 首页
            html_page.append('<li class="disabled"><a>&lt;&lt;</a></li>')
            # 前一页
            html_page.append('<li class="disabled"><a>&lt;</a></li>')
        else:
            # 首页
            self.urlDict["page"] = 1
            html_page.append('<li><a href="{0}?{1}">&lt;&lt;</a></li>'.format(self.path_info, self.urlDict.urlencode()))
            # 前一页
            self.urlDict["page"] = self.current_page - 1
            html_page.append('<li><a href="{1}?{0}">&lt;</a></li>'.format(self.urlDict.urlencode(), self.path_info))

        # 中间部分
        for i in page_range:
            if i == self.current_page:
                self.urlDict["page"] = i
                html_page.append(
                    '<li class="active" ><a href="{1}?{2}">{0}</a></li>'.format(i, self.path_info,
                                                                                self.urlDict.urlencode()))
            else:
                self.urlDict["page"] = i
                html_page.append(
                    '<li><a href="{1}?{2}">{0}</a></li>'.format(i, self.path_info, self.urlDict.urlencode()))
        # 后一页以及最后一页
        if self.current_page == self.page_total:
            html_page.append('<li class="disabled"><a>&gt;</a></li>')
            html_page.append('<li class="disabled"><a>&gt;&gt;</a></li>')
        else:
            # 后一页
            self.urlDict["page"] = self.current_page + 1
            html_page.append('<li><a href="{1}?{0}">&gt;</a></li>'.format(self.urlDict.urlencode(), self.path_info))
            # 最后一页
            self.urlDict["page"] = self.page_total
            html_page.append('<li><a href="{1}?{0}">&gt;&gt;</a></li>'.format(self.urlDict.urlencode(), self.path_info))
        h = '<nav><div style="text-align: right;"><ul class="pagination">{0}</ul></div></nav>'.format("".join(html_page))
        return mark_safe(h)

    def get_urlencode(self, request):
        '''深拷贝GET QueryDict()对象，为了对url添加args'''
        urlDict = request.GET.copy()  # 自带方法的深拷贝
        urlDict._mutable = True  # 允许修改GET的数据
        return urlDict
