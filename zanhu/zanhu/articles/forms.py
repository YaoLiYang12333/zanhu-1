#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from django import forms
from zanhu.articles.models import Article
from markdownx.fields import MarkdownxFormField


class ArticleForm(forms.ModelForm):
    # widget=forms.HiddenInput() 对用户不可见
    status = forms.CharField(widget=forms.HiddenInput())
    # initial = False 初始值 |  required=False 不要求填写
    edited = forms.BooleanField(widget=forms.HiddenInput(), initial=False, required=False)
    content = MarkdownxFormField()

    class Meta:
        model = Article
        # 元数据中定义，可编辑字段
        fields = ["title", "content", "image", "tags"]
