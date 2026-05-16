from django.conf import settings
import json
from urllib import error, parse, request


class GoogleAuthError(ValueError):
    pass


def exchange_google_authorization_code(code, redirect_uri=None):
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        raise GoogleAuthError("GOOGLE_OAUTH_CLIENT_ID is not configured.")

    if not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise GoogleAuthError("GOOGLE_OAUTH_CLIENT_SECRET is not configured.")

    resolved_redirect_uri = redirect_uri or settings.GOOGLE_OAUTH_REDIRECT_URI
    if not resolved_redirect_uri:
        raise GoogleAuthError("GOOGLE_OAUTH_REDIRECT_URI is not configured.")

    payload = parse.urlencode(
        {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": resolved_redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode()

    token_request = request.Request(
        settings.GOOGLE_OAUTH_TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with request.urlopen(token_request, timeout=10) as response:
            token_response = json.loads(response.read().decode())
    except error.HTTPError as exc:
        detail = exc.read().decode()
        raise GoogleAuthError(f"Google token exchange failed: {detail}") from exc
    except (error.URLError, TimeoutError) as exc:
        raise GoogleAuthError("Google token exchange request failed.") from exc

    access_token = token_response.get("access_token")
    if not access_token:
        raise GoogleAuthError("Google token response is missing access_token.")

    return fetch_google_userinfo(access_token)


def fetch_google_userinfo(access_token):
    userinfo_request = request.Request(
        settings.GOOGLE_OAUTH_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )

    try:
        with request.urlopen(userinfo_request, timeout=10) as response:
            userinfo = json.loads(response.read().decode())
    except error.HTTPError as exc:
        detail = exc.read().decode()
        raise GoogleAuthError(f"Google userinfo request failed: {detail}") from exc
    except (error.URLError, TimeoutError) as exc:
        raise GoogleAuthError("Google userinfo request failed.") from exc

    if not userinfo.get("sub"):
        raise GoogleAuthError("Google userinfo response is missing subject.")

    if userinfo.get("email_verified") is False:
        raise GoogleAuthError("Google email is not verified.")

    return {
        "sub": userinfo["sub"],
        "email": userinfo.get("email", ""),
        "name": userinfo.get("name", ""),
        "picture": userinfo.get("picture", ""),
    }
