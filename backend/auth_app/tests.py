from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.test import TestCase
from django.urls import resolve, reverse

from .models import UserProfile
from .views import CallbackView, LoginView, LogoutView, ProfileView, RegisterView


class AuthTests(TestCase):
    def test_auth_urls_are_root_level(self):
        self.assertEqual(resolve("/auth/login").func.view_class, LoginView)
        self.assertEqual(resolve("/auth/callback").func.view_class, CallbackView)
        self.assertEqual(resolve("/auth/register").func.view_class, RegisterView)
        self.assertEqual(resolve("/auth/logout").func.view_class, LogoutView)
        self.assertEqual(resolve("/auth/profile").func.view_class, ProfileView)

    @override_settings(
        GOOGLE_OAUTH_CLIENT_ID="client-id",
        GOOGLE_OAUTH_REDIRECT_URI="http://testserver/auth/callback",
    )
    def test_google_login_redirects_to_google(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("https://accounts.google.com/"))
        self.assertIn("client_id=client-id", response["Location"])
        self.assertIn(
            "redirect_uri=http%3A%2F%2Ftestserver%2Fauth%2Fcallback",
            response["Location"],
        )

    @override_settings(FRONTEND_AUTH_CALLBACK_URL="http://frontend.test/auth/callback")
    def test_google_callback_without_code_redirects_to_frontend_error(self):
        response = self.client.get(reverse("callback"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("success=False", response["Location"])

    def test_google_login_does_not_accept_post(self):
        response = self.client.post(
            reverse("login"),
            {"code": "google-auth-code"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 405)

    @patch("auth_app.views.exchange_google_authorization_code")
    @override_settings(FRONTEND_AUTH_CALLBACK_URL="http://frontend.test/auth/callback")
    def test_google_callback_redirects_has_data_false_for_new_google_user(
        self,
        exchange_code,
    ):
        exchange_code.return_value = {
            "sub": "google-sub-123",
            "email": "tester@example.com",
            "name": "Tester",
            "picture": "",
        }

        response = self.client.get(reverse("callback"), {"code": "google-auth-code"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "http://frontend.test/auth/callback?success=True&hasData=False",
        )
        exchange_code.assert_called_once_with("google-auth-code")
        self.assertEqual(
            self.client.session["pending_google_auth"]["sub"],
            "google-sub-123",
        )

    @patch("auth_app.views.exchange_google_authorization_code")
    def test_register_after_google_login(self, exchange_code):
        exchange_code.return_value = {
            "sub": "google-sub-123",
            "email": "tester@example.com",
            "name": "Tester",
            "picture": "",
        }

        self.client.get(reverse("callback"), {"code": "google-auth-code"})

        response = self.client.post(
            reverse("register"),
            {"language": "ko", "id": "janjan1234", "name": "홍길동"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

        user = get_user_model().objects.get(username="janjan1234")
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user.email, "tester@example.com")
        self.assertEqual(user.profile.google_sub, "google-sub-123")
        self.assertEqual(user.profile.language, "ko")
        self.assertEqual(user.profile.name, "홍길동")

    @patch("auth_app.views.exchange_google_authorization_code")
    @override_settings(FRONTEND_AUTH_CALLBACK_URL="http://frontend.test/auth/callback")
    def test_google_callback_redirects_has_data_true_for_existing_user(
        self,
        exchange_code,
    ):
        user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
        )
        UserProfile.objects.create(
            user=user,
            google_sub="google-sub-123",
            language="ja",
            name="Tester",
        )
        exchange_code.return_value = {
            "sub": "google-sub-123",
            "email": "tester@example.com",
            "name": "Tester",
            "picture": "",
        }

        login_response = self.client.get(
            reverse("callback"),
            {"code": "google-auth-code"},
        )

        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(
            login_response["Location"],
            "http://frontend.test/auth/callback?success=True&hasData=True",
        )
        profile_response = self.client.get(reverse("profile"))
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(profile_response.json()["user"]["username"], "tester")

    def test_logout_returns_success(self):
        logout_response = self.client.post(reverse("logout"))
        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(logout_response.json(), {"success": True})

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])

    def test_profile_returns_current_user(self):
        user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
        )
        UserProfile.objects.create(
            user=user,
            google_sub="google-sub-123",
            language="ko",
            name="테스터",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        self.assertEqual(response.json()["user"]["username"], "tester")
        self.assertEqual(response.json()["user"]["email"], "tester@example.com")
        self.assertEqual(response.json()["user"]["name"], "테스터")
        self.assertEqual(response.json()["user"]["language"], "ko")

    def test_profile_can_update_language_and_name(self):
        user = get_user_model().objects.create_user(
            username="tester",
            email="tester@example.com",
        )
        profile = UserProfile.objects.create(
            user=user,
            google_sub="google-sub-123",
            language="ko",
            name="테스터",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("profile"),
            {"language": "en", "name": "전우치"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

        profile.refresh_from_db()
        self.assertEqual(profile.language, "en")
        self.assertEqual(profile.name, "전우치")

    def test_profile_update_requires_authentication(self):
        response = self.client.post(
            reverse("profile"),
            {"language": "en", "name": "전우치"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()["success"])

    def test_profile_update_rejects_invalid_language(self):
        user = get_user_model().objects.create_user(username="tester")
        UserProfile.objects.create(
            user=user,
            google_sub="google-sub-123",
            language="ko",
            name="테스터",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("profile"),
            {"language": "fr", "name": "전우치"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_profile_update_requires_name(self):
        user = get_user_model().objects.create_user(username="tester")
        UserProfile.objects.create(
            user=user,
            google_sub="google-sub-123",
            language="ko",
            name="테스터",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("profile"),
            {"language": "en"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
