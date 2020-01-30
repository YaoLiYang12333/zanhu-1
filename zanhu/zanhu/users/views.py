#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):
    # 要映射的模型类
    model = User
    # 手动添加模板
    template_name = 'users/user_detail.html'
    # 表示模型类里包含 slug的字段 此处为内置的username
    slug_field = "username"
    # 表示url路由配置里面 包含包含slug的关键字参数
    slug_url_kwarg = "username"

    # 后头开发的函数
    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data()
        # 获取当前登录的用户
        user = User.objects.get(username=self.request.user.username)
        # 动态数量  通过news -> models.py 中外键user 反向查询
        context["moments_num"] = user.publisher.filter(reply=False).count()
        # 文章数量  同理：articles -> models.py 中外键user 反向查询
        context["article_num"] = user.author.filter(status="P").count()  # 只算已发布的文章
        # 评论数量
        """
        from django_comments.models import Comment ctrl+左键 Comment
        class Comment(CommentAbstractModel):  ctrl+左键 CommentAbstractModel
        class CommentAbstractModel(BaseCommentAbstractModel):
            # 已关联到user %(class) 为类名，由于Comment又继承CommentAbstractModel，所以此处%(class)s为 Comment
            user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'),
                             blank=True, null=True, related_name="%(class)s_comments",
                             on_delete=models.SET_NULL)
        """
        # 文章品论数 + 动态评论数
        context["comment_num"] = user.publisher.filter(reply=True).count() + user.comment_comments.count()

        # 提问数量
        context["question_num"] = user.q_author.all().count()
        # 回答数量
        context["answer_num"] = user.a_author.all().count()

        # 互动数量 = 动态点赞数 + 问答点赞数 + 评论数 + 私信用户数(都有发送或接收到私信)
        tmp = set()
        # 我发送私信给了多少不同的用户
        sent_num = user.sent_messages.all()
        for i in sent_num:
            tmp.add(i.recipient.username)
        # 我接收的所有私信来自多少不同的用户
        received_num = user.received_messages.all()
        for r in received_num:
            tmp.add(r.sender.username)

        context["interaction_num"] = user.liked_news.all().count() + user.qa_vote.all().count() + context[
            "comment_num"] + len(tmp)

        return context


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):
    '''用户只能更新自己的信息'''

    model = User
    # 允许用户更改的字段
    fields = ["nickname", "email", "picture", "job_title", "introduction", "location", "personal_url",
              "weibo", "zhihu", "github", "linkedin"]

    # 指定模板
    template_name = 'users/user_form.html'

    # 表示更新成功后跳转的页面
    def get_success_url(self):
        # 更新成功后跳转到自己页面
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    # 获取成功后返回前端的对象
    def get_object(self, queryset=None):
        # 原代码
        # return User.objects.get(username=self.request.user.username)
        return self.request.user

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)


user_update_view = UserUpdateView.as_view()

# class UserRedirectView(LoginRequiredMixin, RedirectView):
#
#     permanent = False
#
#     def get_redirect_url(self):
#         return reverse("users:detail", kwargs={"username": self.request.user.username})
#
#
# user_redirect_view = UserRedirectView.as_view()
