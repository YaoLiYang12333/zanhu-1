#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

""" 原代码
import pytest
from django.conf import settings
from django.urls import reverse, resolve

pytestmark = pytest.mark.django_db

def test_detail(user: settings.AUTH_USER_MODEL):
    assert (
        reverse("users:detail", kwargs={"username": user.username})
        == f"/users/{user.username}/"
    )
    assert resolve(f"/users/{user.username}/").view_name == "users:detail"


def test_update():
    assert reverse("users:update") == "/users/~update/"
    assert resolve("/users/~update/").view_name == "users:update"

def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"
"""

from test_plus.test import TestCase
from django.urls import reverse, resolve


class TestUserURLs(TestCase):
    """将路由函数正向解析，反向解析各一次"""

    def setUp(self):
        self.user = self.make_user()

    def test_detail_reverse(self):
        # 参数来自self.make_user中创建的测试数据
        self.assertEqual(reverse('users:detail', kwargs={'username': 'testuser'}), '/users/testuser/')

    def test_detail_resolve(self):
        # 测试函数传递的是类视图，所以加view_name 方法
        self.assertEqual(resolve('/users/testuser/').view_name, 'users:detail')

    def test_updata_reverse(self):
        self.assertEqual(reverse('users:update'), '/users/update/')

    def test_update_resolve(self):
        self.assertEqual(resolve('/users/update').view_name, 'users:update')
