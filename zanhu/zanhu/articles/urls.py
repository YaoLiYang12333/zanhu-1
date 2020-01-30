#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from django.urls import path
from django.views.decorators.cache import cache_page
from zanhu.articles import views

app_name = 'articles'

urlpatterns = [
    path('', views.ArticlesListView.as_view(), name='list'),
    path('write-new-article/', views.ArticleCreateView.as_view(), name='write_new'),
    path('drafts/', views.DraftListView.as_view(), name='drafts'),
    # 调用ArticleDetailView时 缓存5分钟
    path("<str:slug>/", views.ArticleDetailView.as_view(), name="article"),
    # path("<str:slug>/", cache_page(60 * 5)(views.ArticleDetailView.as_view()), name="article"),
    path("edit/<int:pk>/", views.ArticleEditView.as_view(), name="edit_article"),
]

