from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict


DEFAULT_MODEL = "gemini-2.5-flash"
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

LANGUAGE_LABELS = {
    "ko": "Korean",
    "ja": "Japanese",
    "en": "English",
}

CATEGORY_LABELS = {
    "birth": "출산",
    "wedding": "결혼",
    "employment": "취업 / 이직",
    "school_admission": "입학",
    "business_opening": "개업 / 창업",
    "first_birthday": "돌잔치 / 첫돌",
    "funeral": "장례 / 부고 / 조문",
    "hospital_visit": "병문안",
}

CATEGORY_ALIASES = {
    "childbirth": "birth",
    "career": "employment",
    "admission": "school_admission",
    "business": "business_opening",
}

CULTURE_ALIASES = {
    "한국": "ko",
    "일본": "ja",
    "둘 다": "both",
    "둘다": "both",
    "아직 모르겠음": "unknown",
    "잘 모르겠음": "unknown",
    "ko": "ko",
    "kr": "ko",
    "korea": "ko",
    "ja": "ja",
    "jp": "ja",
    "japan": "ja",
    "both": "both",
    "unknown": "unknown",
}

_DOTENV_LOADED = False


class GeminiResult(TypedDict):
    success: bool
    answer: str


@dataclass(frozen=True)
class QuestionSpec:
    question: str
    prompt: str = ""


