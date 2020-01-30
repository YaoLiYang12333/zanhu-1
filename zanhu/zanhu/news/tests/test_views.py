#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from test_plus.test import TestCase
from zanhu.news.models import News
from django.test import Client
from django.urls import reverse

'''
视图测试2种思路:         1. 模拟浏览器请求方式，走整个django的请求流程
                        2.  通过requestfactery类，只测试视图功能，跳过wsgi server中间键，路由等等
'''


# 第一种方法
class NewsViewTest(TestCase):
    def setUp(self):
        self.user = self.make_user('user01')
        self.other_user = self.make_user('user02')
        # 生成客户端实例 --> 可理解为使用一个浏览器
        self.client = Client()
        self.other_client = Client()
        # 用户登录
        self.client.login(username='user01', password='password')
        self.other_client.login(username='user02', password='password')
        # 发表动态
        self.first_news = News.objects.create(
            user=self.user,
            content='第一条测试动态'
        )

        self.second_news = News.objects.create(
            user=self.user,
            content='第二条测试动态'
        )

        self.third_news = News.objects.create(
            user=self.other_user,
            content='评论第一条测试动态',
            reply=True,
            parent=self.first_news
        )

    # 测试动态列表页功能
    def test_view_list(self):
        # self.client.get('news/list/') 一种写法
        # 这种写法好处：url改变路由没有改变 此处就不会出错 如果路由有问题则会影响此处测试
        response = self.client.get(reverse("news:list"))
        # 断言 响应的动态码 为200
        assert response.status_code == 200
        # 断言 动态在响应的上下文中
        assert self.first_news in response.context["news_list"]
        # 断言 评论不在上下文中
        assert self.third_news not in response.context["news_list"]

    # 测试删除动态
    def test_delete_news(self):
        # 总对象数量
        initial_count = News.objects.count()
        # 删除第二条动态
        response = self.client.post(reverse("news:delete_news", kwargs={"pk": self.second_news.pk}))
        assert response.status_code == 302
        assert News.objects.count() == initial_count - 1

    # 测试发送动态
    def test_post_news(self):
        # 总对象数量
        initial_count = News.objects.count()
        response = self.client.post(
            reverse("news:post_news"), {"post": "测试发表动态"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"  # 表示发送ajax请求
        )
        assert response.status_code == 200
        assert News.objects.count() == initial_count + 1

    # 测试点赞
    def test_like_news(self):
        response = self.client.post(
            reverse("news:like_post"),
            {"news": self.first_news.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        # 断言 点赞数量为1
        assert self.first_news.count_likers() == 1
        # 断言 用户在点赞用户中
        assert self.user in self.first_news.get_likers()
        # 获取JsonResponse的值
        assert response.json()["likes"] == 1

    # 测试动态的评论
    def test_get_thread(self):
        response = self.client.get(reverse("news:get_thread"), {"news": self.first_news.pk},
                                   HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert response.status_code == 200
        # 断言 JsonResponse中的uuid、news、thread  | news、thread 为render_to_string 后的字符串
        assert response.json()['uuid'] == str(self.first_news.pk)
        assert "第一条测试动态" in response.json()["news"]
        assert "评论第一条测试动态" in response.json()["thread"]

    # 测试发表动态
    def test_post_conntent(self):
        response = self.client.post(
            reverse("news:post_comments"),
            {"reply": "第二条测试动态的评论", "parent": self.second_news.pk},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert response.status_code == 200
        assert response.json()["comments"] == 1
