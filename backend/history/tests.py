from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import History


class HistoryApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester")
        self.other_user = User.objects.create_user(username="other")
        self.valid_payload = {
            "targetName": "Hong Gil Dong",
            "received": True,
            "value": 50000,
            "currency": "ko",
            "category": "Money",
            "date": "2026-05-16",
        }
        self.history = History.objects.create(
            user=self.user,
            target_name="Hong Gil Dong",
            received=True,
            value=10000,
            currency="ko",
            category="Old money",
            date=date(2026, 5, 16),
        )
        self.second_history = History.objects.create(
            user=self.user,
            target_name="Kim Chul Soo",
            received=False,
            value=20000,
            currency="ja",
            category="Gift",
            date=date(2026, 5, 17),
        )
        self.other_history = History.objects.create(
            user=self.other_user,
            target_name="Hong Gil Dong",
            received=True,
            value=30000,
            currency="ko",
            category="Other user's money",
            date=date(2026, 5, 15),
        )

    def test_authenticated_user_can_create_history(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("history-new"),
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertIn("historyId", data)

        history = History.objects.get(id=data["historyId"])
        self.assertEqual(history.user, self.user)
        self.assertEqual(history.target_name, self.valid_payload["targetName"])
        self.assertEqual(history.received, self.valid_payload["received"])
        self.assertEqual(history.value, self.valid_payload["value"])
        self.assertEqual(history.currency, self.valid_payload["currency"])
        self.assertEqual(history.category, self.valid_payload["category"])
        self.assertEqual(history.date.isoformat(), self.valid_payload["date"])

    def test_anonymous_user_cannot_create_history(self):
        response = self.client.post(
            reverse("history-new"),
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["success"], False)

    def test_create_history_requires_fields(self):
        self.client.force_login(self.user)
        payload = dict(self.valid_payload)
        payload.pop("targetName")

        response = self.client.post(
            reverse("history-new"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)

    def test_authenticated_user_can_list_own_histories(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("history-list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(
            [history["historyId"] for history in data["histories"]],
            [self.second_history.id, self.history.id],
        )

    def test_history_list_can_filter_by_target_name(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("history-list"),
            {"targetName": "Hong Gil Dong"},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["histories"]), 1)
        self.assertEqual(data["histories"][0]["historyId"], self.history.id)
        self.assertEqual(data["histories"][0]["targetName"], "Hong Gil Dong")
        self.assertEqual(data["histories"][0]["received"], True)
        self.assertEqual(data["histories"][0]["currency"], "ko")
        self.assertEqual(data["histories"][0]["category"], "Old money")
        self.assertEqual(data["histories"][0]["date"], "2026-05-16")

    def test_anonymous_user_cannot_list_histories(self):
        response = self.client.get(reverse("history-list"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["success"], False)

    def test_authenticated_user_can_get_own_history(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("history-detail", kwargs={"history_id": self.history.id})
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["history"]["historyId"], self.history.id)
        self.assertEqual(data["history"]["targetName"], self.history.target_name)
        self.assertEqual(data["history"]["received"], self.history.received)
        self.assertEqual(data["history"]["value"], self.history.value)
        self.assertEqual(data["history"]["currency"], self.history.currency)
        self.assertEqual(data["history"]["category"], self.history.category)
        self.assertEqual(data["history"]["date"], self.history.date.isoformat())

    def test_user_cannot_get_other_users_history(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("history-detail", kwargs={"history_id": self.other_history.id})
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["success"], False)

    def test_authenticated_user_can_update_own_history(self):
        self.client.force_login(self.user)
        payload = {
            "targetName": "Hong Gil Dong",
            "received": False,
            "value": 70000,
            "currency": "ja",
            "category": "Updated money",
            "date": "2026-05-18",
        }

        response = self.client.post(
            reverse("history-detail", kwargs={"history_id": self.history.id}),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["history"]["received"], False)
        self.assertEqual(data["history"]["value"], 70000)
        self.assertEqual(data["history"]["currency"], "ja")
        self.assertEqual(data["history"]["category"], "Updated money")
        self.assertEqual(data["history"]["date"], "2026-05-18")

        self.history.refresh_from_db()
        self.assertEqual(self.history.received, False)
        self.assertEqual(self.history.value, 70000)
        self.assertEqual(self.history.currency, "ja")
        self.assertEqual(self.history.category, "Updated money")
        self.assertEqual(self.history.date.isoformat(), "2026-05-18")

    def test_update_requires_valid_payload(self):
        self.client.force_login(self.user)
        payload = {
            "targetName": "Hong Gil Dong",
            "received": True,
            "value": "not-number",
            "currency": "ko",
            "category": "Updated money",
            "date": "2026-05-18",
        }

        response = self.client.post(
            reverse("history-detail", kwargs={"history_id": self.history.id}),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["success"], False)

    def test_user_cannot_update_other_users_history(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("history-detail", kwargs={"history_id": self.other_history.id}),
            data=self.valid_payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["success"], False)

    def test_authenticated_user_can_delete_own_history(self):
        self.client.force_login(self.user)

        response = self.client.delete(
            reverse("history-detail", kwargs={"history_id": self.history.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        self.assertFalse(History.objects.filter(id=self.history.id).exists())

    def test_user_cannot_delete_other_users_history(self):
        self.client.force_login(self.user)

        response = self.client.delete(
            reverse("history-detail", kwargs={"history_id": self.other_history.id})
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["success"], False)
        self.assertTrue(History.objects.filter(id=self.other_history.id).exists())