CATEGORY_RESPONSE_QUESTIONS: dict[str, tuple[QuestionSpec, ...]] = {
    "birth": (
        QuestionSpec("출산 축하금은 얼마가 적당한가요?"),
        QuestionSpec("출산 선물은 현금이 좋나요, 물건이 좋나요?"),
        QuestionSpec("직장 동료 출산은 개인적으로 챙겨야 하나요, 단체로 챙겨야 하나요?"),
        QuestionSpec("친하지 않은 지인의 출산도 챙겨야 하나요?"),
        QuestionSpec("출산 전에 선물을 줘도 되나요?", "일본 문화권이면 출산 전 선물은 조심스럽게 판단하고, 산모와 아기의 안전이 확인된 뒤 出産祝い를 전하는 쪽을 우선한다."),
        QuestionSpec("출산 직후 병원이나 산후조리원에 방문해도 되나요?"),
        QuestionSpec("산모에게 어떤 말을 하면 실례가 되지 않나요?"),
        QuestionSpec("아기 사진을 찍거나 SNS에 올려도 되나요?"),
        QuestionSpec("첫째와 둘째 이상일 때 축하금이 달라지나요?", "한국 문화권이면 첫째와 둘째 이상에서 축하 규모가 달라질 수 있음을 반영한다."),
        QuestionSpec("일본에서는 出産祝い를 언제 주는 게 적절한가요?", "일본 문화권의 出産祝い 전달 시기를 반영한다."),
        QuestionSpec("일본에서는 출산 축하로 현금을 줘도 되나요?", "일본 문화권에서 현금이 가능한 관계와 피하는 편이 나은 관계를 구분한다."),
        QuestionSpec("출산 축하 메시지는 어떻게 보내면 좋나요?"),
        QuestionSpec("출산 축하 선물은 얼마 정도가 적당한가요?"),
        QuestionSpec("산모에게 실례 될 만한 행동은 무엇이 있나요?"),
    ),
    "wedding": (
        QuestionSpec("결혼식 축의금은 얼마가 적당한가요?"),
        QuestionSpec("결혼식에 참석하지 못하면 축의금을 보내야 하나요?"),
        QuestionSpec("식사를 안 하면 축의금을 줄여도 되나요?"),
        QuestionSpec("친구, 동료, 친척, 거래처별 축의금은 어떻게 다른가요?"),
        QuestionSpec("초대받지 않은 동행인을 데려가도 되나요?"),
        QuestionSpec("모바일 청첩장만 받았는데 축의금을 해야 하나요?"),
        QuestionSpec("계좌이체로 축의금을 보내도 괜찮나요?"),
        QuestionSpec("결혼식 옷차림은 어떻게 해야 하나요?"),
        QuestionSpec("흰색 옷이나 튀는 옷을 입어도 되나요?"),
        QuestionSpec("일본 결혼식에서는 ご祝儀 봉투를 어떻게 준비해야 하나요?", "일본 문화권이면 ご祝儀 봉투 준비와 전달 형식을 안내한다."),
        QuestionSpec("일본 결혼식에서는 얼마를 넣어야 하나요?", "일본 문화권의 관계별 ご祝儀 금액 관행을 반영한다."),
        QuestionSpec("일본 결혼식에서 피해야 하는 금액이나 숫자가 있나요?", "일본 문화권이면 나뉨이나 불길함을 연상시키는 금액과 숫자를 주의시킨다."),
        QuestionSpec("일본 결혼식 초대장 회신은 어떻게 해야 하나요?", "일본 문화권이면 초대장 회신 예절과 늦지 않게 답하는 점을 안내한다."),
        QuestionSpec("결혼 축하 메시지는 어떻게 보내면 좋나요?"),
        QuestionSpec("결혼식 축의금이나 선물은 얼마가 적당한가요?"),
        QuestionSpec("결혼식 옷차림은 어떻게 해야 하나요?"),
    ),
    "employment": (
        QuestionSpec("취업 축하금은 얼마가 적당한가요?"),
        QuestionSpec("이직 축하도 돈으로 챙겨야 하나요?"),
        QuestionSpec("첫 취업과 이직은 챙기는 방식이 다른가요?"),
        QuestionSpec("취업 축하로 현금, 상품권, 선물 중 뭐가 좋나요?"),
        QuestionSpec("취업한 친구에게 밥을 사주는 것만으로 충분한가요?"),
        QuestionSpec("직장 동료의 이직은 개인적으로 챙겨도 되나요?"),
        QuestionSpec("상사나 선배의 이직을 축하할 때 현금을 줘도 되나요?"),
        QuestionSpec("후배나 동생의 취업은 어느 정도 챙기는 게 자연스럽나요?"),
        QuestionSpec("취업 사실이 공개되지 않았는데 축하해도 되나요?", "공개 전인 취업/이직 사실은 먼저 축하하거나 SNS에 쓰지 않도록 조심시킨다."),
        QuestionSpec("SNS에 취업 축하 글을 올려도 되나요?"),
        QuestionSpec("일본에서는 취업 축하로 현금을 주는 게 자연스러운가요?", "일본 문화권이면 취업 축하 현금은 관계가 충분히 가까울 때만 조심스럽게 판단한다."),
        QuestionSpec("취업 축하 메시지는 어떻게 쓰면 좋나요?"),
        QuestionSpec("취업/이직 축하금이나 선물은 얼마가 적당한가요?"),
    ),
    "school_admission": (
        QuestionSpec("입학 축하금은 얼마가 적당한가요?"),
        QuestionSpec("초등학교 입학과 대학교 입학은 금액이 달라지나요?"),
        QuestionSpec("조카 입학은 얼마 정도 챙겨야 하나요?"),
        QuestionSpec("친구 자녀 입학도 챙겨야 하나요?"),
        QuestionSpec("동료 자녀 입학은 메시지만 보내도 되나요?"),
        QuestionSpec("입학 축하금은 아이에게 직접 줘야 하나요, 부모에게 줘야 하나요?"),
        QuestionSpec("입학 선물은 현금, 상품권, 물건 중 뭐가 좋나요?"),
        QuestionSpec("고가 선물을 사도 괜찮나요?"),
        QuestionSpec("일본에서는 入学祝い를 누구에게 주는 게 자연스럽나요?", "일본 문화권이면 入学祝い는 보통 가까운 가족·친척 중심임을 반영한다."),
        QuestionSpec("일본 초등학교 입학 선물로 란도셀을 사줘도 되나요?", "란도셀은 고가이고 취향·중복 문제가 크므로 사전 합의 없이는 추천하지 않는다."),
        QuestionSpec("입학 축하 메시지는 어떻게 보내면 좋나요?"),
        QuestionSpec("입학 축하금이나 선물은 얼마가 적당한가요?"),
    ),
    "business_opening": (
        QuestionSpec(
            "개업 축하를 어떻게 챙기면 좋을까요?",
            "관계, 소식 전달 방식, 개업 형태, 개업 시점, 방문 여부, 단체 축하 여부, 문화권을 바탕으로 개업 축하를 챙길지 먼저 판단한다. 적절하다면 현금, 화분/화환, 실용 선물, 메시지 중 가장 자연스러운 방식을 추천하고 가능하면 금액 범위를 제시한다. 화분이나 화환이 적절할 때만 문구 예시를 준다. 일본 문화권이면 공개 축하, 피해야 할 선물, 상대에게 부담이 되는 행동을 별도로 경고한다.",
        ),
        QuestionSpec(
            "개업한 곳에 방문해 축하한다면, 언제 어떻게 방문하는 것이 적절한가요?",
            "방문이 적절한지 먼저 판단한다. 방문한다면 개업 당일, 첫 주, 몇 주 후 중 언제가 덜 부담스러운지 안내한다. 매장/음식점/카페라면 바쁜 시간대를 피하고 손님으로 이용하거나 짧게 축하하는 방식을 우선한다. 응대 부담이 크면 방문보다 메시지나 비대면 선물을 추천한다.",
        ),
        QuestionSpec(
            "이 관계에서 개인적으로 챙겨도 부담스럽지 않을까요?",
            "관계 친밀도, 소식을 알게 된 방식, 단체 축하 분위기, 과거 히스토리를 바탕으로 개인 축하가 자연스러운지 판단한다. 애매하면 단체 참여, 작은 선물, 짧은 메시지 같은 부담 적은 대안을 제안한다.",
        ),
        QuestionSpec(
            "SNS에 홍보 글을 올려도 되나요?",
            "문화권, 공개 축하 선호, SNS 홍보 가능성, 공개 발표 여부, 관계 친밀도를 바탕으로 판단한다. 허락 없이 매장 내부 사진, 사람 얼굴, 가격표, 위치, 사업자 정보, 개인 계정 태그를 공개하지 말라고 안내한다. 일본 문화권이면 명시적 허락 없는 공개 축하나 홍보가 부담이 될 수 있음을 반영한다.",
        ),
    ),
    "first_birthday": (
        QuestionSpec(
            "첫돌 축하는 무엇으로, 어느 정도 챙기면 좋을까요?",
            "문화권, 부모와의 관계, 초대 여부, 참석 여부, 행사 형태, 단체 축하 분위기, 동반 참석 여부를 바탕으로 챙기는 것이 적절한지 판단한다. 적절하다면 현금, 금반지, 실용 선물, 상품권, 메시지 중 자연스러운 방식을 추천하고 가능하면 금액 범위를 제시한다. 한국은 돌잔치 참석 여부, 식사 제공, 관계 친밀도, 동반 인원에 따른 금액 차이를 반영한다. 일본은 한국식 돌잔치와 동일하게 보지 말고 첫 생일 선물 중심으로 판단한다. 초대받지 않았거나 관계가 멀다면 과한 현금보다 작은 선물이나 메시지를 우선한다.",
        ),
        QuestionSpec(
            "참석하거나 불참할 때 어떻게 챙기면 좋을까요?",
            "참석 여부, 초대 방식, 행사 형태, 식사 여부, 동반 참석 여부를 바탕으로 안내한다. 참석하면 식사 제공과 동반 인원에 따라 금액/선물 수준이 달라질 수 있음을 반영한다. 불참하면 정식 초대 후 불참과 단순히 소식만 들은 경우를 구분한다. 과한 선물, 갑작스러운 방문, 동반자 임의 참석을 피하게 한다.",
        ),
        QuestionSpec(
            "이 관계에서 개인적으로 챙기는 것이 적절할까요?",
            "부모와의 관계, 초대 여부, 소식 경로, 단체 축하 분위기, 사용자의 위치를 바탕으로 개인 축하가 자연스러운지 판단한다. 가족/친척, 매우 가까운 친구, 친구/동료, 가끔 연락하는 지인을 구분하고 애매하면 단체 축하, 간단한 메시지, 작은 선물을 제안한다.",
        ),
        QuestionSpec(
            "사진을 찍거나 SNS에 올려도 될까요?",
            "아기 사진이나 행사 공개 허락 여부, 문화권, 관계 친밀도, 참석 여부를 바탕으로 사진 촬영과 SNS 게시를 판단한다. 허락 없이 아기 얼굴, 부모 얼굴, 장소, 다른 참석자, 가족 정보를 올리지 말라고 안내한다. 촬영 가능과 SNS 공개 허락은 별개일 수 있음을 설명한다.",
        ),
        QuestionSpec(
            "축하 메시지는 어떻게 보내면 좋을까요?",
            "문화권, 부모와의 관계, 참석 여부, 선물/축의금 전달 여부를 바탕으로 메시지를 작성한다. 가까운 관계, 직장 동료, 가끔 연락하는 지인, 불참하는 경우를 구분하여 톤을 조절한다. 아이의 건강한 성장과 부모에 대한 축하를 중심으로 하되 답장 부담을 주지 않는다.",
        ),
    ),
    "funeral": (
        QuestionSpec(
            "부의금이나 조의금은 어느 정도가 적절할까요?",
            "문화권, 고인과의 관계, 유족/상주와의 관계, 업무·조직 관계, 부고 경로, 직접 조문 가능 여부, 단체 부의금 여부, 부의금/향전 사양 여부를 바탕으로 금전 조의가 적절한지 먼저 판단한다. 사양이면 금액 제시보다 사양 의사 존중을 우선한다. 일본이면 香典 관행과 종교·장례 방식별 봉투 표현 차이를 안내한다. 단체 부의금 참여 시 개인 추가가 필요한지 판단한다. 답변은 적절성, 권장 금액 범위, 단체 참여 판단, 사양 주의점 순서로 구성한다.",
        ),
        QuestionSpec(
            "직접 조문을 가야 할까요?",
            "문화권, 고인/유족과의 관계, 부고 경로, 빈소 안내, 가족장, 조문 사양, 현재 시점, 직접 조문 가능 여부를 바탕으로 판단한다. 가족장이나 조문 사양이면 유족 의사를 우선한다. 조문이 적절하면 언제, 얼마나 머물지, 단체 조문이 자연스러운지 안내한다. 못 가면 부의금, 단체 참여, 짧은 위로 메시지, 장례 후 연락 중 적절한 대안을 제안한다. 답변은 적절성, 방식, 가지 않는 게 나은 경우, 대신할 행동, 한 줄 행동지침 순서로 구성한다.",
        ),
        QuestionSpec(
            "조문 자리에서는 어떻게 입고 행동하면 좋을까요?",
            "문화권, 조문 여부, 복장 준비 상태, 장례 방식/종교를 바탕으로 복장과 행동을 안내한다. 검정 정장 가능 여부와 어두운 단정한 대안을 구분한다. 상의, 하의, 신발, 가방, 액세서리, 화장/향수처럼 실수하기 쉬운 요소를 간결히 포함한다. 사망 원인 캐묻기, 지나친 위로, 비교 발언, 사진 촬영, 웃고 떠들기, 유족을 오래 붙잡는 행동을 피하게 한다.",
        ),
        QuestionSpec(
            "부고나 장례 정보를 다른 사람에게 공유해도 될까요?",
            "문화권, 부고 경로, 공개 허락 여부, 빈소 안내, 가족장/조문 사양 여부를 바탕으로 공유 가능성을 판단한다. 공식 부고문이나 단체 공지 범위 안에서 필요한 사람에게 전달하는 것은 가능할 수 있으나 허락 없는 SNS 공유는 피하게 한다. 빈소 위치, 발인 시간, 고인 정보, 사망 원인, 유족 연락처, 계좌번호, 가족관계 정보는 민감정보로 다룬다.",
        ),
        QuestionSpec(
            "위로 메시지는 어떻게 보내면 좋을까요?",
            "문화권, 고인/유족과의 관계, 부고 경로, 직접 조문 여부, 장례 시점, 부의금 전달 여부, 조문 사양 여부를 바탕으로 짧고 정중한 메시지 예시 2~3개를 작성한다. 사망 원인이나 자세한 상황을 캐묻지 않으며, '힘내세요'처럼 부담될 수 있는 표현은 상황에 따라 피한다. 일본이면 반복이나 불행의 지속을 연상시키는 표현을 피한다.",
        ),
        QuestionSpec(
            "지금 시점에서 어떻게 조의를 전하면 좋을까요?",
            "문화권, 현재 장례 시점, 고인/유족과의 관계, 부고 경로, 직접 조문 가능 여부, 조문/부의금 사양 여부, 추모 행사까지 챙길 관계인지 여부를 바탕으로 지금 할 수 있는 행동, 하지 않는 것이 나은 행동, 필요하면 보낼 메시지 예시 순서로 간결하게 작성한다.",
        ),
    ),
    "hospital_visit": (
        QuestionSpec(
            "병문안을 가도 되는 상황인가요?",
            "문화권, 환자와의 관계, 소식 경로, 환자/보호자의 허락, 환자 상태, 병원 면회 규칙, 사용자의 감염 위험을 바탕으로 판단한다. 명확한 허락이 없으면 먼저 확인하게 한다. 환자가 쉬어야 하거나 수술/검사 직후, 감염 위험, 면회 제한, 사용자의 감기/기침/발열/감염병 접촉/컨디션 저하가 있으면 방문보다 메시지를 우선한다. 답변은 방문 가능 여부, 확인 대상, 가지 않는 게 나은 경우, 대신할 행동, 한 줄 행동지침 순서로 구성한다.",
        ),
        QuestionSpec(
            "병문안을 간다면 언제, 어떻게 가는 것이 좋을까요?",
            "문화권, 관계, 허락 여부, 환자 상태, 면회 시간, 예약/출입증, 보호자 확인 필요 여부를 바탕으로 방문 방식과 태도를 안내한다. 가족이 아닌 경우 먼저 방문 가능 여부와 시간을 확인하게 한다. 면회 시간 안에 짧게 머물고 환자가 피곤해 보이면 바로 나온다. 큰 소리, 오래 머물기, 여러 명 방문, 답변 강요를 피한다.",
        ),
        QuestionSpec(
            "병문안 선물이나 위로금은 무엇이 적절할까요?",
            "문화권, 관계, 선물/음식 반입 가능 여부, 꽃/화분 제한, 현금/위로금이 가능한 관계인지 바탕으로 판단한다. 실용 선물, 부담 없는 음료 쿠폰, 필요한 물품, 메시지 중 추천한다. 음식은 질환·식이 제한·병원 규칙상 확인된 경우만 추천한다. 꽃/화분은 규정, 알레르기, 감염 관리, 문화적 금기 때문에 확인되지 않으면 추천하지 않는다. 일본이면 お見舞い金 관행을 반영하되 가까운 관계가 아니면 부담을 설명한다.",
        ),
        QuestionSpec(
            "방문하지 않고 메시지만 보내도 괜찮을까요?",
            "문화권, 관계, 방문 허락 여부, 환자 상태, 면회 제한, 사용자의 감염 위험을 바탕으로 메시지만 보내도 되는지 판단한다. 환자가 쉬어야 하거나 방문을 원하지 않거나 면회 제한/감염 위험이 있으면 메시지만 보내는 것이 배려일 수 있음을 안내한다. 가까운 관계라면 보호자를 통해 필요한 것이 있는지 묻는 방법도 제안한다.",
        ),
        QuestionSpec(
            "병명이나 상태를 물어봐도 될까요?",
            "문화권, 관계, 환자가 먼저 공유했는지, 민감한 병 가능성, 자세히 물어봐도 되는 관계인지 바탕으로 판단한다. 가까운 가족이나 매우 가까운 사이가 아니면 병명, 수술 내용, 예후, 비용, 원인을 캐묻지 않게 한다. 먼저 말해주면 더 캐묻기보다 들어주고 공감한다. 일본 문화권은 사적인 건강 정보를 더 조심한다.",
        ),
        QuestionSpec(
            "병실 사진이나 입원 사실을 공개해도 될까요?",
            "문화권, 관계, 공개 허락 여부, 병원 규칙을 바탕으로 사진 촬영과 SNS 게시를 판단한다. 명시적 허락 없이 환자 얼굴, 병실, 병원명, 병명, 보호자, 다른 환자, 의료진이 보이는 사진을 찍거나 올리지 않는다. 환자가 허락해도 병원 규칙을 확인한다. 입원 사실 자체도 민감한 개인정보다.",
        ),
        QuestionSpec(
            "병문안 위로 메시지는 어떻게 보내면 좋을까요?",
            "문화권, 관계, 직접 방문 가능 여부, 선물/위로금 전달 여부, 환자 상태를 바탕으로 짧고 부담 없는 메시지 예시 2~3개를 작성한다. 답장을 강요하지 않고 회복을 기원하며 쉬어도 괜찮다는 느낌을 준다. 병명·원인 캐묻기, 과한 낙관, 비교, 부담스러운 표현을 피한다.",
        ),
    ),
}

