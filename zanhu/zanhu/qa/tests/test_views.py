#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"


"""
使用TestClient和RequestFactory测试视图的区别
TestClient: 走Django框架的整个请求响应流程，经过WSGI handler、中间件、URL路由、
上下文处理器，返回response，更像是集成测试。特点：使用简单，测试一步到位。
测试用例运行慢，依赖于中间件、URL路由等其它部分

RequestFactory: 生成WSGIRequest供使用，与Django代码无关，单元测试的最佳实践，但使用难度高
"""

# from django.test import Client
# from django.urls import reverse
# from test_plus.test import TestCase
#
# from zanhu.qa.models import Question, Answer
#
#
# class QAViewsTest(TestCase):
#     def setUp(self):
#         self.user = self.make_user("user01")
#         self.other_user = self.make_user("user02")
#         self.client = Client()
#         self.other_client = Client()
#         self.client.login(username="user01", password="password")
#         self.other_client.login(username="user02", password="password")
#         self.question_one = Question.objects.create(
#             user=self.user,
#             title="问题1",
#             content="问题1的内容",
#             tags="测试1, 测试2"
#         )
#         self.question_two = Question.objects.create(
#             user=self.user,
#             title="问题2",
#             content="问题2的内容",
#             has_answer=True,
#             tags="测试1, 测试2"
#         )
#         self.answer = Answer.objects.create(
#             user=self.user,
#             question=self.question_two,
#             content="问题2被采纳的回答",
#             is_answer=True
#         )
#
#     def test_index_questions(self):
#         response = self.client.get(reverse("qa:all_q"))
#         assert response.status_code == 200
#         assert "问题1" in str(response.context["questions"])
#
#     def test_create_question_view(self):
#         current_count = Question.objects.count()
#         response = self.client.post(reverse("qa:ask_question"),
#                                     {"title": "问题标题",
#                                      "content": "问题内容",
#                                      "status": "O",
#                                      "tags": "测试标签"})
#         assert response.status_code == 302
#         new_question = Question.objects.first()
#         assert new_question.title == "问题标题"
#         assert Question.objects.count() == current_count + 1
#
#     def test_answered_questions(self):
#         response = self.client.get(reverse("qa:answered_q"))
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue("问题2" in str(response.context["questions"]))
#
#     def test_unanswered_questions(self):
#         response = self.client.get(reverse("qa:unanswered_q"))
#         assert response.status_code == 200
#         assert "问题1" in str(response.context["questions"])
#
#     def test_answer_question(self):
#         current_answer_count = Answer.objects.count()
#         response = self.client.post(
#             reverse("qa:propose_answer", kwargs={"question_id": self.question_one.id}), {"content": "问题1的回答"}
#         )
#         assert response.status_code == 302
#         assert Answer.objects.count() == current_answer_count + 1
#
#     def test_question_upvote(self):
#         """赞同问题"""
#         response_one = self.client.post(
#             reverse("qa:question_vote"),
#             {"value": "U", "question": self.question_one.id},
#             HTTP_X_REQUESTED_WITH="XMLHttpRequest"
#         )
#         assert response_one.status_code == 200
#
#     def test_question_downvote(self):
#         """反对问题"""
#         response_one = self.client.post(
#             reverse("qa:question_vote"),
#             {"value": "D", "question": self.question_one.id},
#             HTTP_X_REQUESTED_WITH="XMLHttpRequest")
#         assert response_one.status_code == 200
#
#     def test_answer_upvote(self):
#         """赞同回答"""
#         response_one = self.client.post(
#             reverse("qa:answer_vote"),
#             {"value": "U", "answer": self.answer.uuid_id},
#             HTTP_X_REQUESTED_WITH="XMLHttpRequest")
#         assert response_one.status_code == 200
#
#     def test_answer_downvote(self):
#         """反对回答"""
#         response_one = self.client.post(
#             reverse("qa:answer_vote"),
#             {"value": "D", "answer": self.answer.uuid_id},
#             HTTP_X_REQUESTED_WITH="XMLHttpRequest")
#         assert response_one.status_code == 200
#
#     def test_accept_answer(self):
#         """接受回答"""
#         response_one = self.client.post(
#             reverse("qa:accept_answer"),
#             {"answer": self.answer.uuid_id},
#             HTTP_X_REQUESTED_WITH="XMLHttpRequest")
#         assert response_one.status_code == 200

import json
from django.test import RequestFactory
from test_plus.test import CBVTestCase
from zanhu.qa.models import Question, Answer
from zanhu.qa import views

# 去点message
from django.contrib.messages.storage.fallback import FallbackStorage


# 基类
class BaseQATest(CBVTestCase):
    def setUp(self):
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")
        self.question_one = Question.objects.create(
            user=self.user,
            title="问题1",
            content="问题1的内容",
            tags="测试1, 测试2"
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title="问题2",
            content="问题2的内容",
            has_answer=True,
            tags="测试1, 测试2"
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content="问题2被采纳的回答",
            is_answer=True
        )
        # 生成request.get 请求  | /fake-url 地址无所谓 因为不经过路由
        self.request = RequestFactory().get('/fake-url')
        # 网站要求用户登录 将用户放入 请求中
        self.request.user = self.user


