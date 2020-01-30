#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

from django.urls import path
# 导入认证中间键
from channels.auth import AuthMiddlewareStack
# 导入协议解析器ProtocolTypeRouter 、URLRouter 可以想django url路由一样写 websocket路由
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from zanhu.messager.consumer import MessagesConsumer
from zanhu.notifications.consumers import NotificationsConsumer

# self.scope['type']获取协议类型
# self.scope['url_route']['kwargs'] ['username']获取url中关键字参数，
# 相当于views中获取路由参数的 return reverse("xxx路由"，kwargs={"传递字段名"：self.kwargs['路由参数']})
# channels routing是scope级别的，一个连接只能由一个consumer接收和处理
application = ProtocolTypeRouter({
    # "http":views  # 普通的HTTP请求不需要我们手动在这里添加，框架会自动加载

    # AllowedHosts 读取我们在.env中定义的DJANGO_ALLOWED_HOSTS，读取对应的IP和域名
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                # 和http协议区分在前面添加 ws/
                path('ws/notifications/', NotificationsConsumer),
                path('ws/<str:username>/', MessagesConsumer),
            ])
        )
    )
})

"""
OriginValidator或AllowedHostsOriginValidator可以防止通过WebSocket进行CSRF攻击

from channels.security.websocket import AllowedHostsOriginValidator
可以读取我们settings中定义的DJANGO_ALLOWED_HOSTS(.env中定义的DJANGO_ALLOWED_HOSTS)，读取对应的IP和域名

from channels.security.websocket import OriginValidator
OriginValidator需要手动添加允许访问的源站，如：

application = ProtocolTypeRouter({
    'websocket': OriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                路由匹配
                ...
            ])
        ),
        # OriginValidator函数参数为2个 第一个application （应用） 第二个为allowed_origins(允许访问的域名)
        [".imooc.com", "http://.imooc.com:80", "http://muke.site.com"]
    )
})
使用AllowedHostsOriginValidator，允许的访问的源站与settings.py文件中的ALLOWED_HOSTS相同

AuthMiddlewareStack用于WebSocket认证，集成了CookieMiddleware, SessionMiddleware,
AuthMiddleware, 兼容Django认证系统
"""