CATEGORY_GUIDES = {
    "birth": "출산 축하는 관계, 출산 시점, 방문 허락, 첫째/둘째 여부, 사용자의 위치, 문화권을 함께 본다. 산모와 아기의 휴식·안전·사생활을 최우선으로 두고, 방문과 사진/SNS는 명시적 허락 없이는 피한다.",
    "wedding": "결혼 축하는 초대 강도, 참석/식사 여부, 관계, 동행인, 전달 방식, 일본 초대장 회신 여부를 함께 본다. 한국은 참석·식사·관계·동행 인원이 금액에 영향을 주고, 일본은 ご祝儀 형식과 숫자 금기를 반영한다.",
    "employment": "취업/이직 축하는 첫 취업인지 이직인지, 관계와 선후배 위치, 단체 분위기, 공개 여부를 함께 본다. 현금보다 식사·상품권·작은 선물이 자연스러운 관계가 많고, 공개 전 축하나 SNS 게시는 조심한다.",
    "school_admission": "입학 축하는 학교 단계, 아이/부모와의 관계, 전달 대상, 단체 분위기, 고가 선물 여부를 함께 본다. 어린 아이는 부모를 통해 전달하는 편이 안전하며, 일본의 入学祝い는 가까운 가족·친척 중심으로 판단한다.",
    "business_opening": "개업/창업 축하는 관계, 소식 경로, 방문 여부, 개업 형태, 시점, 공개 축하 선호, 단체 축하 여부를 함께 본다. 방문은 상대의 영업과 응대 부담을 줄이는 방식이어야 하고, SNS 홍보는 허락을 우선한다.",
    "first_birthday": "첫돌 축하는 부모와의 관계, 초대 여부, 참석 여부, 행사 형태, 선물 분위기, 동반 참석, 사진 공개 허락을 함께 본다. 한국 돌잔치와 일본 첫 생일 축하를 구분하고, 아기 사진/SNS는 허락 없이는 피한다.",
    "funeral": "장례/부고/조문은 고인과 유족 중 누구와 가까운지, 부고 경로, 공개 조문 여부, 현재 시점, 부의금/향전 사양, 단체 조문 여부, 종교·장례 방식, 복장, 정보 공개 허락을 함께 본다. 유족의 사양 의사와 개인정보 보호를 최우선으로 둔다.",
    "hospital_visit": "병문안은 환자와의 관계, 소식 경로, 방문 허락, 환자 상태, 병원 규칙, 사용자의 감염 위험, 선물/음식 제한, 건강정보·사진 공개 허락을 함께 본다. 환자의 회복, 휴식, 감염 예방, 개인정보 보호를 최우선으로 둔다.",
}


