from django.contrib.auth import get_user_model, login, logout
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from urllib import parse
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile
from .services import GoogleAuthError, exchange_google_authorization_code


PENDING_GOOGLE_AUTH_SESSION_KEY = "pending_google_auth"


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         "refresh": str(refresh),
#         "access": str(refresh.access_token),
#     }


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        auth_query = parse.urlencode(
            {
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile",
            }
        )
        return redirect(f"{settings.GOOGLE_OAUTH_AUTH_URL}?{auth_query}")


@method_decorator(csrf_exempt, name="dispatch")
class CallbackView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        code = request.query_params.get("code")

        if not code:
            return self._redirect_to_frontend(
                success=False,
                detail="Google authorization code is required.",
            )

        try:
            google_user = exchange_google_authorization_code(code)
        except GoogleAuthError as exc:
            return self._redirect_to_frontend(
                success=False,
                detail=str(exc),
            )

        profile = (
            UserProfile.objects.select_related("user")
            .filter(google_sub=google_user["sub"])
            .first()
        )
        if profile:
            if not profile.user.is_active:
                return self._redirect_to_frontend(
                    success=False,
                    detail="User is inactive.",
                )

            login(request, profile.user)
            request.session.pop(PENDING_GOOGLE_AUTH_SESSION_KEY, None)
            return self._redirect_to_frontend(
                success=True, 
                hasData=True, 
            )

        request.session[PENDING_GOOGLE_AUTH_SESSION_KEY] = google_user
        return self._redirect_to_frontend(success=True, hasData=False)

    def _redirect_to_frontend(self, **query):
        callback_query = parse.urlencode(query)
        separator = "&" if "?" in settings.FRONTEND_AUTH_CALLBACK_URL else "?"
        return redirect(f"{settings.FRONTEND_AUTH_CALLBACK_URL}{separator}{callback_query}")


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    @transaction.atomic
    def post(self, request):
        pending_google_user = request.session.get(PENDING_GOOGLE_AUTH_SESSION_KEY)
        if not pending_google_user:
            return Response(
                {"success": False, "detail": "Google login is required first."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        language = request.data.get("language")
        username = request.data.get("id")
        name = request.data.get("name")

        if not username:
            return Response(
                {"success": False, "detail": "id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if language not in UserProfile.Language.values:
            return Response(
                {"success": False, "detail": "language must be 'ko', 'ja', or 'en'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return Response(
                {"success": False, "detail": "id is already taken."},
                status=status.HTTP_409_CONFLICT,
            )

        if UserProfile.objects.filter(name=name).exists():
            return Response(
                {"success": False, "detail": "name is already taken."},
                status=status.HTTP_409_CONFLICT,
            )

        if UserProfile.objects.filter(
            google_sub=pending_google_user["sub"]
        ).exists():
            return Response(
                {"success": False, "detail": "Google account is already registered."},
                status=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(
            username=username,
            email=pending_google_user.get("email", ""),
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])

        UserProfile.objects.create(
            user=user,
            google_sub=pending_google_user["sub"],
            language=language,
            name=name,
        )

        # tokens = get_tokens_for_user(user)
        login(request, user)
        request.session.pop(PENDING_GOOGLE_AUTH_SESSION_KEY, None)
        return Response({
            "success": True,
            # "token": tokens["access"],
            # "refresh": tokens["refresh"]
        })


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        logout(request)
        request.session.pop(PENDING_GOOGLE_AUTH_SESSION_KEY, None)
        return Response({"success": True})


@method_decorator(csrf_exempt, name="dispatch")
class ProfileView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        profile = getattr(request.user, "profile", None)
        return Response(
            {
                "success": True,
                "user": {
                    # "id": request.user.id,
                    "username": request.user.get_username(),
                    "email": request.user.email,
                    "name": profile.name if profile else "",
                    "language": profile.language if profile else "",
                    "googleSub": profile.google_sub if profile else "",
                },
            }
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        profile = getattr(request.user, "profile", None)
        if not profile:
            return Response(
                {"success": False, "detail": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        language = request.data.get("language")
        name = request.data.get("name")

        if language not in UserProfile.Language.values:
            return Response(
                {"success": False, "detail": "language must be 'ko', 'ja', or 'en'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not name:
            return Response(
                {"success": False, "detail": "name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile.language = language
        profile.name = name
        profile.save(update_fields=["language", "name", "updated_at"])
        return Response({"success": True})
