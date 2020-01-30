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


# 自定义QuerySet,提高模型类的可用性
@python_2_unicode_compatible
class ArticleQuerySet(models.query.QuerySet):

    # 获取已发表的文章
    def get_published(self):
        return self.filter(status="P").select_related('user')

    # 获取草稿箱的文章
    def get_drafts(self):
        return self.filter(status="D").select_related('user')

    # 需求分析时 ，统计所有已发表的文章中每一个标签的数量
    def get_counted_tags(self):
        tag_dict = {}
        # self.get_publisher()->获取已发表的文章
        # .filter(tag__gt=0) 表示过滤小于等于0的标签
        # annotate(tagged=models.Count("tags")) 表示根据tags 聚合分组
        # query = self.get_published().annotate(tagged=models.Count("tags")).filter(tags__gt=0)
        for obj in self.all():
            for tag in obj.tags.names():
                if tag not in tag_dict:
                    tag_dict[tag] = 1
                else:
                    tag_dict[tag] += 1
        return tag_dict.items()


@python_2_unicode_compatible
class Article(models.Model):
    # Draft->草稿    Publisher -> 已发布
    STATUS = (("D", "Draft"), ("P", "Published"))

    title = models.CharField(max_length=255, null=False, unique=True, verbose_name="标题")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="author", verbose_name="作者")
    image = models.ImageField(upload_to="articles_pictures/%Y/%m/%d/", verbose_name="文章图片")
    slug = models.SlugField(max_length=255, null=True, blank=True, verbose_name="(URL)别名")
    status = models.CharField(max_length=1, choices=STATUS, default="D", verbose_name="状态")
    # content = models.TextField(verbose_name="内容")
    content = MarkdownxField(verbose_name="内容")
    edited = models.BooleanField(default=False, verbose_name="是否可编辑")
    tags = TaggableManager(help_text="多个标签使用,(英文)隔开", verbose_name="标签")
    created_at = models.DateTimeField(db_index=True, auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ('created_at',)

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # self.slug = slugify(self.title)
        # super(Article, self).save()
        if not self.slug:
            # 根据作者和标题生成文章在URL中的别名
            self.slug = slugify(self.title)
        super(Article, self).save()

    # 将markdown文本转换为html
    def get_markdown(self):
        return markdownify(self.content)

