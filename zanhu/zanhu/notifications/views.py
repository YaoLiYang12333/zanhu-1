#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from zanhu.notifications.models import Notification


class NotificationUnreadListView(LoginRequiredMixin, ListView):
    """未读通知列表"""
    model = Notification
    context_object_name = 'notification_list'
    template_name = 'notifications/notification_list.html'

    def get_queryset(self, **kwargs):
        # self.request.user登录的用户  | .notifications 反向查询 models.py中的recipient
        return self.request.user.notifications.unread()


@login_required
def mark_all_as_read(request):
    """将所有通知标为已读"""
    request.user.notifications.mark_all_as_read()
    # 如果是从其他链接跳转过来的 获取要跳转的地址
    redirect_url = request.GET.get('next')

    messages.add_message(request, messages.SUCCESS, f'用户{request.user.username}的所有通知标为已读')
    # messages.success()
    # messages.error() 报错时 怎么做
    # messages.info() 普通的信息提醒
    # messages.warning() 发生错误时报警

    if redirect_url:
        # 如有要跳转的地址 则跳转
        return redirect(redirect_url)

    # 跳转到未读通知页
    return redirect('notifications:unread')


@login_required
def mark_as_read(request, slug):
    """根据slug标为已读"""
    notification = get_object_or_404(Notification, slug=slug)
    notification.mark_as_read()

    redirect_url = request.GET.get('next')

    messages.add_message(request, messages.SUCCESS, f'通知{notification}标为已读')
    # messages.add_message(request, messages.WARING, f'通知{notification}标为已读')  # 提示框为 黄色
    # messages.add_message(request, messages.ERROR, f'通知{notification}标为已读') # 提示框为 红色

    if redirect_url:
        return redirect(redirect_url)

    return redirect('notifications:unread')


@login_required
def get_latest_notifications(request):
    """最近的未读通知"""
    notifications = request.user.notifications.get_most_recent()
    return render(request, 'notifications/most_recent.html',
                  {'notifications': notifications})


def notification_handler(actor, recipient, verb, action_object, **kwargs):
    """
    通知处理器
    :param actor:           request.user对象
    :param recipient:       User Instance 接收者实例，可以是一个或者多个接收者
    :param verb:            str 通知类别
    :param action_object:   Instance 动作对象的实例
    :param kwargs:          key, id_value等
    :return:                None
    """
    # 只通知接收者，即recipient(接收者) == action_object(动作对象)的作者
    # 并且actor.username(动作发起者) != recipient.username(接收者)  即 自己给自己点赞 无显示
    if actor.username != recipient.username and recipient.username == action_object.user.username:
        # 获取关键字参数里的key 默认为'notification'
        key = kwargs.get('key', 'notification')
        id_value = kwargs.get('id_value', None)
        # 记录通知内容 存入数据库
        Notification.objects.create(
            actor=actor,
            recipient=recipient,
            verb=verb,
            action_object=action_object
        )
        # 将消息传递给consumer.py中的receive方法

        # 获取频道层 与consumer.py中self.channel_layer获取的时同一频道
        channel_layer = get_channel_layer()
        payload = {
            'type': 'receive',
            'key': key,  # 当key == 某一个值时，触发另外的JS
            'actor_name': actor.username,
            'id_value': id_value
        }
        async_to_sync(channel_layer.group_send)('notifications', payload)
