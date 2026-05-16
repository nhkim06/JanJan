from __future__ import annotations

from typing import Any, Final, TypedDict

try:
    from .gemini_client import call_gemini, pretty_json
    from .language_rules import language_output_rule
    from .type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        CultureBase,
        History,
        OccasionCategory,
        is_occasion_category,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from gemini_client import call_gemini, pretty_json
    from language_rules import language_output_rule
    from type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        CultureBase,
        History,
        OccasionCategory,
        is_occasion_category,
    )


class SurveyQuestion(TypedDict):
    id: str
    text: str
    options: tuple[str, ...]
    cultures: tuple[CultureBase, ...]


QUESTION_BANK: Final[dict[OccasionCategory, tuple[SurveyQuestion, ...]]] = {
    "birth": (
        {
            "id": "Q1",
            "text": "상대와의 관계는 어느 정도인가요?",
            "options": ("가족/친척", "매우 가까운 친구", "친구/동료/선후배", "가끔 연락하는 지인"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2",
            "text": "축하하려는 시점은 언제인가요?",
            "options": ("출산 전", "출산 직후~1개월 이내", "출산 후 1개월 이후", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q3",
            "text": "어떻게 축하할 예정인가요?",
            "options": ("방문해서 전달", "비대면으로 선물/현금 전달", "단체로 모아서 전달", "메시지만 보냄"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "방문해도 되는 상황인가요?",
            "options": ("방문 허락을 받음", "아직 허락받지 않음", "산모/아기가 쉬어야 할 것 같음", "방문하지 않을 예정"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q5",
            "text": "이번 아이는 몇 번째 아이인가요?",
            "options": ("첫째", "둘째 이상", "잘 모르겠음"),
            "cultures": ("ko",),
        },
        {
            "id": "Q6",
            "text": "본인의 위치는 어디에 가까운가요?",
            "options": ("학생", "사회초년생", "일반 직장인", "선배/상사/친척 어른"),
            "cultures": ("ja",),
        },
    ),
    "wedding": (
        {
            "id": "Q1",
            "text": "초대받은 상황인가요?",
            "options": ("정식으로 초대받음", "모바일/구두로 초대받음", "소식만 들음", "초대받지 않음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2-KO",
            "text": "결혼식에 참석하나요?",
            "options": ("참석하고 식사도 함", "참석하지만 식사는 안 함", "불참함", "아직 모름"),
            "cultures": ("ko",),
        },
        {
            "id": "Q2-JA",
            "text": "결혼식 또는 피로연에 참석하나요?",
            "options": ("결혼식/피로연에 참석함", "참석하지만 피로연은 안 감", "불참함", "아직 모름"),
            "cultures": ("ja",),
        },
        {
            "id": "Q3",
            "text": "신랑/신부와의 관계는 어느 정도인가요?",
            "options": ("가족/친척", "매우 가까운 친구", "친구/동료/선후배", "상사/부하직원/거래처", "가끔 연락하는 지인"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "동행인이 있나요?",
            "options": ("혼자 감", "초대받은 동행인과 감", "동행 가능 여부를 모름", "불참 예정"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q5",
            "text": "축의금은 어떻게 전달할 예정인가요?",
            "options": ("예식장에서 직접 전달", "계좌이체로 전달", "지인을 통해 전달", "전달하지 않을 예정"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q6",
            "text": "본인의 위치는 어디에 가까운가요?",
            "options": ("학생", "사회초년생", "일반 직장인", "선배/상사/친척 어른"),
            "cultures": ("ja",),
        },
        {
            "id": "Q7",
            "text": "초대장 회신은 했나요?",
            "options": ("참석으로 회신함", "불참으로 회신함", "아직 회신하지 않음", "초대장을 받지 않음"),
            "cultures": ("ja",),
        },
    ),
    "employment": (
        {
            "id": "Q1",
            "text": "축하 대상은 어떤 상황인가요?",
            "options": ("첫 취업/합격", "이직", "인턴/계약직 시작", "승진에 가까운 변화"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2",
            "text": "상대와의 관계는 어느 정도인가요?",
            "options": ("가족/친척", "매우 가까운 친구", "친구/동료/선후배", "가끔 연락하는 지인"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q3",
            "text": "어떻게 축하할 예정인가요?",
            "options": ("식사 대접", "선물/상품권", "현금/축하금", "단체 선물", "메시지만 보냄"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "단체로 챙기는 분위기가 있나요?",
            "options": ("이미 단체로 준비 중", "단체 축하는 없음", "개인적으로 따로 챙기고 싶음", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q5",
            "text": "나이 차이나 선후배 관계는 어떤가요?",
            "options": ("내가 손윗사람/선배임", "상대가 손윗사람/선배임", "비슷한 위치임", "상대가 후배/동생임"),
            "cultures": ("ko",),
        },
        {
            "id": "Q6",
            "text": "일본 기준이라면, 현금을 줘도 자연스러운 관계인가요?",
            "options": ("가족/친척이라 가능함", "아주 가까운 사이라 가능할 것 같음", "친구/동료라 부담스러울 수 있음", "직장 관계라 피하는 게 좋을 것 같음"),
            "cultures": ("ja",),
        },
    ),
    "school_admission": (
        {
            "id": "Q1",
            "text": "입학하는 학교 단계는 어디인가요?",
            "options": ("어린이집/유치원", "초등학교", "중·고등학교", "대학교 이상"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2",
            "text": "입학하는 사람과의 관계는 어느 정도인가요?",
            "options": ("자녀/형제자매", "조카/친척 아이", "가까운 친구의 자녀", "동료/지인의 자녀", "본인 친구/동료"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q3",
            "text": "누구에게 전달할 예정인가요?",
            "options": ("입학하는 사람에게 직접", "부모를 통해 전달", "부모와 함께 있을 때 전달", "메시지만 보냄"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "어떻게 축하할 예정인가요?",
            "options": ("현금/축하금", "선물/상품권", "식사 대접", "메시지만 보냄"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q5",
            "text": "단체로 챙기는 분위기가 있나요?",
            "options": ("가족/친척끼리 함께 준비 중", "회사/모임에서 함께 준비 중", "단체 축하는 없음", "잘 모르겠음"),
            "cultures": ("ko",),
        },
        {
            "id": "Q6",
            "text": "초등학교 입학이고 고가 선물을 고려 중이라면, 이미 준비된 물건이 있나요?",
            "options": ("란도셀 등 주요 물건이 이미 준비됨", "아직 준비 안 됨", "누가 사줄지 정해짐", "잘 모르겠음", "해당 없음"),
            "cultures": ("ja",),
        },
    ),
    "business_opening": (
        {
            "id": "Q1",
            "text": "상대와의 관계는 어느 정도인가요?",
            "options": ("가족/친척", "매우 가까운 친구", "친구/동료", "상사/선배/거래처", "가끔 연락하는 지인"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2",
            "text": "개업 소식을 어떻게 알게 되었나요?",
            "options": ("직접 초대받음", "개인적으로 연락받음", "단체 공지로 알게 됨", "SNS/지인을 통해 알게 됨"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q3",
            "text": "방문하거나 참석할 예정인가요?",
            "options": ("방문/참석 예정", "못 감", "아직 고민 중", "상대가 원할지 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "개업 형태는 무엇인가요?",
            "options": ("실제 매장/공간이 있는 개업", "사무실/병원/학원 등 공간 기반 개업", "온라인 서비스/앱/쇼핑몰", "법인/스타트업 창업", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q5",
            "text": "지금 개업 시점은 언제인가요?",
            "options": ("개업 전", "개업 당일/첫 주", "개업 후 몇 주 지남", "개업 후 몇 달 이상 지남"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q6",
            "text": "공개적으로 축하해도 되는 분위기인가요?",
            "options": ("공개 축하해도 괜찮을 것 같음", "조용히 축하하는 게 나을 것 같음", "SNS 홍보를 좋아할 것 같음", "공개 축하는 부담스러워할 것 같음", "잘 모르겠음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q7",
            "text": "방문하면 상대에게 부담이 될 수 있나요?",
            "options": ("부담 없을 것 같음", "바쁜 시간이라 부담될 수 있음", "응대 부담이 클 것 같음", "방문하지 않는 게 나을 것 같음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q8",
            "text": "단체로 축하하는 분위기가 있나요?",
            "options": ("이미 단체로 돈/선물을 모으고 있음", "단체 축하 예정은 없음", "개인적으로 따로 챙기고 싶음", "잘 모르겠음"),
            "cultures": ("ja",),
        },
    ),
    "first_birthday": (
        {
            "id": "Q1",
            "text": "부모와의 관계는 어느 정도인가요?",
            "options": ("가족/친척", "매우 가까운 친구", "친구/동료", "가끔 연락하는 지인"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2",
            "text": "돌잔치에 초대받았나요?",
            "options": ("개인적으로 초대받음", "단체로 초대받음", "소식만 들음", "초대받지 않음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q3",
            "text": "참석할 예정인가요?",
            "options": ("참석함", "불참함", "아직 모름"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "식사나 행사가 있는 자리인가요?",
            "options": ("식사 있는 돌잔치", "가족 중심 작은 모임", "돌상/사진만 진행", "잘 모르겠음"),
            "cultures": ("ko",),
        },
        {
            "id": "Q5",
            "text": "어떤 선물이 자연스러운 분위기인가요?",
            "options": ("금/현금 선물이 자연스러움", "실용 선물이 자연스러움", "메시지만으로 충분할 것 같음", "잘 모르겠음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q6",
            "text": "동반 참석이 포함되어 있나요?",
            "options": ("나만 초대받음", "동반자도 초대받음", "가족 단위 초대임", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q7",
            "text": "아기 사진이나 행사 내용을 공개해도 되나요?",
            "options": ("허락받음", "허락받지 않음", "공개하지 않을 예정", "잘 모르겠음"),
            "cultures": ("ja",),
        },
    ),
    "funeral": (
        {
            "id": "Q1",
            "text": "누구와 가까운 관계인가요?",
            "options": ("고인과 가까움", "유족/상주와 가까움", "둘 다 가까움", "업무/조직 관계임", "둘 다 잘 모름"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2",
            "text": "부고를 어떻게 알게 되었나요?",
            "options": ("직접 연락받음", "회사/학교/단체 공지로 받음", "지인을 통해 들음", "SNS/우연히 알게 됨"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q3",
            "text": "공개 조문을 받는 장례인가요?",
            "options": ("빈소/장례식장 안내가 있음", "가족장이라고 들음", "조문 사양이라고 들음", "부의금/향전 사양이라고 들음", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "직접 조문할 수 있나요?",
            "options": ("조문 예정", "못 감", "아직 고민 중", "조문해도 되는지 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q5-KO",
            "text": "지금 어느 시점인가요?",
            "options": ("빈소 조문 가능 기간", "발인 전", "발인 후", "장례가 끝난 뒤", "추모/기일/법요 시기"),
            "cultures": ("ko",),
        },
        {
            "id": "Q5-JA",
            "text": "지금 어느 시점인가요?",
            "options": ("通夜 전/당일", "葬儀・告別式 전/당일", "장례가 끝난 뒤", "法要/추모 시기", "잘 모르겠음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q6",
            "text": "부의금/향전을 해야 할 관계인가요?",
            "options": ("해야 할 것 같음", "단체 부의금에 참여하면 될 것 같음", "하지 않아도 될 것 같음", "상대가 사양함", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q7",
            "text": "단체로 조문하거나 부의금을 모으고 있나요?",
            "options": ("이미 모으고 있음", "단체 조문 예정임", "없음", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q8",
            "text": "종교나 장례 방식이 안내되었나요?",
            "options": ("불교식", "기독교/천주교식", "무종교/일반식", "일본식 장례", "잘 모르겠음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q9",
            "text": "복장은 준비되었나요?",
            "options": ("검정 정장 가능", "어두운 단정한 옷 가능", "준비가 부족함", "직접 방문하지 않을 예정"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q10",
            "text": "장례 관련 정보를 공개해도 된다고 들었나요?",
            "options": ("허락받음", "허락받지 않음", "공개하지 않을 예정", "잘 모르겠음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q11",
            "text": "장례 이후 추모 행사까지 챙겨야 할 관계인가요?",
            "options": ("가족/친척이라 챙겨야 함", "아주 가까운 관계라 챙길 수 있음", "일반 지인이라 장례까지만 챙기면 될 것 같음", "초대받은 경우에만 갈 예정", "잘 모르겠음"),
            "cultures": ("ja",),
        },
    ),
    "hospital_visit": (
        {
            "id": "Q1",
            "text": "환자와의 관계는 어느 정도인가요?",
            "options": ("가족/친척", "매우 가까운 친구", "친구/동료", "가끔 연락하는 지인"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q2",
            "text": "입원/치료 소식을 어떻게 알게 되었나요?",
            "options": ("환자에게 직접 들음", "보호자에게 들음", "단체 공지로 알게 됨", "다른 사람/SNS를 통해 알게 됨"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q3",
            "text": "직접 병문안을 가도 되는 상황인가요?",
            "options": ("환자나 보호자가 허락함", "아직 묻지 않음", "방문을 원하지 않는다고 들음", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q4",
            "text": "환자가 면회를 받을 수 있는 상태인가요?",
            "options": ("받을 수 있음", "쉬어야 하는 상태임", "수술/검사 직후라 어려움", "감염 위험이 있음", "잘 모르겠음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q5",
            "text": "병원 면회 규칙을 확인했나요?",
            "options": ("확인했고 방문 가능함", "면회 시간이 제한됨", "보호자만 가능함", "예약/출입증이 필요함", "아직 확인하지 않음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q6",
            "text": "내가 감염 위험이 있나요?",
            "options": ("없음", "감기/기침/발열이 있음", "최근 감염병 접촉 가능성이 있음", "컨디션이 좋지 않음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q7",
            "text": "선물이나 음식을 가져가도 되나요?",
            "options": ("가능하다고 들음", "음식은 제한됨", "꽃/화분은 제한됨", "아무것도 가져가지 않을 예정", "아직 확인하지 않음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q8",
            "text": "현금이나 위로금을 줄 관계인가요?",
            "options": ("가족/아주 가까운 사이라 줄 수 있음", "간단한 선물이 적절함", "메시지만으로 충분함", "상대가 부담스러워할 것 같음", "잘 모르겠음"),
            "cultures": ("ko", "ja"),
        },
        {
            "id": "Q9",
            "text": "병명이나 상태를 자세히 물어봐도 되는 관계인가요?",
            "options": ("물어봐도 될 만큼 가까움", "먼저 말해주면 듣는 정도가 좋음", "묻지 않는 게 좋음", "민감한 병일 수 있음", "잘 모르겠음"),
            "cultures": ("ja",),
        },
        {
            "id": "Q10",
            "text": "병실 사진이나 입원 사실을 공개해도 되나요?",
            "options": ("허락받음", "허락받지 않음", "공개하지 않을 예정", "잘 모르겠음"),
            "cultures": ("ja",),
        },
    ),
}

CATEGORY_ALIASES: Final[dict[str, OccasionCategory]] = {
    "childbirth": "birth",
    "출산": "birth",
    "birth": "birth",
    "결혼": "wedding",
    "wedding": "wedding",
    "career": "employment",
    "취업": "employment",
    "이직": "employment",
    "employment": "employment",
    "admission": "school_admission",
    "입학": "school_admission",
    "school_admission": "school_admission",
    "business": "business_opening",
    "개업": "business_opening",
    "창업": "business_opening",
    "business_opening": "business_opening",
    "돌잔치": "first_birthday",
    "첫돌": "first_birthday",
    "first_birthday": "first_birthday",
    "부고": "funeral",
    "장례": "funeral",
    "조문": "funeral",
    "funeral": "funeral",
    "병문안": "hospital_visit",
    "hospital_visit": "hospital_visit",
}

CULTURE_ALIASES: Final[dict[str, CultureBase]] = {
    "ko": "ko",
    "kr": "ko",
    "korea": "ko",
    "korean": "ko",
    "한국": "ko",
    "일본": "ja",
    "ja": "ja",
    "jp": "ja",
    "japan": "ja",
    "japanese": "ja",
    "both": "both",
    "둘 다": "both",
    "한국/일본": "both",
    "unknown": "unknown",
    "잘 모르겠음": "unknown",
    "아직 모르겠음": "unknown",
}

PLACEHOLDER_TARGET_NAMES: Final[set[str]] = {
    "?",
    "??",
    "???",
    "??님",
    "???님",
    "unknown",
    "(unknown)",
    "(not provided)",
    "not provided",
    "none",
    "null",
    "상대방",
}

SYSTEM_INSTRUCTION = """
You are JanJan, a practical etiquette and cost advisor for Korean and Japanese
congratulation and condolence situations.

Interpretation rules:
- Treat the selected category and pre-survey answers as the user's current situation.
- Treat the histories as past congratulation/condolence records between the user and the
  current target person. They are reciprocity context, not a rigid debt ledger.
- Treat conversation memory as the prior turns in the same chat. Use it to resolve
  follow-up references, keep continuity, and avoid asking again for details already
  provided.
- If a history appears unrelated to the current target, category, culture, or timing, mention
  uncertainty briefly and do not force it into the recommendation.
- Do not invent facts that are not present in the pre-survey, history, memory, or user question.
- If memory conflicts with the latest user question or current pre-survey/history, prefer the
  latest explicit user question and current structured context.
- When information is missing, give the safest conservative recommendation and name the
  missing factor only if it changes the action.

Answering rules:
- Answer only in the requested output language. Interpret common language codes as
  ko=Korean, ja=Japanese, and en=English.
- Do not let currency, culture marker, question text, survey text, history, or memory choose
  the output language.
- Return plain text only.
- Answer only the user's latest free-form question. Use the current pre-survey context and
  target-specific history only as evidence for that answer.
- Write 150 to 300 characters total, including spaces and punctuation.
- Give the direct answer first, then provide enough context-based reasoning for why that
  answer fits. Do not use headings or bullet lists unless the user explicitly asks for them.
- Do not proactively add neighboring advice about money, visits, gifts, attire, photos,
  public posting, or message wording unless the user explicitly asks about it.
- If the user asks about money, answer the amount and only the minimal reason or caution.
  If the user asks about wording, answer with wording and only the minimal tone note.
  If the user asks about an action, answer that action and only the minimal etiquette caveat.
- Add an unasked caution only when omitting it would create a clear etiquette, privacy, or
  safety risk.
- Prefer choices that reduce burden, protect privacy, and respect refusals such as no visits,
  no money, no photos, no public posting, or no reply pressure.
- For medical or funeral contexts, be especially conservative about visits, privacy, photos,
  asking intrusive details, public sharing, and wording.
""".strip()


def question(
    language: str,
    histories: list[History] | list[dict[str, Any]],
    question: str,
    memory: str = "",
    *,
    category: str | None = None,
    target_name: str | None = None,
    culture_base: str | None = None,
    presurvey: Any | None = None,
    survey_answers: Any | None = None,
) -> AIResponse:
    """Answer a follow-up etiquette question using pre-survey context and history."""

    invalid_reason = _validate_histories(histories)
    if invalid_reason:
        return {"success": False, "answer": invalid_reason}

    resolved_target_name = _resolve_target_name(target_name, histories)
    histories_for_prompt = _histories_for_prompt(histories, resolved_target_name)
    normalized_category = _normalize_category(category)
    normalized_culture = _normalize_culture_base(culture_base)
    survey_data = survey_answers if survey_answers is not None else presurvey

    conversation_memory = memory.strip()
    prompt = _build_prompt(
        language=language,
        histories=histories_for_prompt,
        user_question=question,
        memory=conversation_memory,
        category=normalized_category,
        raw_category=category,
        target_name=resolved_target_name,
        culture_base=normalized_culture,
        raw_culture_base=culture_base,
        survey_answers=survey_data,
    )
    result = call_gemini(
        prompt,
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.3,
        max_output_tokens=2400,
    )
    return {
        "success": bool(result.get("success")),
        "answer": str(result.get("answer", "")),
    }


def _resolve_target_name(target_name: Any, histories: list[dict[str, Any]]) -> str | None:
    direct_name = _clean_target_name(target_name)
    if direct_name:
        return direct_name

    for history in reversed(histories):
        history_name = _target_name_from_history(history)
        if history_name:
            return history_name
    return None


def _histories_for_prompt(
    histories: list[dict[str, Any]],
    resolved_target_name: str | None,
) -> list[dict[str, Any]]:
    prompt_histories: list[dict[str, Any]] = []
    for history in histories:
        prompt_history = dict(history)
        history_name = _target_name_from_history(prompt_history)

        if history_name:
            prompt_history["targetName"] = history_name
        elif resolved_target_name:
            prompt_history["targetName"] = resolved_target_name
        elif "targetName" in prompt_history:
            prompt_history["targetName"] = "unknown"

        prompt_histories.append(prompt_history)
    return prompt_histories


def _target_name_from_history(history: dict[str, Any]) -> str | None:
    for key in ("targetName", "target_name", "name"):
        name = _clean_target_name(history.get(key))
        if name:
            return name
    return None


def _clean_target_name(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    name = value.strip()
    if not name:
        return None

    lower_name = name.lower()
    if lower_name in PLACEHOLDER_TARGET_NAMES:
        return None

    name_without_honorific = name[:-1].strip() if name.endswith("님") else name
    meaningful = name_without_honorific.replace("?", "").replace("�", "").strip()
    if not meaningful:
        return None

    return name


def _build_prompt(
    *,
    language: str,
    histories: list[History] | list[dict[str, Any]],
    user_question: str,
    memory: str,
    category: OccasionCategory | None,
    raw_category: str | None,
    target_name: str | None,
    culture_base: CultureBase,
    raw_culture_base: str | None,
    survey_answers: Any,
) -> str:
    category_label = CATEGORY_LABELS.get(category, category) if category else "(unknown)"
    category_key = category or "(unknown)"
    output_language_rule = language_output_rule(language)
    return f"""
Task:
Answer the user's latest free-form question about what to do, how much to spend, what
to avoid, or how to write a message in this exact congratulation/condolence situation.

Output language:
{output_language_rule}

Output rules:
- Return plain text only.
- Length must be 150 to 300 characters total, including spaces and punctuation.
- Structure the answer as one concise paragraph: direct answer first, then enough evidence
  from the pre-survey/history/culture context to justify it.
- Before returning, verify internally that the final answer is within 150 to 300 characters.
- First infer the user's requested intent from the latest question: amount, action, wording,
  timing, caution, comparison, or clarification.
- Answer only that requested intent. Do not include fixed sections or a general guide unless
  the user explicitly asks for a full guide.
- Do not add message examples, gift ideas, visit advice, money advice, or behavior checklists
  unless that is what the user asked for.
- If a narrow answer needs a critical etiquette, privacy, or safety caveat, add one short
  caution after the direct answer.
- Do not answer as a generic category guide. Use the pre-survey answers as the current
  context and the history as target-specific reciprocity context.
- Do not mention unrelated context just because it appears in the pre-survey, history, or
  memory.
- Continue from the conversation memory when the latest question depends on earlier turns.
  Do not repeat already-settled context unless it is needed to answer accurately.
- If the latest question updates or corrects earlier memory, follow the latest question.
- Make clear when the safest answer is to not visit, not give money, not post publicly,
  or confirm permission first.

Current target:
- target_name: {target_name or "(not provided)"}

Target name handling:
- If target_name is provided, refer to that person using the exact provided name.
- If target_name is omitted but target-specific history contains targetName, treat that
  targetName as the current person.
- Never write placeholder names such as "??", "???", "unknown", or "(not provided)" in the
  final answer. If no real name is available, use a neutral phrase in the requested language.

Current event category:
- key: {category_key}
- label: {category_label}
- raw_input: {raw_category or "(not provided)"}

Culture/currency context:
- normalized: {culture_base}
- raw_input: {raw_culture_base or "(not provided)"}

Prepared question bank for this category/culture:
{_format_question_bank(category, culture_base)}

Pre-survey answers for the current situation:
{_format_survey_answers(category, culture_base, survey_answers)}

Target-specific past history:
{pretty_json(histories)}

History schema note:
- targetName: the other person involved in the past event.
- received: true means the user received money/gift/help from that person; false means the
  user gave it to that person.
- value: amount or approximate value.
- currency: ko, ja, both, unknown, or project-specific text if older data exists.
- category/date: what the past event was and when it happened.

Conversation memory from previous turns:
{memory or "(none)"}

User's latest question:
{user_question.strip()}
""".strip()


def _normalize_category(category: str | None) -> OccasionCategory | None:
    if not category:
        return None

    normalized = category.strip()
    alias = CATEGORY_ALIASES.get(normalized)
    if alias:
        return alias
    if is_occasion_category(normalized):
        return normalized
    return None


def _normalize_culture_base(culture_base: str | None) -> CultureBase:
    if not culture_base:
        return "unknown"
    return CULTURE_ALIASES.get(culture_base.strip().lower(), CULTURE_ALIASES.get(culture_base.strip(), "unknown"))


def _questions_for_culture(
    category: OccasionCategory,
    culture_base: CultureBase,
) -> tuple[SurveyQuestion, ...]:
    questions = QUESTION_BANK[category]
    if culture_base in ("ko", "ja"):
        return tuple(
            item for item in questions if culture_base in item["cultures"] or item["cultures"] == ("ko", "ja")
        )
    return questions


def _format_question_bank(
    category: OccasionCategory | None,
    culture_base: CultureBase,
) -> str:
    if category is None:
        allowed = ", ".join(OCCASION_CATEGORIES)
        return f"(unknown category; allowed: {allowed})"

    lines: list[str] = []
    for item in _questions_for_culture(category, culture_base):
        cultures = "/".join(item["cultures"])
        options = " | ".join(item["options"])
        lines.append(f"- {item['id']} [{cultures}] {item['text']} options: {options}")
    return "\n".join(lines)


def _format_survey_answers(
    category: OccasionCategory | None,
    culture_base: CultureBase,
    survey_answers: Any,
) -> str:
    if survey_answers is None or survey_answers == "":
        return "(none provided)"

    if isinstance(survey_answers, dict):
        answers = survey_answers.get("answers")
        if answers is not None:
            return _format_survey_answers(category, culture_base, answers)
        return pretty_json(survey_answers)

    if isinstance(survey_answers, list):
        normalized = _normalize_survey_answer_list(category, culture_base, survey_answers)
        return pretty_json(normalized)

    return str(survey_answers).strip() or "(none provided)"


def _normalize_survey_answer_list(
    category: OccasionCategory | None,
    culture_base: CultureBase,
    survey_answers: list[Any],
) -> list[dict[str, Any]]:
    if _looks_like_question_answer_list(survey_answers):
        return [_normalize_question_answer_item(item) for item in survey_answers]

    questions = _questions_for_culture(category, culture_base) if category else ()
    normalized: list[dict[str, Any]] = []
    for index, answer in enumerate(survey_answers):
        question_item = questions[index] if index < len(questions) else None
        normalized.append(
            {
                "id": question_item["id"] if question_item else f"Q{index + 1}",
                "question": question_item["text"] if question_item else "(unknown question)",
                "answer": "잘 모르겠음" if answer is None else answer,
            }
        )
    return normalized


def _looks_like_question_answer_list(value: list[Any]) -> bool:
    if not value:
        return True
    return all(isinstance(item, dict) for item in value)


def _normalize_question_answer_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"question": "(invalid item)", "answer": item}

    question_text = item.get("question") or item.get("text") or item.get("label") or "(unknown question)"
    answer = item.get("answer")
    if answer is None:
        answer = item.get("value")

    normalized = {
        "question": question_text,
        "answer": "잘 모르겠음" if answer is None else answer,
    }
    if item.get("id"):
        normalized["id"] = item["id"]
    return normalized


def _validate_histories(histories: Any) -> str | None:
    if not isinstance(histories, list):
        return "histories must be a list."

    for index, history in enumerate(histories):
        if not isinstance(history, dict):
            return f"histories[{index}] must be an object."
    return None