def get_gemini_answer(
    language: str,
    histories: list[dict[str, Any]],
    question: str,
    memory: str,
    *,
    current_context: dict[str, Any] | None = None,
    category: str | None = None,
    target_name: str = "",
    culture_base: str | None = None,
) -> GeminiResult:
    """Return Gemini advice as a JSON string with exactly money/text keys."""

    context = current_context or {}
    normalized_category = _normalize_category(
        category
        or _string_or_none(context.get("category"))
        or _infer_category_from_question(question)
    )
    if not normalized_category:
        allowed = ", ".join(CATEGORY_LABELS)
        return _wrap_result(False, f"category must be one of: {allowed}")

    normalized_culture = _normalize_culture(
        culture_base
        or _string_or_none(context.get("cultureBase"))
        or _string_or_none(context.get("culture_base"))
    )
    resolved_target_name = (
        target_name
        or _string_or_none(context.get("targetName"))
        or _string_or_none(context.get("target_name"))
        or ""
    )
    matched_specs = _match_question_specs(normalized_category, question)
    prompt = _build_prompt(
        language=language,
        histories=histories,
        question=question,
        memory=memory,
        category=normalized_category,
        culture_base=normalized_culture,
        target_name=resolved_target_name,
        current_context=context,
        matched_specs=matched_specs,
    )

    success, raw_answer = _call_gemini(prompt)
    if not success:
        return _wrap_result(False, raw_answer)

    try:
        answer = _normalize_answer_payload(raw_answer)
    except ValueError as exc:
        return _wrap_result(False, str(exc))

    return _wrap_result(True, json.dumps(answer, ensure_ascii=False))


