#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = '__Miles__'

from django.http import HttpResponseBadRequest
from functools import wraps
from django.views.generic import View
from django.core.exceptions import PermissionDenied


# 验证是否为ajax请求
def ajax_required(f):
    # 为不改变返回函数的名字和返回信息 使用装饰器 @wraps(f)
    @wraps(f)
    def wrap(request, *args, **kwargs):
        # request.is_ajax()判断是否为AJAX请求
        if not request.is_ajax():
            return HttpResponseBadRequest("不是AJAX请求")

        return f(request, *args, **kwargs)

    return wrap


class AuthorRequiredMixin(View):
    """
    验证是否为原作者，用于状态删除，以及文章编辑
    """
    def dispatch(self, request, *args, **kwargs):
        # 状态和文章都有user
        # 如果实例对象中的user的用户名 不等于 request请求中用户相同
        if self.get_object().user.username != self.request.user.username:
            # 报错请求不允许
            raise PermissionDenied
        # 如果是作者，重载父类方法 并返回
        return super(AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
