#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from test_plus.test import TestCase
from zanhu.news.models import News


class NewsModelsTest(TestCase):
    def setUp(self):
        # 新建2个用户
        self.user = self.make_user('user01')
        self.other_user = self.make_user('user02')

        # 第一个用户发表2条动态
        self.first_news = News.objects.create(
            user=self.user,
            content='第一条测试动态'
        )
        self.second_news = News.objects.create(
            user=self.user,
            content='第二条测试动态'
        )
        # 第二个用户评论第一条动态
        self.third_news = News.objects.create(
            user=self.other_user,
            content='第一次评论第一条动态',
            reply=True,
            parent=self.first_news
        )

    # 测试__str__ 方法
    def test_str(self):
        # 错误写法
        # self.assertEqual(self.first_news, '第一条测试动态')
        self.assertEqual(self.first_news.__str__(), '第一条测试动态')

    # 测试点赞/取消赞功能
    def test_switch_liked(self):
        # 第一个用户给自己点赞
        self.first_news.switch_like(self.user)
        # 断言 点赞后点赞数量 =1
        assert self.first_news.count_likers() == 1
        # 断言 此用户在赞过的用户里
        assert self.user in self.first_news.get_likers()

    # 测试回复功能
    def test_reply_this(self):
        # 用户模型类中总对象数
        initial_count = News.objects.count()
        # 第二个用户评论
        self.first_news.reply_this(self.other_user, '第二次评论第一条动态')
        # 断言 评论过后用户模型对象 +1
        assert News.objects.count() == initial_count + 1
        # 断言 第一条动态 评论数量为2
        assert self.first_news.comment_count() == 2
        assert self.third_news in self.first_news.get_thread()
