from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from auth_app.models import UserProfile
from form.models import Form
from history.models import History

from .models import ChatItem


class ChatCreateTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester")
        self.other_user = User.objects.create_user(username="other")
        UserProfile.objects.create(
            user=self.user,
            google_sub="google-sub-tester",
            language="ja",
            name="Tester",
        )
        self.form = Form.objects.create(
            user=self.user,
            answers=[
                {
                    "question": "What food do you like?",
                    "answer": "Kimchi jjigae",
                }
            ],
            target_name="Yuna",
            culture_base="ko",
        )
        self.other_form = Form.objects.create(
            user=self.other_user,
            answers=[],
            target_name="Other",
            culture_base="ja",
        )
        self.url = reverse("chat-new")
        self.valid_payload = {
            "formId": self.form.id,
            "question": "What should I say next?",
        }
        self.history = History.objects.create(
            user=self.user,
            target_name="Yuna",
            received=True,
            value=50000,
            culture_base="ko",
            category="Money",
            date=date(2026, 5, 16),
        )
        History.objects.create(
            user=self.user,
            target_name="Different target",
            received=False,
            value=70000,
            culture_base="ja",
            category="Filtered out",
            date=date(2026, 5, 17),
        )
        History.objects.create(
            user=self.other_user,
            target_name="Yuna",
            received=True,
            value=90000,
            culture_base="ko",
            category="Other user",
            date=date(2026, 5, 18),
        )

    def test_authenticated_user_can_create_chat_item(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["status"], ChatItem.Status.SUCCESS)
        self.assertEqual(data["answer"], "Test Success! This is gemini answer")

        chat_item = ChatItem.objects.get(id=data["chatItemId"])
        self.assertEqual(chat_item.form, self.form)
        self.assertEqual(chat_item.question, self.valid_payload["question"])
        self.assertEqual(chat_item.answer, data["answer"])
        self.assertEqual(chat_item.status, ChatItem.Status.SUCCESS)

    @patch("chat.views.get_gemini_answer")
    def test_chat_create_passes_language_histories_question_and_empty_memory(
        self,
        mock_answer,
    ):
        mock_answer.return_value = (True, "Gemini answer")
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        mock_answer.assert_called_once()
        language, histories, question, memory = mock_answer.call_args.args
        self.assertEqual(language, "ja")
        self.assertEqual(
            histories,
            [
                {
                    "targetName": self.history.target_name,
                    "received": self.history.received,
                    "value": self.history.value,
                    "cultureBase": self.history.culture_base,
                    "category": self.history.category,
                    "date": self.history.date.isoformat(),
                }
            ],
        )
        self.assertEqual(question, self.valid_payload["question"])
        self.assertEqual(memory, "")

    @patch("chat.views.get_gemini_answer")
    def test_chat_create_builds_memory_from_previous_success_chat_items(
        self,
        mock_answer,
    ):
        mock_answer.return_value = (True, "Next answer")
        first_chat = ChatItem.objects.create(
            form=self.form,
            question='[{"question":"질문", "answer":"답변"}]',
            answer="Gemini 답변",
            status=ChatItem.Status.SUCCESS,
        )
        second_chat = ChatItem.objects.create(
            form=self.form,
            question="사용자 입력 질문1",
            answer="Gemini 답변 1",
            status=ChatItem.Status.SUCCESS,
        )
        ChatItem.objects.create(
            form=self.form,
            question="아직 처리 중인 질문",
            answer="",
            status=ChatItem.Status.PENDING,
        )
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        memory = mock_answer.call_args.args[3]
        self.assertIn("사전 질문:", memory)
        self.assertIn(first_chat.question, memory)
        self.assertIn(first_chat.answer, memory)
        self.assertIn("추가 질문:", memory)
        self.assertIn(second_chat.question, memory)
        self.assertIn(second_chat.answer, memory)
        self.assertNotIn("아직 처리 중인 질문", memory)

    def test_anonymous_user_cannot_create_chat_item(self):
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(ChatItem.objects.count(), 0)

    def test_user_cannot_create_chat_item_for_other_users_form(self):
        self.client.force_login(self.user)
        payload = {**self.valid_payload, "formId": self.other_form.id}

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(ChatItem.objects.count(), 0)

    def test_form_id_is_required(self):
        self.client.force_login(self.user)
        payload = dict(self.valid_payload)
        payload.pop("formId")

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(ChatItem.objects.count(), 0)

    def test_question_is_required(self):
        self.client.force_login(self.user)
        payload = dict(self.valid_payload)
        payload.pop("question")

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(ChatItem.objects.count(), 0)

    def test_blank_question_is_invalid(self):
        self.client.force_login(self.user)
        payload = {**self.valid_payload, "question": "   "}

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(ChatItem.objects.count(), 0)

    @patch("chat.views.get_gemini_answer")
    def test_chat_item_remains_pending_when_answer_generation_fails(self, mock_answer):
        mock_answer.side_effect = RuntimeError("temporary failure")
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["success"], False)
        self.assertEqual(data["status"], ChatItem.Status.PENDING)

        chat_item = ChatItem.objects.get(id=data["chatItemId"])
        self.assertEqual(chat_item.status, ChatItem.Status.PENDING)
        self.assertEqual(chat_item.answer, "")

    @patch("chat.views.get_gemini_answer")
    def test_chat_item_remains_pending_when_answer_generation_returns_false(
        self,
        mock_answer,
    ):
        mock_answer.return_value = (False, "temporary failure")
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertEqual(data["success"], False)
        self.assertEqual(data["status"], ChatItem.Status.PENDING)
        self.assertEqual(data["detail"], "temporary failure")

        chat_item = ChatItem.objects.get(id=data["chatItemId"])
        self.assertEqual(chat_item.status, ChatItem.Status.PENDING)
        self.assertEqual(chat_item.answer, "")


class ChatListTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester")
        self.other_user = User.objects.create_user(username="other")
        self.form = Form.objects.create(
            user=self.user,
            answers=[],
            target_name="Yuna",
            culture_base="ko",
        )
        self.other_form = Form.objects.create(
            user=self.other_user,
            answers=[],
            target_name="Other",
            culture_base="ja",
        )
        self.first_chat = ChatItem.objects.create(
            form=self.form,
            question="First question",
            answer="First answer",
            status=ChatItem.Status.SUCCESS,
        )
        self.second_chat = ChatItem.objects.create(
            form=self.form,
            question="Second question",
            answer="",
            status=ChatItem.Status.PENDING,
        )
        ChatItem.objects.create(
            form=self.other_form,
            question="Other question",
            answer="Other answer",
            status=ChatItem.Status.SUCCESS,
        )
        self.url = reverse("chat-list")

    def test_authenticated_user_can_list_chat_items_for_own_form(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url, {"formId": self.form.id})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["chatItems"]), 2)
        self.assertEqual(data["chatItems"][0]["chatItemId"], self.first_chat.id)
        self.assertEqual(data["chatItems"][0]["formId"], self.form.id)
        self.assertEqual(data["chatItems"][0]["question"], self.first_chat.question)
        self.assertEqual(data["chatItems"][0]["answer"], self.first_chat.answer)
        self.assertEqual(data["chatItems"][0]["status"], ChatItem.Status.SUCCESS)
        self.assertEqual(data["chatItems"][1]["chatItemId"], self.second_chat.id)
        self.assertEqual(data["chatItems"][1]["status"], ChatItem.Status.PENDING)

    def test_anonymous_user_cannot_list_chat_items(self):
        response = self.client.get(self.url, {"formId": self.form.id})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["success"], False)

    def test_form_id_is_required_to_list_chat_items(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)

    def test_user_cannot_list_chat_items_for_other_users_form(self):
        self.client.force_login(self.user)

        response = self.client.get(self.url, {"formId": self.other_form.id})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["success"], False)
