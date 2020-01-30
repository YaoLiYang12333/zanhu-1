#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.urls import reverse_lazy
# django的消息机制
from django.contrib import messages
# django-comments的信号机制(在github上提供有3个信号机制) comment_was_posted 评论已被提交时
from django_comments.signals import comment_was_posted
# 缓存装饰器
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from zanhu.articles.models import Article
from zanhu.articles.forms import ArticleForm
from zanhu.notifications.views import notification_handler

# django信号机制
# 为触发模式request_started 请求开始时触发 request_finished请求结束后触发
# from django.core.signals import request_started,request_finished

from zanhu.helpers import AuthorRequiredMixin


# 已发布的文章列表
class ArticlesListView(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 20
    context_object_name = 'articles'
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        # 重载父类方法
        context = super(ArticlesListView, self).get_context_data()
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    # 只返回已发布的文章
    def get_queryset(self):
        return Article.objects.get_published()


# 草稿箱文章列表
class DraftListView(ArticlesListView):
    # 当前用户的草稿
    def get_queryset(self, **kwargs):
        return Article.objects.filter(user=self.request.user).get_drafts()


# 发表文章
@method_decorator(cache_page(60 * 60), name='get')  # get是小写
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/article_create.html"
    # 消息提醒 只是自定义的字符串
    message = "您的文章创建成功！"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleCreateView, self).form_valid(form)

    # 创建成功后跳转
    def get_success_url(self):
        # 通过django messages 消息机制，将消息传递给下一次请求 下下次就没有了
        messages.success(self.request, self.message)
        return reverse_lazy("articles:list")


class ArticleDetailView(LoginRequiredMixin, DetailView):
    """文章详情"""
    model = Article
    template_name = "articles/article_detail.html"

    def get_queryset(self):
        # slug=self.kwargs['slug'] 为urls 中传递的参数 slug
        return Article.objects.select_related('user').filter(slug=self.kwargs['slug'])


class ArticleEditView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """编辑文章"""
    model = Article
    template_name = "articles/article_update.html"
    # 关联到用户需要填写的表单
    form_class = ArticleForm
    message = "文章编辑成功"

    # 自动填充给标题栏 填充ok
    # initial = {"title": "ok"}

    def form_valid(self, form):
        """编辑验证"""
        form.instance.user = self.request.user
        return super(ArticleEditView, self).form_valid(form)

    def get_success_url(self):
        """编辑成功, 跳转链接"""
        messages.success(self.request, self.message)
        return reverse_lazy("articles:article", kwargs={"slug": self.get_object().slug})

    # 自动填充逻辑 适用于发表规律性内容
    # def get_initial(self):
    #     initial = super().get_initial()
    #     # 填充逻辑
    #     return initial


# 10-13章 结合django-comments信号机制实现文章评论的通知
def notify_comments(**kwargs):
    """文章有评论时通知作者"""
    # 从参数中提取动作执行者，即哪个用户给此文章评论
    actor = kwargs["request"].user
    # from django_comments.models import Comment | Comment模型类 中的通用外键
    obj = kwargs["comment"].content_object

    notification_handler(actor, obj.user, "C", obj)


# 调用信号机制
# receiver=notify_comments(信号目标) 也就是评论被提交之后 执行notify_comments 函数
comment_was_posted.connect(receiver=notify_comments)
