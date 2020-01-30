#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.db import models
# 标签(slug)管理包
from slugify import slugify
from taggit.managers import TaggableManager

# markdownx
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

import uuid
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

# 计数类
from collections import Counter


@python_2_unicode_compatible
class Vote(models.Model):
    """使用Django中的ContentType，同时关联用户对问题和回答的投票"""
    uuid_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="qa_vote", on_delete=models.CASCADE,
                             verbose_name="用户")
    value = models.BooleanField(default=True, verbose_name="点赞或踩")
    # GenericForeignKey设置
    content_type = models.ForeignKey(ContentType, related_name="vote_on", on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    vote = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = "投票"
        verbose_name_plural = verbose_name
        # 联合唯一键 -> user某一用户只能给 content_type某一模型类 中object_id 某一条数据点赞或踩
        unique_together = ("user", "content_type", "object_id")
        # 联合唯一索引 SQL优化
        index_together = ("content_type", "object_id")


# 自定义QuerySet,提高模型类的可用性
@python_2_unicode_compatible
class QuestionQuerySet(models.query.QuerySet):

    # # 已有答案的问题
    # def get_published(self):
    #     return self.filter(has_answer=True)
    #
    # # 未回答的问题
    # def get_drafts(self):
    #     return self.filter(has_answer=True)

    def get_answered(self):
        """已有答案的问题"""
        return self.filter(has_answer=True).select_related('user')

    def get_unanswered(self):
        """未被的回答的问题"""
        return self.filter(has_answer=False).select_related('user')

    # 统计所有已发表的问题中每一个标签的数量
    def get_counted_tags(self):
        tag_dict = {}
        # self.get_publisher()->获取已发表的文章
        # .filter(tag__gt=0) 表示过滤小于等于0的标签
        # annotate(tagged=models.Count("tags")) 表示根据tags 聚合分组
        # query = self.all().annotate(tagged=models.Count("tags")).filter(tags__gt=0)
        for obj in self.all():
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


@python_2_unicode_compatible
class Question(models.Model):
    # Draft->草稿    Publisher -> 已发布
    STATUS = (("O", "Open"), ("C", "Close"), ("D", "Draft"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="q_author", verbose_name="提问者")
    title = models.CharField(max_length=255, unique=True, verbose_name="标题")
    slug = models.SlugField(max_length=80, null=True, blank=True, verbose_name='(URL)别名')
    status = models.CharField(max_length=1, choices=STATUS, default="O", verbose_name="问题状态")
    content = MarkdownxField(verbose_name="内容")
    tags = TaggableManager(help_text="多个标签使用,(英文)隔开", verbose_name="标签")
    # 通过GenericRelation关联到Vote表，不是实际的字段
    votes = GenericRelation(Vote, verbose_name="投票情况")
    has_answer = models.BooleanField(default=False, verbose_name="接受回答")

    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = "问题"
        verbose_name_plural = verbose_name
        ordering = ('-updated_at', '-created_at')

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Question, self).save()

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """总票数"""
        # self.votes.values_list 相当于 Vote.objects.values_list()
        dic = Counter(self.votes.values_list("value", flat=True))
        return dic[True] - dic[False]

    # 获取所有回答
    def get_answers(self):
        # self为参数表示当前问题有多少回答
        return Answer.objects.filter(question=self).prefetch_related('user', 'question')

    # 回答的数量
    def count_answers(self):
        return self.get_answers().count()

    def get_upvoters(self):
        """赞同用户"""
        # return [vote.user for vote in self.votes.filter(value=True)]
        return [vote.user for vote in self.votes.filter(value=True).select_related('user').prefetch_related('vote')]

    def get_downvoters(self):
        """踩的用户"""
        # return [vote.user for vote in self.votes.filter(value=False)]
        return [vote.user for vote in self.votes.filter(value=False).select_related('user').prefetch_related('vote')]

    # 获取问题接受的回答
    def get_accepted_answer(self):
        return Answer.objects.get(question=self, is_answer=True)


@python_2_unicode_compatible
class Answer(models.Model):
    uuid_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="a_author", verbose_name="问题回答者")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="")
    content = MarkdownxField(verbose_name="回答的特容")
    is_answer = models.BooleanField(default=False, verbose_name="回答是否呗接受")
    votes = GenericRelation(Vote, verbose_name='投票情况')
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = "回答"
        verbose_name_plural = verbose_name
        # 多字段排序
        ordering = ('-is_answer', '-created_at')

    def __str__(self):
        return self.content

    def get_markdown(self):
        return markdownify(self.content)

    def total_votes(self):
        """总票数"""
        # self.votes.value_list 相当于 Vote.objects.value_list()
        dic = Counter(Vote.objects.values_list("value", flat=True))
        return dic[True] - dic[False]

    def get_upvoters(self):
        """赞同用户"""
        # return [vote.user for vote in self.votes.filter(value=True)]
        return [vote.user for vote in self.votes.filter(value=True).select_related('user').prefetch_related('vote')]

    def get_downvoters(self):
        """踩的用户"""
        # return [vote.user for vote in self.votes.filter(value=False)]
        return [vote.user for vote in self.votes.filter(value=False).select_related('user').prefetch_related('vote')]

    # 获取问题接受的回答
    def get_accepted_answer(self):
        return Answer.objects.get(question=self, is_answer=True)

    # 采纳回答
    def accept_answer(self):
        # 当一个问题有多个回答时，只接受一个答案，其他答案不接受
        answer_set = Answer.objects.filter(question=self.question)  # 查询当前所有答案
        answer_set.update(is_answer=False)  # 一律设为未接受
        # 接受当前回答并保存
        self.is_answer = True
        self.save()
        # 该问题已有呗接受的答案
        self.question.has_answer = True
        self.question.save()