def get_gemini_category_report(
    language: str,
    histories: list[dict[str, Any]],
    current_context: dict[str, Any],
    category: str,
    *,
    target_name: str = "",
    culture_base: str | None = None,
) -> GeminiResult:
    """Answer all app-supported questions for a category in one money/text JSON."""

    normalized_category = _normalize_category(category)
    if not normalized_category:
        allowed = ", ".join(CATEGORY_LABELS)
        return _wrap_result(False, f"category must be one of: {allowed}")

    all_questions = CATEGORY_RESPONSE_QUESTIONS[normalized_category]
    joined_questions = "\n".join(f"- {spec.question}" for spec in all_questions)
    return get_gemini_answer(
        language,
        histories,
        f"아래 앱 질문 전체에 답해 주세요.\n{joined_questions}",
        "",
        current_context=current_context,
        category=normalized_category,
        target_name=target_name,
        culture_base=culture_base,
    )


def _build_prompt(
    *,
    language: str,
    histories: list[dict[str, Any]],
    question: str,
    memory: str,
    category: str,
    culture_base: str,
    target_name: str,
    current_context: dict[str, Any],
    matched_specs: tuple[QuestionSpec, ...],
) -> str:
    language_label = LANGUAGE_LABELS.get(language, language or "Korean")
    category_label = CATEGORY_LABELS[category]
    question_block = _format_question_specs(matched_specs)
    allowed_questions = "\n".join(
        f"- {spec.question}" for spec in CATEGORY_RESPONSE_QUESTIONS[category]
    )

    return f"""
You are JanJan, an etiquette and money advisor for Korean and Japanese life-event customs.

Core task:
- Treat the pre-survey answers as the user's current situation, not optional background.
- Treat payment history as this same target person's past congratulations/condolence data.
- Answer only within the selected category and the current situation.
- Use the detailed prompt notes for the selected app question.
- Return valid JSON only with exactly these top-level keys: money, text.

Output JSON shape:
{{
  "money": "recommended amount/range and currency, or 0 with a reason when money is not appropriate",
  "text": "direct practical answer to the user's selected app question"
}}

Answer language:
- {language_label}

Selected category:
- key: {category}
- label: {category_label}

Category guidance:
{CATEGORY_GUIDES[category]}

Selected app question:
{question}

Question-specific prompt notes to apply:
{question_block}

All allowed app questions for this category:
{allowed_questions}

Current target:
- name: {target_name or "unknown"}
- cultureBase: {culture_base}

Current pre-survey answers:
{_pretty_json(current_context)}

Past history with this target:
{_pretty_json(histories)}

Previous chat memory:
{memory or "none"}

Answer rules:
- money must include a concrete amount or range whenever spending money is appropriate.
- If money is not appropriate, money must clearly say 0 and name the better action, such as message only, group contribution only, visit later, or no public action.
- text must explain why the amount/action fits this relationship, culture, timing, and history.
- Always include key etiquette warnings when the current situation makes them relevant.
- Include a message example when the selected question asks about messages, or when a short wording example helps the user act.
- Do not invent facts not present in the pre-survey or history. When uncertain, choose the safer and less burdensome option.
- Do not include Markdown code fences, commentary outside JSON, or extra top-level keys.
""".strip()


