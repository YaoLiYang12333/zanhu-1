#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

from django.test import Client
from django.urls import reverse
from test_plus.test import TestCase

from zanhu.messager.models import Message


class MessagesViewsTests(TestCase):

    def setUp(self):
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")
        self.client = Client()
        self.other_client = Client()
        self.client.login(username="user01", password="password")
        self.other_client.login(username="user02", password="password")
        self.first_message = Message.objects.create(
            sender=self.user,
            recipient=self.other_user,
            message="user01发送给user02的第一条私信"
        )
        self.second_message = Message.objects.create(
            sender=self.user,
            recipient=self.other_user,
            message="user01发送给user02的第二条私信"
        )
        self.third_message = Message.objects.create(
            sender=self.other_user,
            recipient=self.user,
            message="user02回复给user01的私信"
        )

    def test_user_messages(self):
        """user01的私信"""
        response = self.client.get(reverse("messager:messages_list"))
        assert response.status_code == 200
        assert str(response.context["message"]) == "user01发送给user02的第一条私信"
        assert str(response.context["active"]) == Message.objects.get_most_recent_conversation(self.user).username
        assert str(response.context["active"]) == "user02"

    def test_user_conversation(self):
        """私信会话"""
        response = self.client.get(reverse("messager:conversation_detail", kwargs={"username": self.user.username}))
        assert response.status_code == 200
        assert str(response.context["active"]) == "user01"

    def test_send_message_view(self):
        """发送私信"""
        message_count = Message.objects.count()
        request = self.client.post(
            reverse("messager:send_message"),
            {"to": "user02", "message": "私信内容"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert request.status_code == 200
        new_msm_count = Message.objects.count()
        assert new_msm_count == message_count + 1

    def test_wrong_requests_send_message(self):
        """使用错误的请求方式发送私信"""
        get_request = self.client.get(
            reverse("messager:send_message"),
            {"to": "user02", "message": "私信内容 AJAX-GET"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        no_ajax_request = self.client.get(
            reverse("messager:send_message"),
            {"to": "user02", "message": "私信内容 HTTP-GET"}
        )
        same_user_request = self.client.post(
            reverse("messager:send_message"),
            {"to": "user02", "message": "私信内容 AJAX-POST"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        no_length_request = self.client.post(
            reverse("messager:send_message"),
            {"to": "user02", "message": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        # 状态码为405表示请求的方式不对
        assert get_request.status_code == 405
        # 状态码为405表示 异常请求
        assert no_ajax_request.status_code == 400
        assert same_user_request.status_code == 200
        assert no_length_request.status_code == 200
