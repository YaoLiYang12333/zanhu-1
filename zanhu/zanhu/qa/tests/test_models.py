#!/usr/bin/python3
# -*- coding:utf-8 -*-
# __author__ = "__Miles__"

from test_plus.test import TestCase
from zanhu.qa.models import Question, Answer, Vote


class QAModelTest(TestCase):
    def setUp(self):
        self.user = self.make_user("user01")
        self.other_user = self.make_user("user02")
        self.question_one = Question.objects.create(
            user=self.user,
            title="问题1",
            content="问题1的内容",
            tags="测试1,测试2"
        )
        self.question_two = Question.objects.create(
            user=self.user,
            title="问题2",
            content="问题2的内容",
            tags="测试1,测试2",
            has_answer=True
        )
        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question_two,
            content="问题2的回答",
            is_answer=True
        )

    def test_can_vote_question(self):
        """给问题投票"""
        self.question_one.votes.update_or_create(user=self.user, defaults={"value": True})
        self.question_one.votes.update_or_create(user=self.other_user, defaults={"value": True})
        # user01 user02 各投一票
        assert self.question_one.total_votes() == 2

    def test_can_vote_answer(self):
        """可以给回答投票"""
        self.answer.votes.update_or_create(user=self.user, defaults={"value": True})
        self.answer.votes.update_or_create(user=self.other_user, defaults={"value": True})
        # user01 user02 各投一票
        assert self.answer.total_votes() == 2

    def test_get_question_voters(self):
        """问题的投票用户"""
        self.question_one.votes.update_or_create(user=self.user, defaults={"value": True})
        self.question_one.votes.update_or_create(user=self.other_user, defaults={"value": False})
        assert self.user in self.question_one.get_upvoters()
        assert self.other_user in self.question_one.get_downvoters()

    def test_get_answer_voters(self):
        """回答的投票用户"""
        self.answer.votes.update_or_create(user=self.user, defaults={"value": True})
        self.answer.votes.update_or_create(user=self.other_user, defaults={"value": False})
        assert self.user in self.answer.get_upvoters()
        assert self.other_user in self.answer.get_downvoters()

    def test_unanswered_question(self):
        """未回答的问题"""
        assert self.question_one == Question.objects.get_unanswered()[0]

    def test_answered_question(self):
        """已采纳回答的问题"""
        assert self.question_two == Question.objects.get_answered()[0]

    def test_question_get_answers(self):
        """获取问题的答案"""
        assert self.answer == self.question_two.get_answers()[0]
        assert self.question_two.count_answers() == 1

    def test_question_accept_answer(self):
        """问题采纳答案"""
        # 给question_one 提交3个回答
        answer_one = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="内容1"
        )
        answer_two = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="内容2"
        )
        answer_three = Answer.objects.create(
            user=self.user,
            question=self.question_one,
            content="内容3"
        )
        # 断言answer_one、answer_two、answer_three 的is_answer 都为False
        self.assertFalse(answer_one.is_answer)
        self.assertFalse(answer_two.is_answer)
        self.assertFalse(answer_three.is_answer)
        # 断言 question_one 的has_answer(采纳的回答) 为False
        self.assertFalse(self.question_one.has_answer)
        # 接受 回答1 为正确答案
        answer_one.accept_answer()
        self.assertTrue(answer_one)
        self.assertTrue(self.question_one.has_answer)

    def test_question_str_(self):
        """测试question模型类str方法"""
        assert isinstance(self.question_one,Question)
        assert str(self.question_one) == "问题1"

    def test_answer_str_(self):
        """测试answer模型类str方法"""
        assert isinstance(self.answer, Answer)
        assert str(self.answer) == "问题2的回答"