def _format_question_specs(specs: tuple[QuestionSpec, ...]) -> str:
    if not specs:
        return (
            "The user's question does not exactly match one allowed app question. "
            "Answer it only if it is a close follow-up to the selected category; "
            "otherwise explain the closest supported question and stay within money/text JSON."
        )

    lines = []
    for spec in specs:
        lines.append(f"- Question: {spec.question}")
        if spec.prompt:
            lines.append(f"  Prompt note: {spec.prompt}")
    return "\n".join(lines)


def _match_question_specs(category: str, question: str) -> tuple[QuestionSpec, ...]:
    normalized_question = _normalize_text(question)
    if not normalized_question:
        return CATEGORY_RESPONSE_QUESTIONS[category]

    exact_matches = tuple(
        spec
        for spec in CATEGORY_RESPONSE_QUESTIONS[category]
        if _normalize_text(spec.question) == normalized_question
    )
    if exact_matches:
        return exact_matches

    contained_matches = tuple(
        spec
        for spec in CATEGORY_RESPONSE_QUESTIONS[category]
        if _normalize_text(spec.question) in normalized_question
        or normalized_question in _normalize_text(spec.question)
    )
    return contained_matches


def _infer_category_from_question(question: str) -> str | None:
    normalized_question = _normalize_text(question)
    if not normalized_question:
        return None

    for category, specs in CATEGORY_RESPONSE_QUESTIONS.items():
        for spec in specs:
            normalized_spec = _normalize_text(spec.question)
            if normalized_spec == normalized_question:
                return category
            if normalized_spec and normalized_spec in normalized_question:
                return category
    return None


