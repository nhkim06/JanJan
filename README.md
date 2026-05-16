# 🕊️ JanJan (잔잔 / ジャンジャン)

> An AI-powered cross-border etiquette guide  
> that helps users navigate social pressure and cultural nuances  
> in Korean and Japanese relationships, celebrations, and condolences.

---

## 🌟 Overview

JanJan is an AI assistant designed to reduce stress and information gaps caused by cultural differences between Korea and Japan in social etiquette, ceremonies, and interpersonal relationships.

By entering the country, relationship, and situation, users can receive:

- 💰 Recommended gift or condolence money amounts
- ✍️ AI-generated message templates
- 🇰🇷🇯🇵 Country-specific etiquette guides
- 📒 Reciprocity records & reminders

---

## 🚀 Core Features

### 1. Smart Etiquette Amount Calculator

- Recommends appropriate monetary amounts based on:
  - Country (KR/JP)
  - Relationship
  - Event type
- Reflects local customs such as:
  - Odd-number gifting traditions in Japan
  - Avoidance of brand-new bills
- Provides taboo and etiquette warnings for each situation

### 2. AI Message Templates

Generate messages for situations such as:

- Replying after leaving someone on read
- Politely declining invitations
- Asking for overdue payments
- Requesting vacation leave

→ Automatically generated in:
- Formal tone
- Neutral tone
- Friendly tone

### 3. Reciprocity Ledger & Reminders

- Track money and gifts given/received
- Relationship-based reminder system
- Optional Google Calendar integration

---

## 💰 Business Model

JanJan monetizes users’ “moment of truth” decisions by connecting contextual commerce services such as:

- Suit rentals
- Mobile gift vouchers
- Flower wreath delivery
- LINE Gift integrations

---

## 🛠 Tech Stack

### Frontend

- Vue 3
- Vite
- Tailwind CSS

### AI

- OpenAI API
- Claude API

### UX

- SPA / PWA architecture
- KakaoTalk-inspired chat interface

---

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/your-username/janjan.git
cd janjan
```

### Frontend (Vue 3)

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv

# Windows
cd .venv\Scripts
.\activate
# Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate

# backend.md 참고하여 .env 파일 작성 후
python manage.py runserver
```