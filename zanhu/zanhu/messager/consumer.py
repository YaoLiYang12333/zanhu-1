#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
import json


class MessagesConsumer(AsyncWebsocketConsumer):
    """
    处理思想业务中的WebSocket请求
    self.channel_layer & self.channel_name 已封装好的方法 不需要导入
    """

    # 连接
    async def connect(self):
        # self.scope['user']为http请求 is_anonymous 是否为匿名用户(为登录)
        if self.scope['user'].is_anonymous:
            # 未登录的用户拒绝连接
            await self.close()
        else:
            # 加入聊天组
            # 为保证用户聊天组的唯一性  采用主键用户id作为组名
            # self.scope['user'].username当前登录用户的用户名，即哪个用户登录了 点开了聊天页 就把他加入聊天组
            await self.channel_layer.group_add(self.scope['user'].username, self.channel_name)
            # 接受websocket连接
            await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """接收私信"""
        # 此处接收到的私信 为什么要通过send方法返回前端？不应该通过ORM保存到数据库？后面奖后后端数据库设计即可了解
        # text_data=None不是前端发送来的私信内容
        await self.send(text_data=json.dumps(text_data))

    async def disconnect(self, code):
        """离开聊天组"""
        await self.channel_layer.group_discard(self.scope['user'].username, self.channel_name)
