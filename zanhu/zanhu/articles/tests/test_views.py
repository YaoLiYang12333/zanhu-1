#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from test_plus.test import TestCase
from django.test import override_settings
from django.urls import reverse

# 将临时文件保存到临时文件目录下 测试完消失
import tempfile
from PIL import Image

from zanhu.articles.models import Article


class ArticleViewTest(TestCase):
    # 创建并读取临时图片
    @staticmethod
    def get_temp_img():
        img_size = (200, 200)
        img_color = (255, 0, 0, 0)
        # suffix=".png" 后缀为.png  |  delete=False 临时文件不删除
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image = Image.new("RGB", size=img_size, color=img_color)
            image.save(f, "PNG")
        return open(f.name, mode="rb")

    def setUp(self):
        self.user = self.make_user()
        self.client.login(username="testuser", password="password")
        self.article = Article.objects.create(
            title="第一篇文章",
            content="第一篇文章的测试",
            status="P",
            user=self.user
        )

        self.test_image = self.get_temp_img()

    # 测试结束时，关闭临时图片文件
    def tearDown(self):
        self.test_image.close()

    # 测试文章列表页
    def test_index_articles(self):
        response = self.client.get(reverse("articles:list"))
        self.assertEqual(response.status_code, 200)

    # 访问一篇不存在的文章
    def test_error_404(self):
        response_no_page = self.client.get(reverse("articles:article", kwargs={"slug": "no-slug"}))
        self.assertEqual(response_no_page.status_code, 404)

    # MEDIA_ROOT=tempfile.gettempdir() 指定临时文件路径  重写了settings.py文件中MEDIA_ROOT
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_article(self):
        # 测试文章发表功能   文章创建成功后跳转
        response = self.client.post(reverse("articles:write_new"),
                                    {"title": "这是标题",
                                     "content": "这是内容",
                                     "tags": "标签",
                                     "status": "P",
                                     "image": self.test_image})
        assert response.status_code == 302

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_single_article(self):
        # 测试多篇文章发表
        current_count = Article.objects.count()
        response = self.client.post(reverse("articles:write_new"),
                                    {"title": "这是标题2",
                                     "content": "这是内容2",
                                     "tags": "标签2",
                                     "status": "P",
                                     "image": self.test_image})
        assert response.status_code == 302
        assert Article.objects.count() == current_count + 1

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_draft_article(self):
        # 测试草稿箱功能
        response = self.client.post(reverse("articles:write_new"),
                                    {"title": "草稿文章",
                                     "content": "草稿箱的文章",
                                     "tags": "测试",
                                     "status": "D",
                                     "image": self.test_image})
        resp = self.client.get(reverse("articles:drafts"))
        assert resp.status_code == 200
        assert response.status_code == 302
        assert resp.context["articles"][0].slug == "cao-gao-wen-zhang"
