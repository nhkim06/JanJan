## JanJan Backend

Django REST Framework 기반 백엔드입니다.

### 백엔드 서버는 https://janjan-backend.vercel.app/ 에 있습니다!


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
- `chat`: 챗봇 대화 저장 API
- `form`: 폼 생성 API
- `history`: 기록 CRUD API

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

Vercel 배포에서는 `.env` 파일이 아니라 Project Settings의 Environment Variables에 같은 키들을 등록합니다.
`DJANGO_ALLOWED_HOSTS`는 배포 도메인을 포함해야 합니다.

```env
DJANGO_ALLOWED_HOSTS=.vercel.app
```

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

- `POST /auth/profile`

현재 로그인된 계정의 언어와 이름을 수정합니다.

```jsonb
{
  "language": "en",
  "name": "전우치"
}
```

```jsonb
{
  "success": true
}
```

프론트는 Google 로그인 시작 시 redirect URI를 백엔드 콜백 주소로 지정합니다.

### Form API

- `POST /form/new`

현재 로그인된 계정으로 form을 저장합니다.

```jsonb
{
  "answers": [
    {
      "question": "좋아하는 음식은?",
      "answer": "김치찌개"
    }
  ],
  "targetName": "홍길동",
  "cultureBase": "ko"
}
```

```jsonb
{
  "success": true,
  "formId": 1
}
```

- `GET /form/list`

현재 로그인된 계정의 form 목록을 반환합니다.

```jsonb
{
  "success": true,
  "forms": [
    {
      "formId": 1,
      "answers": [
        {
          "question": "좋아하는 음식은?",
          "answer": "김치찌개"
        }
      ],
      "targetName": "홍길동",
      "cultureBase": "ko",
      "createdAt": "2026-05-16T22:30:00+09:00",
      "updatedAt": "2026-05-16T22:30:00+09:00"
    }
  ]
}
```

- `GET /form/{id}`

현재 로그인된 계정의 특정 form 데이터를 반환합니다.

```jsonb
{
  "success": true,
  "form": {
    "formId": 1,
    "answers": [
      {
        "question": "좋아하는 음식은?",
        "answer": "김치찌개"
      }
    ],
    "targetName": "홍길동",
    "cultureBase": "ko",
    "createdAt": "2026-05-16T22:30:00+09:00",
    "updatedAt": "2026-05-16T22:30:00+09:00"
  }
}
```

### Chat API

- `POST /chat/new`

현재 로그인된 계정의 form에 챗봇 대화를 저장합니다. 지금은 실제 Gemini API 대신 테스트 응답을 저장합니다.

```jsonb
{
  "formId": 1,
  "question": "다음에는 어떤 말을 하면 좋을까?"
}
```

### History API

- `POST /history/new`

현재 로그인된 계정으로 history를 저장합니다.

```jsonb
{
  "targetName": "홍길동",
  "received": true,
  "value": 50000,
  "cultureBase": "ko",
  "category": "결혼",
  "date": "2026-05-16"
}
```

```jsonb
{
  "success": true,
  "historyId": 1
}
```

- `GET /history/list?targetName=홍길동`

현재 로그인된 계정의 history 목록을 반환합니다. `targetName`은 선택입니다.

```jsonb
{
  "success": true,
  "histories": [
    {
      "historyId": 1,
      "targetName": "홍길동",
      "received": true,
      "value": 50000,
      "cultureBase": "ko",
      "category": "결혼",
      "date": "2026-05-16",
      "createdAt": "2026-05-17T00:40:00+09:00",
      "updatedAt": "2026-05-17T00:40:00+09:00"
    }
  ]
}
```

- `GET /history/{id}`

```jsonb
{
  "success": true,
  "history": {
    "historyId": 1,
    "targetName": "홍길동",
    "received": true,
    "value": 50000,
    "cultureBase": "ko",
    "category": "결혼",
    "date": "2026-05-16",
    "createdAt": "2026-05-17T00:40:00+09:00",
    "updatedAt": "2026-05-17T00:40:00+09:00"
  }
}
```

- `POST /history/{id}`

해당 history를 수정합니다.

```jsonb
{
  "targetName": "홍길동",
  "received": false,
  "value": 70000,
  "cultureBase": "ko",
  "category": "축의금",
  "date": "2026-05-17"
}
```

```jsonb
{
  "success": true,
  "history": {
    "historyId": 1,
    "targetName": "홍길동",
    "received": false,
    "value": 70000,
    "cultureBase": "ko",
    "category": "축의금",
    "date": "2026-05-17",
    "createdAt": "2026-05-17T00:40:00+09:00",
    "updatedAt": "2026-05-17T00:45:00+09:00"
  }
}
```

- `DELETE /history/{id}`

```jsonb
{
  "success": true
}
```

```jsonb
{
  "success": true,
  "chatItemId": 1,
  "status": "success",
  "answer": "그만 말해도 괜찮을 것 같아!"
}
```

- `GET /chat/list?formId=1`

현재 로그인된 계정의 특정 form에 연결된 챗봇 대화 목록을 반환합니다.

```jsonb
{
  "success": true,
  "chatItems": [
    {
      "chatItemId": 1,
      "formId": 1,
      "question": "다음에는 어떤 말을 하면 좋을까?",
      "answer": "Test Success! This is gemini answer",
      "status": "success",
      "createdAt": "2026-05-16T22:30:00+09:00",
      "updatedAt": "2026-05-16T22:30:00+09:00"
    }
  ]
}
```
