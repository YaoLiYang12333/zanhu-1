#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from __future__ import unicode_literals
import uuid

from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from zanhu.users.models import User
from zanhu.notifications.views import notification_handler


# Create your models here.

@python_2_unicode_compatible
class News(models.Model):
    # 主键
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                               help_text="uuid主键")
    # 用户 用户被封号后评论不被删除 blank=True, null=True， 当父表用户删除时，子表置空 on_delete=models.SET_NULL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
                             related_name='publisher', verbose_name='用户')

    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE,
                               related_name='thread', verbose_name='自关联', help_text="内容/评论自关联")
    # 用户发表的内容
    content = models.TextField(verbose_name='动态内容', help_text="可以是文章也可以是评论")

    # 多对多  null=True, blank=True null has no effect on ManyToManyField
    liked = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_news',
                                   verbose_name='点赞用户')
    # liked = models.ManyToManyField(User, related_name='liked_news',
    #                                verbose_name='点赞用户')
    reply = models.BooleanField(default=False, verbose_name='是否为评论', help_text="默认是文章内容")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '首页'
        verbose_name_plural = verbose_name
        ordering = ('-created_at',)

    def __str__(self):
        # 返回用户发表的内容
        return self.content

    # 实现10-9章 冒泡提示 重写save方法
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(News, self).save()
        if not self.reply:
            # 将消息传递给consumer.py中的receive方法

            # 获取频道层 与consumer.py中self.channel_layer获取的时同一频道
            channel_layer = get_channel_layer()
            payload = {
                'type': 'receive',
                # 'key': key,  # 当key == 某一个值时，触发另外的JS
                'key': "additional_news",  # 变为JS->notifications.js 中定义的 line 90 additional_news
                'actor_name': self.user,  # 动作执行者变为 此动态的用户
                # 'id_value': id_value  # 不需要  此为更新点赞数
            }
            async_to_sync(channel_layer.group_send)('notifications', payload)

    def switch_like(self, user):
        '''点赞或取消赞'''
        # 赞过则取消
        # liked多对多外键字段 直接.all() 获取获取数据
        if user in self.liked.all():
            self.liked.remove(user)
        # 未赞 则点赞
        else:
            self.liked.add(user)
            # 点赞时通知楼主
            # user 为点赞用户，self.user为动态作者 verb为L action_object 为 当前这条动态 为self
            # id_value key 为必须参数  key值不同则 notifications.JS触发不同
            notification_handler(user, self.user, "L", self, id_value=str(self.uuid_id), key="social_update")

    def get_parent(self):
        '''返回自关联中的上级记录或者本身'''
        if self.parent:
            return self.parent
        else:
            return self

    def reply_this(self, user, text):
        """
        回复首页的动态
        user -> 登录的用户
        test -> 回复的内容
        """
        # 获取父记录 获取动态
        parent = self.get_parent()

        News.objects.create(
            user=user,
            content=text,
            reply=True,
            parent=parent
        )
        notification_handler(user, parent.user, "R", parent, id_value=str(parent.uuid_id), key="social_update")

    def get_thread(self):
        '''关联到当前记录的所有记录'''
        parent = self.get_parent()
        # 通过 relate_name 来查询所有子记录
        return parent.thread.all()

    def comment_count(self):
        '''评论数'''
        return self.get_thread().count()

    def count_likers(self):
        '''点赞数'''
        return self.liked.count()

    def get_likers(self):
        '''所有点赞用户'''
        return self.liked.all()
