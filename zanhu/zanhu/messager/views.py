#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

from asgiref.sync import async_to_sync
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
# get_user_model()实际获取的是settings.AUTH_USER_MODEL指定的User model
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from django.template.loader import render_to_string

# 获取所在的频道
from channels.layers import get_channel_layer

from zanhu.messager.models import Message
from zanhu.helpers import ajax_required


# 所有用户的私信列表
class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    # 聊天页面不需要分页
    # paginate_by = 10
    template_name = "messager/message_list.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MessagesListView, self).get_context_data()
        # 获取除当前登录用户外的所有用户，按最近登录时间降序排列
        # is_active=True只要已激活的用户 exclude排除自己 username=self.request.user
        context['users_list'] = get_user_model().objects.filter(is_active=True).exclude(
            username=self.request.user
        ).order_by('-last_login')[:10]
        # 最近一次私信互动的用户
        last_conversation = Message.objects.get_most_recent_conversation(self.request.user)
        # 前端样式  message_list.html中 {{ "active" }} 的值
        context['active'] = last_conversation.username
        return context

    def get_queryset(self):
        """最近私信互动的内容"""
        active_user = Message.objects.get_most_recent_conversation(self.request.user)
        return Message.objects.get_conversation(self.request.user, active_user)


class ConversationListView(MessagesListView):
    """与指定用户的私信内容"""

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ConversationListView, self).get_context_data()
        # 用户在前端与指定用户聊天时 样式active 就变成指定用户
        context['active'] = self.kwargs["username"]
        return context

    # sql优化：只返回选中的用户
    def get_queryset(self):
        active_user = get_object_or_404(get_user_model(),
                                        username=self.kwargs["username"])
        return Message.objects.get_conversation(self.request.user, active_user)


@login_required
@ajax_required
@require_http_methods(["POST"])
def send_message(request):
    """发送消息，AJAX POST请求"""
    sender = request.user
    recipient_username = request.POST['to']
    recipient = get_user_model().objects.get(username=recipient_username)
    message = request.POST['message']
    # len(message.strip()) != 0 发送内容不为空  sender != recipient 发送者不是接收者
    if len(message.strip()) != 0 and sender != recipient:
        msg = Message.objects.create(
            sender=sender,
            recipient=recipient,
            message=message
        )
        # 获取频道层
        channel_layer = get_channel_layer()
        # 视图中要传递给consumer的数据
        payload = {
            # type必须有 receive为consumer.py中的receive函数
            'type': 'receive',
            # 要传递的消息内容 render_to_string将要传递的数据换位字符串，相当于前端代码.format(xxx)
            'message': render_to_string('messager/single_message.html', {"message": msg}),
            'sender': sender.username
        }
        # group_send(group: 要发送的组[所在组-接收者的username], message: 消息内容)
        # consumer.py中方法为异步，需要把异步变为同步
        # 使用时 async_to_sync(要转换的函数名)(转换函数的参数)
        async_to_sync(channel_layer.group_send)(recipient.username, payload)

        return render(request, 'messager/single_message.html', {'message': msg})

    return HttpResponse()


# 由于使用messager.js 定义了 websocket连接 所以不需要此函数 来使用ajax来接收数据
# 同时也删除了 messager.js 定义的ajax接收函数
# @login_required
# @ajax_required
# @require_http_methods(["GET"])
# def get_message(request):
#     """接收消息 AJAX get请求"""
#     msg_id = request.GET["message_id"]
#     msg = Message.objects.get(msg_id)
#     return render(request, "messager/single_message.html", {"message": msg})
