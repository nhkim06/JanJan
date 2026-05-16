# 🥂 잔잔 (JanJan) - 스마트 경조사 에티켓 가이드

**잔잔(JanJan)**은 복잡하고 어려운 경조사 에티켓과 적정 축의금/부의금에 대한 고민을 AI를 통해 해결해주는 스마트 가이드 서비스입니다. 한국과 일본 등 문화권별 맞춤 조언을 제공하며, 나의 경조사 기록을 체계적으로 관리할 수 있습니다.

---

## ✨ 주요 기능

- **🤖 AI 에티켓 상담**: 상황별(결혼, 조의, 병문안 등) 맞춤 에티켓과 적정 금액을 Gemini AI가 분석하여 제안합니다.
- **🗺️ 다국어 및 문화권 지원**: 한국어, 영어, 일본어를 지원하며 한국/일본 문화권별 고유한 예절 가이드를 제공합니다.
- **📋 경조사 기록 관리**: AI 상담 내역뿐만 아니라 직접 주고받은 경조사 비용을 인물별로 기록하고 관리할 수 있습니다.
- **🎨 직관적인 UI**: AI 상담은 상담 카드로, 직접 기록은 파스텔톤의 연하늘/연초록 카드로 구분하여 한눈에 파악 가능합니다.
- **🔐 구글 소셜 로그인**: 구글 계정을 통해 간편하게 시작하고 나의 데이터를 안전하게 보관합니다.

---

## 🛠️ 기술 스택

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **State Management**: Pinia
- **Styling**: Tailwind CSS
- **Icons**: Font Awesome

### Backend
- **Framework**: Django REST Framework (DRF)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **AI Engine**: Google Gemini API
- **Auth**: Google OAuth 2.0 & Django Session Auth

---

## 🚀 시작하기

### 1. 레포지토리 클론
```bash
git clone https://github.com/your-username/janjan.git
cd JanJan
```

### 2. 백엔드 설정 (Django)
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# .env 파일 생성 및 API 키 설정 (backend/.env.example 참고)
# GOOGLE_API_KEY, GOOGLE_OAUTH_CLIENT_ID 등 설정

python manage.py migrate
python manage.py runserver
```

### 3. 프론트엔드 설정 (Vue 3)
```bash
cd ../frontend
npm install

# .env 파일 생성 및 API 주소 설정 (frontend/.env.example 참고)
# VITE_API_BASE_URL=http://localhost:8000

npm run dev
```

---

## 📂 프로젝트 구조

- `frontend/`: Vue 3 기반 웹 애플리케이션
  - `src/pages/`: 각 화면(홈, 채팅, 설문, 결과 등) 컴포넌트
  - `src/stores/`: 인증 및 글로벌 상태 관리
  - `src/utils/`: API 통신 모듈 (Axios)
- `backend/`: Django 기반 API 서버
  - `auth_app/`: 회원가입, 로그인 및 프로필 관리
  - `form/`: AI 설문 및 결과 데이터 관리
  - `chat/`: Gemini AI 상담 내역 관리
  - `history/`: 수동 경조사 기록 관리
  - `ai_yk/`: Gemini AI 엔진 및 프롬프트 로직

---

## 📄 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.