def _normalize_category(category: str | None) -> str | None:
    if not category:
        return None
    normalized = category.strip()
    normalized = CATEGORY_ALIASES.get(normalized, normalized)
    if normalized in CATEGORY_LABELS:
        return normalized
    return None


def _normalize_culture(culture_base: str | None) -> str:
    if not culture_base:
        return "unknown"
    normalized = culture_base.strip().lower()
    return CULTURE_ALIASES.get(culture_base.strip(), CULTURE_ALIASES.get(normalized, normalized))


def _normalize_text(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"\s+", "", value)
    value = value.rstrip("?？")
    return value


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _call_gemini(prompt: str) -> tuple[bool, str]:
    _load_dotenv_files()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return False, "Gemini API key is missing. Set GEMINI_API_KEY or GOOGLE_API_KEY."

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    url = API_ENDPOINT.format(model=model)
    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are a careful Korean/Japanese etiquette advisor. "
                        "You must return strict JSON only, with exactly money and text keys."
                    )
                }
            ]
        },
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json",
        },
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return False, _format_error(exc.code, error_body)
    except urllib.error.URLError as exc:
        return False, f"Gemini API connection failed: {exc.reason}"
    except TimeoutError:
        return False, "Gemini API request timed out."

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError:
        return False, "Gemini API returned invalid JSON."

    text = _extract_text(data)
    if not text:
        return False, "Gemini API returned an empty response."
    return True, text


