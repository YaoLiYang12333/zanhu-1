#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from django.apps import AppConfig


class NewsConfig(AppConfig):
    # Model class zanhu.news.models.News doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.
    # name = 'news' # 这样写报错
    name = 'zanhu.news'
    verbose_name = '赞乎'
