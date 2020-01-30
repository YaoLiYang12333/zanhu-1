#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse



# from django.utils.translation import ugettext_lazy as _ 自动生成的弃用

# 使项目适应不同环境，python2.x 向python3 一样处理各种unicode字符
@python_2_unicode_compatible
class User(AbstractUser):
    '''
    自定义邮箱模型
    '''
    nickname = models.CharField(null=True, blank=True, max_length=255, verbose_name='昵称')
    job_title = models.CharField(max_length=50, null=True, blank=True, verbose_name='职称')
    introduction = models.TextField(blank=True, null=True, verbose_name='简介')
    picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name='头像')
    location = models.CharField(max_length=50, null=True, blank=True, verbose_name='城市')
    personal_url = models.URLField(max_length=555, blank=True, null=True, verbose_name='个人链接')
    weibo = models.URLField(max_length=255, blank=True, null=True, verbose_name='微博链接')
    zhihu = models.URLField(max_length=255, blank=True, null=True, verbose_name='知乎链接')
    github = models.URLField(max_length=255, blank=True, null=True, verbose_name='Github链接')
    linkedin = models.URLField(max_length=255, blank=True, null=True, verbose_name='LinkedIn链接')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 定义表名字 和复数形式名字
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        # 为AbstractUser 中内置定义的  是唯一键
        return self.username

    def get_absolute_url(self):
        # 框架自动生成 用于返回用户详情页中的路径
        return reverse("users:detail", kwargs={"username": self.username})

    def get_profile_name(self):
        # 用于个人信息中返回用户的名字
        if self.nickname:
            return self.nickname
        return self.username