def _wrap_result(success: bool, answer: str) -> GeminiResult:
    return {
        "success": success,
        "answer": answer,
    }


def _normalize_answer_payload(raw_answer: str) -> dict[str, str]:
    parsed = _parse_json_object(raw_answer)
    if not isinstance(parsed, dict):
        raise ValueError("Gemini response must be a JSON object.")

    money = parsed.get("money")
    text = parsed.get("text")
    if text is None or str(text).strip() == "":
        raise ValueError("Gemini response JSON must include non-empty text.")

    return {
        "money": _stringify_json_value(money if money is not None else "0"),
        "text": _stringify_json_value(text),
    }


def _parse_json_object(raw_answer: str) -> Any:
    text = raw_answer.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Gemini response was not valid JSON.")
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"Gemini response was not valid JSON: {exc}") from exc


def _stringify_json_value(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _extract_text(data: dict[str, Any]) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        return ""

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    return "\n".join(part for part in text_parts if part).strip()


def _format_error(status_code: int, error_body: str) -> str:
    try:
        parsed = json.loads(error_body)
    except json.JSONDecodeError:
        return f"Gemini API request failed with HTTP {status_code}: {error_body}"

    message = parsed.get("error", {}).get("message") or error_body
    return f"Gemini API request failed with HTTP {status_code}: {message}"


def _load_dotenv_files() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return

    _DOTENV_LOADED = True
    seen: set[Path] = set()
    search_roots = (Path.cwd(), Path(__file__).resolve().parent)

    for root in search_roots:
        for directory in (root, *root.parents):
            dotenv_path = directory / ".env"
            if dotenv_path in seen:
                continue

            seen.add(dotenv_path)
            if dotenv_path.is_file():
                _load_dotenv_file(dotenv_path)


def _load_dotenv_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)
