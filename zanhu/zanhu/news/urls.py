#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

from django.urls import path

from zanhu.news import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsListView.as_view(), name='list'),
    path('post-news/', views.post_news, name='post_news'),
    # 因为news表 主键为uuid str类型，如果默认则为str
    path('delete/<str:pk>/', views.NewsDeleteView.as_view(), name='delete_news'),
    path('like/', views.like, name='like_post'),
    path('get-thread/', views.get_thread, name='get_thread'),
    path('post-comment/', views.post_comment, name='post_comments'),
    # 为10-11章 WebSocket触发Ajax请求-自动更新点赞数和评论数，也是 notifications.js，
    # function update_social_activity(id_value) 的触发路由
    path('update-interactions/', views.update_interactions, name='update_interactions'),

]
