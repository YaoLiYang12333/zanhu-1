#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

import datetime

from haystack import indexes

# 导入需要被检索的模型类
from zanhu.news.models import News
from zanhu.articles.models import Article
from zanhu.qa.models import Question
from django.contrib.auth import get_user_model
from taggit.models import Tag


# 对Article模型类中部分字段建立索引
class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    # use_template=True 表示将结果保存到模板中 在template_name='search/articles_text.txt' 中定义要保存的结果
    # eg：{{ object.title }} 标题 {{ object.content }} 内容
    text = indexes.CharField(document=True, use_template=True, template_name='search/articles_text.txt')

    # 表示索引哪一个模型类
    def get_model(self):
        return Article

    # 当Article模型类中的索引有更新时调用
    def index_queryset(self, using=None):
        # status="P" 只对已发布的文章建立索引
        # updated_at__lte=datetime.datetime.now() 只建立当前时间之后的索引，之前已建立的索引不要再更新
        return self.get_model().objects.filter(status="P", updated_at__lte=datetime.datetime.now())


class NewsIndex(indexes.SearchIndex, indexes.Indexable):
    """对News模型类中部分字段建立索引"""
    text = indexes.CharField(document=True, use_template=True, template_name='search/news_text.txt')

    def get_model(self):
        return News

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(reply=False, updated_at__lte=datetime.datetime.now())


class QuestionIndex(indexes.SearchIndex, indexes.Indexable):
    """对Question模型类中部分字段建立索引"""
    text = indexes.CharField(document=True, use_template=True, template_name='search/questions_text.txt')

    def get_model(self):
        return Question

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    """对User模型类中部分字段建立索引"""
    text = indexes.CharField(document=True, use_template=True, template_name='search/users_text.txt')

    def get_model(self):
        return get_user_model()

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(updated_at__lte=datetime.datetime.now())


class TagsIndex(indexes.SearchIndex, indexes.Indexable):
    """对Tags模型类中部分字段建立索引"""
    text = indexes.CharField(document=True, use_template=True, template_name='search/tags_text.txt')

    def get_model(self):
        return Tag

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
