#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

# 所有视图需要登录后才能看见
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from zanhu.news.models import News
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
# 表示要求的hhtp方法可以用来装饰http函数
from django.views.decorators.http import require_http_methods
from zanhu.helpers import ajax_required, AuthorRequiredMixin
from django.urls import reverse, reverse_lazy


# Create your views here.
class NewsListView(LoginRequiredMixin, ListView):
    """首页动态"""
    # 指定关联的模型类，给模板返回哪一个表中的数据
    model = News
    # 分页 每页显示多少 url中的？page
    paginate_by = 20
    # 指定前端渲染的模板
    template_name = 'news/news_list.html'  # 可以不写默认为: 模型类名_.html

    '''
    # 前端html中要循环的对象 默认为 模型类名_.list 或 object_list
    context_object_name = 'new_list'
    ordering = 'created_at'  # 多字段排序 需要用元组
    # 简单过滤
    queryset = News.objects.all()


    # 使用更复杂的排序
    def get_ordering(self):
        pass

    # 更复杂的分页 queryset -> 查询集对象
    def get_paginate_by(self, queryset):
        pass
    '''

    # 更多逻辑处理 实现动态过滤
    def get_queryset(self):
        # 因为 News.objects.filter(reply=False)直接是模型类api所以可以直接接在后面
        return News.objects.filter(reply=False).select_related("user", "parent").prefetch_related("liked")

    # 添加额外的数据个前端
    def get_context_data(self, *, object_list=None, **kwargs):
        # 重载弗雷方法
        context = super().get_context_data()
        # 定义要浏览的次数
        context['views'] = 100
        # 此处返回的内容包含 get_queryset() 过滤后的查询集对象
        return context


# AuthorRequiredMixin为helper.py中自定义类
class NewsDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    """
    AuthorRequiredMixin中self.get_object().user.username 来自SingleObjectMixin(ContextMixin)
    通过外键关联到user表 查找到username
    """
    model = News
    template_name = 'news/news_confirm_delete.html'
    slug_url_kwarg = 'slug'  # 通过url传入要删除的对象id，默认值是slug
    pk_url_kwarg = 'pk'  # 通过url传入要删除的对象id，默认值是pk
    # 删除成功后跳转页面 此处使用reverse_lazy好处 ：在项目URLconf 未加载前使用
    success_url = reverse_lazy("news:list")


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_news(request):
    '''发送动态，AJAX POST请求'''
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        html = render_to_string('news/news_single.html', {'news': posted, 'request': request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest("内容不能为空！")


@login_required
@ajax_required
@require_http_methods(['POST'])
def like(request):
    '''点赞，AJAX POST请求'''
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    # 取消赞 或者添加赞
    news.switch_like(request.user)
    # 返回赞数 JSON格式
    return JsonResponse({'likes': news.count_likers()})


@login_required
@ajax_required
@require_http_methods(['GET'])
def get_thread(request):
    '''获取当前状态下的所有评论，AJAX GET请求'''
    news_id = request.GET['news']
    """
    # news = News.objects.get(pk=news_id)     sql语句优化
    因为get(pk=news_id)不是查询集 所以select_related('user')要放News.objects后面
    不需要加上parent 因为已经是评论了
    """
    news = News.objects.select_related('user').get(pk=news_id)
    # 没有评论的时候 render_to_string()表示加载模板，填充数据，返回字符串
    news_html = render_to_string('news/news_single.html', {'news': news})
    # 有评论的时候
    thread_html = render_to_string('news/news_thread.html', {'thread': news.get_thread()})
    return JsonResponse({
        'uuid': news_id,
        'news': news_html,
        'thread': thread_html
    })


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_comment(request):
    '''评论，AJAX POST请求'''
    # 获取用户提价的评论内容
    post = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    parent = News.objects.get(pk=parent_id)
    if post:
        parent.reply_this(request.user, post)
        return JsonResponse({'comments': parent.comment_count()})
    else:  # 评论为空返回400.html
        return HttpResponseBadRequest('内容不能为空！')


# 10-11章 WebSocket触发Ajax请求-自动更新点赞数和评论数
@login_required
@ajax_required
@require_http_methods(['POST'])
def update_interactions(request):
    """
    更新点赞数，和评论数
    models中以实现 comment_count count_likers
    """
    data_point = request.POST["id_value"]
    news = News.objects.get(pk=data_point)
    return JsonResponse({"likes": news.count_likers(), "comments": news.comment_count()})
