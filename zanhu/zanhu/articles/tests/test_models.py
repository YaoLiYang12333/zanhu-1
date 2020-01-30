#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from test_plus.test import TestCase
from zanhu.articles.models import Article


class ArticleModelsTest(TestCase):
    def setUp(self):
        self.user = self.make_user("test_user")
        self.other_user = self.make_user("other_test_user")
        self.article = Article.objects.create(
            title="第一篇文章",
            content="第一篇文章的测试",
            status="P",
            user=self.user
        )
        self.not_p_article = Article.objects.create(
            title="第二篇文章",
            content="第二篇文章的测试",
            # status="P",  模型类默认为D，所以忽略
            user=self.user
        )

    # 判断实例对象是否为Article模型类
    def test_object_instance(self):
        assert isinstance(self.article, Article)
        assert isinstance(self.not_p_article, Article)
        assert isinstance(Article.objects.get_published()[0], Article)
        assert isinstance(Article.objects.get_drafts()[0], Article)

    # 测试返回值
    def test_return_values(self):
        assert self.article.status == "P"
        assert self.not_p_article.status == "D"
        assert str(self.article) == "第一篇文章"
        assert self.article in Article.objects.get_published()
        assert self.not_p_article in Article.objects.get_drafts()
        assert Article.objects.get_published()[0].title == "第一篇文章"
        assert Article.objects.get_drafts()[0].title == "第二篇文章"

