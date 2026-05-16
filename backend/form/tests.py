from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Form


class FormCreateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="tester")
        self.url = reverse("form-new")
        self.valid_payload = {
            "answers": [
                {
                    "question": "What food do you like?",
                    "answer": "Kimchi jjigae",
                }
            ],
            "targetName": "Yuna",
            "cultureBase": "ko",
        }

    def test_authenticated_user_can_create_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertIn("formId", data)

        form = Form.objects.get(id=data["formId"])
        self.assertEqual(form.user, self.user)
        self.assertEqual(form.answers, self.valid_payload["answers"])
        self.assertEqual(form.target_name, self.valid_payload["targetName"])
        self.assertEqual(form.culture_base, self.valid_payload["cultureBase"])

    def test_anonymous_user_cannot_create_form(self):
        response = self.client.post(
            self.url,
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(Form.objects.count(), 0)

    def test_answers_must_be_array(self):
        self.client.force_login(self.user)
        payload = {**self.valid_payload, "answers": "not-array"}

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(Form.objects.count(), 0)

    def test_answers_items_must_have_string_question_and_answer(self):
        self.client.force_login(self.user)
        payload = {**self.valid_payload, "answers": [{"question": "Q"}]}

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(Form.objects.count(), 0)

    def test_target_name_is_required(self):
        self.client.force_login(self.user)
        payload = dict(self.valid_payload)
        payload.pop("targetName")

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(Form.objects.count(), 0)

    def test_culture_base_is_required(self):
        self.client.force_login(self.user)
        payload = dict(self.valid_payload)
        payload.pop("cultureBase")

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)
        self.assertEqual(Form.objects.count(), 0)


class FormReadTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester")
        self.other_user = User.objects.create_user(username="other")
        self.first_form = Form.objects.create(
            user=self.user,
            answers=[
                {
                    "question": "First question",
                    "answer": "First answer",
                }
            ],
            target_name="Yuna",
            culture_base="ko",
        )
        self.second_form = Form.objects.create(
            user=self.user,
            answers=[
                {
                    "question": "Second question",
                    "answer": "Second answer",
                }
            ],
            target_name="Haruto",
            culture_base="ja",
        )
        self.other_form = Form.objects.create(
            user=self.other_user,
            answers=[],
            target_name="Other",
            culture_base="ko",
        )

    def test_authenticated_user_can_list_own_forms(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("form-list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        form_ids = {form["formId"] for form in data["forms"]}
        self.assertEqual(form_ids, {self.first_form.id, self.second_form.id})
        self.assertNotIn(self.other_form.id, form_ids)

    def test_anonymous_user_cannot_list_forms(self):
        response = self.client.get(reverse("form-list"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["success"], False)

    def test_authenticated_user_can_get_own_form_detail(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("form-detail", kwargs={"form_id": self.first_form.id})
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["form"]["formId"], self.first_form.id)
        self.assertEqual(data["form"]["answers"], self.first_form.answers)
        self.assertEqual(data["form"]["targetName"], self.first_form.target_name)
        self.assertEqual(data["form"]["cultureBase"], self.first_form.culture_base)

    def test_user_cannot_get_other_users_form_detail(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("form-detail", kwargs={"form_id": self.other_form.id})
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["success"], False)

    def test_anonymous_user_cannot_get_form_detail(self):
        response = self.client.get(
            reverse("form-detail", kwargs={"form_id": self.first_form.id})
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["success"], False)