class TestQuestionListView(BaseQATest):
    """测试问题列表"""

    # 测试返回的上下文
    def test_context_data(self):
        # get 函数要求参数： def get(self, cls, *args, **kwargs)
        # 将request=self.request 请求传递给  views.QuestionListView视图
        response = self.get(views.QuestionListView, request=self.request)

        # 断言 响应状态码status_code为 200
        self.assertEqual(response.status_code, 200)

        # 断言 查询集是否相等  ordered=False 不考虑顺序
        # response.context_data['questions'] 拿到queryset查询集对象 然后循环和self.question_one self.question_two对比
        self.assertQuerysetEqual(response.context_data['questions'],
                                 # [repr(self.question_one), repr(self.question_two)], ordered=False)
                                 map(repr, [self.question_one, self.question_two]), ordered=False)
        # 第二种断言上下文方法
        self.assertTrue(all(a == b for
                            a, b in zip(response.context_data['questions'], Question.objects.all())))
        # 断言 上下文
        self.assertContext("active", "all")
        self.assertContext("popular_tags", Question.objects.get_counted_tags())


class TestAnsweredQuestionListView(BaseQATest):
    """测试已回答的问题列表"""

    def test_context_data(self):
        # response1 = self.get(views.AnsweredQuestionListView, request=self.request)
        # 第二种写法
        response2 = views.AnsweredQuestionListView.as_view()(self.request)
        # 断言 响应状态码status_code为 200
        # self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertQuerysetEqual(response2.context_data['questions'],
                                 [repr(self.question_two)])

        # 如果使用 第二种写法 只能用 response 来获取回答
        self.assertEqual(response2.context_data["active"], "answered")


class TestUnansweredQuestionListView(BaseQATest):
    """测试已回答的问题列表"""

    def test_context_data(self):
        response = self.get(views.UnansweredQuestionListView, request=self.request)

        # 判断响应 状态码为200 方式一
        self.assertEqual(response.status_code, 200)
        # 判断响应 状态码为200 方式二
        self.response_200(response)
        self.assertQuerysetEqual(response.context_data['questions'],
                                 [repr(self.question_one)])
        self.assertEqual(response.context_data["active"], "unanswered")


class TestCreateQuestionView(BaseQATest):
    """
    测试创建问题
    通用类视图测试用例 只测试结果  不测试重写的函数在 程序中流转过程
    """

    def test_get(self):
        response = self.get(views.CreateQuestionView, requesr=self.request)
        self.response_200(response)

        # 断言 返回结果是否包含关键字
        self.assertContains(response, "标题")
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")
        self.assertContains(response, "标签")

        # 类CreateView -> BaseCreateView -> ModelFormMixin -> FormMixin -> ContextMixin 中kwargs.setdefault("view",self)
        self.assertIsInstance(response.context_data["view"], views.CreateQuestionView)

    def test_post(self):
        data = {"title": "title", "content": "content", "tags": "tags1,tags2", "status": "O"}
        # 创造post请求 | 此处url 随意写 数据不能随意写
        request = RequestFactory().post("/test", data=data)
        request.user = self.user

        # RequestFactory测试含有django.contrib.messages的视图 https://code.djangoproject.com/ticket/17971
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateQuestionView, request=request)
        assert response.status_code == 302
        assert response.url == '/qa/'


class TestQuestionDetail(BaseQATest):
    """测试问题详情"""

    def test_context_data(self):
        response = self.get(views.QuestionDetailView, request=self.request, pk=self.question_one.id)
        self.response_200(response)
        self.assertEqual(response.context_data["question"], self.question_one)


class TestCreateAnswerDetail(BaseQATest):
    """测试创建回答"""

    def test_get(self):
        response = self.get(views.CreateAnswerView, request=self.request, question_id=self.question_one.id)
        self.response_200(response)
        self.assertContains(response, "编辑")
        self.assertContains(response, "预览")
        self.assertIsInstance(response.context_data["view"], views.CreateAnswerView)

    def test_post(self):
        # 创造post请求 | 此处url 随意写 数据不能随意写
        data = {"content": "content"}
        request = RequestFactory().post("/fake-url", data=data)
        request.user = self.user

        # RequestFactory测试含有django.contrib.messages的视图 https://code.djangoproject.com/ticket/17971
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.post(views.CreateAnswerView, request=request, question_id=self.question_one.id)
        assert response.status_code == 302
        # python 3.6 新特性
        assert response.url == f'/qa/question-detail/{self.question_one.id}/'


class TestQAVote(BaseQATest):

    def setUp(self):
        super(TestQAVote, self).setUp()
        # HTTP_X_REQUESTED_WITH = 'XMLHttpRequest' 将请求方式改为Ajax
        self.request = RequestFactory().post('/fake-url', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # QueryDict instance is immutable, request.POST是QueryDict对象，不可变 | 复制一份
        self.request.POST = self.request.POST.copy()

        self.request.user = self.other_user

    def test_question_upvote(self):
        """赞同问题"""
        self.request.POST['question'] = self.question_one.id
        self.request.POST['value'] = 'U'

        response = views.question_vote(self.request)

        assert response.status_code == 200
        # 因为返回的是JsonResponse
        assert json.loads(response.content)['votes'] == 1

    def test_question_downvote(self):
        """反对问题"""
        self.request.POST['question'] = self.question_two.id
        self.request.POST['value'] = 'D'

        response = views.question_vote(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == -1

    def test_answer_upvote(self):
        """赞同问答"""
        self.request.POST['answer'] = self.answer.uuid_id
        self.request.POST['value'] = 'U'

        response = views.answer_vote(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == 1

    def test_answer_downvote(self):
        """反对回答"""
        self.request.POST['answer'] = self.answer.uuid_id
        self.request.POST['value'] = 'D'

        response = views.answer_vote(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['votes'] == -1

    def test_accept_answer(self):
        """接受回答"""

        self.request.user = self.user  # self.user是提问者
        self.request.POST['answer'] = self.answer.uuid_id

        response = views.accept_answer(self.request)

        assert response.status_code == 200
        assert json.loads(response.content)['status'] == 'true'
