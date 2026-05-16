## JanJan Backend

Django REST Framework 기반 백엔드입니다.

### 로컬 실행

```powershell
cd backend
python -m venv .venv

# 일반 Windows Python이면:
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# 이 환경처럼 .venv/bin 구조로 만들어졌다면:
.\.venv\bin\python -m pip install -r requirements.txt
.\.venv\bin\python manage.py migrate
.\.venv\bin\python manage.py runserver
```

### 기본 API

- `GET /api/health/`: 백엔드 상태 확인

### 앱 구조

- `api`: 공통 API, 헬스체크
- `auth_app`: Google 로그인, 회원가입, 로그아웃

### 환경 변수

필요하면 `.env.example`을 참고해서 `backend/.env` 파일을 만듭니다.

```powershell
Copy-Item .env.example .env
```

Google 로그인 검증을 위해 OAuth Client ID를 설정합니다.

```env
GOOGLE_OAUTH_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/callback
FRONTEND_AUTH_CALLBACK_URL=http://localhost:5173/auth/callback
```

Supabase를 쓰려면 아래 값들을 설정합니다.

```env
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres.[Supabase프로젝트ID]
SUPABASE_DB_PASSWORD=[Supabase비밀번호]
SUPABASE_DB_HOST=aws-0-[지역].pooler.supabase.com
SUPABASE_DB_PORT=6543
```

Supabase 환경 변수가 없으면 로컬 개발 편의를 위해 SQLite를 사용합니다.

### 인증 API

- `GET /auth/login`

Google 로그인 링크로 redirect 시킵니다.

로그인이 완료되고 나면 `미리정해진프론트링크?success=True&hasData=True`로 리다이렉트됩니다. 이때 기존 회원이면 `hasData=True`, 신규 회원이면 `hasData=False`입니다.

- `POST /auth/register`
- 
```jsonb
{
  "language": "ko",  # "ko" 또는 "ja"
  "id": "janjan1234",  # 아이디
  "name": "홍길동"  # 이름
}
```

```jsonb
{
  "success": true
}
```

- `POST /auth/logout`

```jsonb
{
  "success": true
}
```

- `GET /auth/profile`

현재 로그인된 계정 정보를 반환합니다.

```jsonb
{
  "success": true,
  "user": {
    "id": 1,
    "username": "janjan1234",
    "email": "user@example.com",
    "name": "홍길동",
    "language": "ko",
    "googleSub": "google-user-sub"
  }
}
```

프론트는 Google 로그인 시작 시 redirect URI를 백엔드 콜백 주소로 지정합니다.
