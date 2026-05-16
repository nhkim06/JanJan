from __future__ import annotations

import json
import re
from typing import Any, Final

try:
    from .gemini_client import call_gemini, pretty_json, pretty_question
    from .language_rules import language_output_rule
    from .type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from gemini_client import call_gemini, pretty_json, pretty_question
    from language_rules import language_output_rule
    from type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )


BASE_SYSTEM_INSTRUCTION = """
You are JanJan, a money and gift-cost advisor for Korean and Japanese life-event customs.
Give practical, culturally careful guidance only for cash gifts, gift value, group
contributions, account transfers, and cases where spending money is inappropriate. Consider
reciprocity from the payment history, but do not treat it as a rigid debt. Avoid stereotypes,
explain uncertainty, and prefer options that reduce social burden. Always answer in the
requested output language. Do not let currency, culture marker, question text, survey text,
or history choose the output language.

The question data is not optional background. It is the user's current situation itself.
Treat it as the authoritative boundary of the task. Only output money, gift, or payment
guidance that is limited to that current situation. Do not output guidance for other possible
cases in the same category, and do not explain etiquette points that fall outside the money
or gift decision.
Category customs and payment history are secondary context only; they must never override or
expand beyond the current situation described by the question data. Every recommendation must
answer: "What amount or money/gift choice fits this exact situation?"

For every category, synthesize the question data into user-facing money guidance instead of
answering each survey question separately. Do not produce a broad category guide. Do not
output visit manners, attire, photo/SNS cautions, message wording, or other non-money advice.
Non-money details may be used only as private context for deciding the spending
recommendation. The answer must read like advice written for an end user, not like an
internal report, schema, JSON, form field list, or developer output.

The function output must contain exactly two user-facing items:
1. A natural prose recommendation about cash, gift, group contribution, account transfer, or
   not spending money. This recommendation text must be 300 to 600 characters, including
   spaces and punctuation.
2. Exactly one integer for the event spending amount followed by one space and the required
   currency unit, with no comma, range, label, or explanation.

Never output internal labels, field names, snake_case names, JSON-like keys, or developer
schema markers. If giving money is inappropriate because the other side refused money or the
relationship is too distant, explain that in the recommendation and set the amount item to 0.
""".strip()

BIRTH_SYSTEM_INSTRUCTION = """
Category: birth / childbirth.
종합해야 할 질문: 출산 축하금, 출산 선물의 현금/물건 선택, 직장 동료 출산을 개인/단체로 챙길지, 친하지 않은 지인의 출산을 금전적으로 챙길지, 첫째와 둘째 이상일 때 축하금 차이, 일본의 出産祝い 시기와 현금 관행.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- Decide whether money, a practical gift, a group gift, or no spending is most natural from relationship, closeness, timing, culture/currency marker, and history.
- For Korea, consider whether this is the first child or later child, whether the user is family, close friend, coworker, or distant acquaintance, and whether a group contribution is more natural.
- For Japan, be careful about giving before birth; generally judge 出産祝い after mother and baby are safe, and consider that cash can be acceptable when relationship and format fit.
- Warn only about money or gifts that create care burden; do not include visit, photo/SNS, or message-writing advice.
""".strip()

WEDDING_SYSTEM_INSTRUCTION = """
Category: wedding.
종합해야 할 질문: 결혼식 축의금, 불참 시 축의금 여부, 식사하지 않는 경우 금액 조정, 친구/동료/친척/거래처별 차이, 모바일 청첩장만 받은 경우의 금액, 계좌이체 가능성, 일본 ご祝儀 금액, 피해야 하는 숫자/금액.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- Decide the proper congratulations amount by attendance, meal/reception participation, invitation strength, relationship closeness, group/organization norms, plus reciprocity history.
- Distinguish formal invitation, mobile-only notice, casual news, and inability to attend; explain whether account transfer is acceptable and how to make it polite.
- For Korea, reflect that attendance, meal, relationship, and companion count can change the socially expected amount.
- For Japan, reflect ご祝儀 format, envelope preparation, avoiding split-associated or unlucky amounts/numbers when relevant, and the importance of replying to invitations properly.
- Warn only about payment-related mistakes, such as lowering money too aggressively because the user will not eat, sending money too casually in a close relationship, or treating every mobile notice as equal to a formal invitation.
""".strip()

EMPLOYMENT_SYSTEM_INSTRUCTION = """
Category: employment / job change.
종합해야 할 질문: 취업 축하금, 이직 축하를 돈으로 챙길지, 첫 취업과 이직의 차이, 현금/상품권/선물 선택, 식사 대접만으로 충분한지, 상사/선배에게 현금이 자연스러운지, 후배/동생 취업 축하 수준, 일본 취업 축하 현금 관행.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- Decide whether money, a meal treat, a gift card, a practical work item, or no spending is most natural from relationship, seniority, whether this is first employment or job change, publicity of the news, and history.
- Treat first employment, job change, promotion-like move, and coworker departure differently; avoid over-formal money when a meal or small gift is more socially natural.
- For seniors, managers, and not-close coworkers, prefer a group gift, meal treat, or small practical item over personal cash unless the relationship clearly supports it.
- For Japan, be conservative about cash for employment congratulations; consider gift or meal treat depending on relationship.
- Warn only about money or gift choices that could embarrass a senior, manager, coworker, or distant relationship; do not include message or SNS advice.
""".strip()

SCHOOL_ADMISSION_SYSTEM_INSTRUCTION = """
Category: school admission.
종합해야 할 질문: 입학 축하금, 초등학교/대학교 등 학교급별 차이, 조카 입학 금액, 아이에게 직접 줄지 부모에게 줄지, 현금/상품권/물건 선택, 고가 선물 가능성.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- Decide whether money, gift card, school supplies, practical item, or no spending is most natural from the child's school stage, relationship to child/parents, invitation or notice strength, family closeness, and history.
- Distinguish close family/relatives, close friends' children, coworkers' children, and distant acquaintances; avoid making a distant relationship feel obligated to return a favor.
- Decide whether to give to the child or parent; for younger children, parent-facing delivery is often safer unless family custom says otherwise.
- For Japan, judge 入学祝い as usually for close family/relatives, and warn that a randoseru is expensive and preference-sensitive, so it should not be bought without prior agreement.
- Warn only about expensive surprise gifts, gifts that ignore school rules, or cash/gifts that create return pressure; do not include message or public-sharing advice.
""".strip()

BUSINESS_OPENING_SYSTEM_INSTRUCTION = """
Category: business opening / startup.
종합해야 할 질문: 개업 축하를 금전적으로 챙길지, 관계/소식 전달 방식/개업 형태/시점/단체 축하/문화권에 따른 현금·화분·화환·실용 선물 선택, 개인적으로 챙겨도 부담스럽지 않은 금액인지.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- First judge whether spending money is appropriate at all. If yes, recommend the most natural form among money, plant/flower stand, practical business gift, becoming a paying customer, group gift, or no spending.
- Consider relationship closeness, whether the opening was publicly announced, business type, opening day vs first week vs later timing, group norms, and history only to decide spending.
- Judge plant/flower stand budget only if that gift type is actually appropriate.
- For Japan, be especially careful about unlucky or burdening gifts and spending that creates obligation or embarrassment.
- Warn only about money or gift mistakes, such as sending oversized flowers to a small space, expensive surprise gifts, or gifts that create business burden.
""".strip()

FIRST_BIRTHDAY_SYSTEM_INSTRUCTION = """
Category: first birthday / doljanchi.
종합해야 할 질문: 첫돌 축하를 현금/금반지/선물/상품권 중 무엇으로 어느 정도 챙길지, 참석/불참 상황에 따른 금액, 개인적으로 챙기는 것이 적절한지.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- Decide whether money, gold ring, practical baby gift, gift card, group gift, or no additional spending is most natural from parent relationship, invitation status, attendance, event format, meal, group mood, companion count, culture/currency marker, and history.
- For Korea, reflect that doljanchi attendance, meal provision, relationship closeness, and companion count can affect the cash-gift level.
- For Japan, do not treat the event exactly like a Korean doljanchi unless the family is holding one; judge it more as a first-birthday gift situation.
- Distinguish formal invitation, nonattendance after invitation, simply hearing the news, and distant relationship.
- Warn only about excessive cash, expensive surprise gifts, group-gift pressure, or gifts that burden the parents; do not include visit, photo/SNS, or message advice.
""".strip()

FUNERAL_SYSTEM_INSTRUCTION = """
Category: funeral / obituary / condolence visit.
종합해야 할 질문: 부의금/조의금 적정 금액, 직접 조문 여부가 금액에 미치는 영향, 단체 조의금 여부, 현재 시점에서 금전 조의를 해도 되는지.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- First judge whether monetary condolence is appropriate. If money or visit has been refused, or the funeral is family-only/visits declined, prioritize respecting that request and set recommended_amount to 0 unless the data clearly says another route is accepted.
- If money is appropriate, judge by culture/currency marker, relationship to the deceased, relationship to the bereaved/chief mourner, work/organization context, how the obituary was received, visit possibility, group contribution, and history.
- Distinguish close to deceased, close to bereaved, close to both, workplace/organization relationship, and barely knowing either side.
- If the user joined a group condolence payment, decide whether that alone is enough or whether a personal addition is appropriate.
- For Japan, reflect 香典 customs and payment amount conventions; do not explain ceremony attendance unless it changes the amount.
- Use visit and notice context only to decide whether condolence money is appropriate; do not include clothing, behavior, message, photo/SNS, or funeral-detail sharing advice.
- Warn only about payment-related mistakes, such as forcing money after refusal, adding personal money when group payment is already enough, or making the amount feel performative.
""".strip()

HOSPITAL_VISIT_SYSTEM_INSTRUCTION = """
Category: hospital visit / illness consolation.
종합해야 할 질문: 병문안 선물/위로금, 방문 여부가 선물이나 금액에 미치는 영향, 환자 상태와 병원 규칙에 맞는 선물 선택, 현금/상품권/실용 선물/무지출 중 무엇이 적절한지.

Report requirements:
- Start naturally with the current situation in prose; do not write any section label.
- Use patient condition, permission, hospital rules, and relationship closeness only to decide whether money or a practical gift is appropriate.
- For gifts or money, decide whether practical small gift, drink coupon, needed item, cash, or no spending is natural. Food should be recommended only when diet and hospital rules allow it. Flowers/plants should not be recommended unless rules, allergies, infection control, and culture fit.
- For Japan, reflect お見舞い金 only when the relationship is close enough and warn about gifts or expressions that can feel unlucky or burdensome.
- Warn only about money or gift mistakes, such as burdensome food, flowers/plants against rules, overly expensive gifts, or cash that feels inappropriate for the relationship.
""".strip()

CATEGORY_ALIASES: Final[dict[str, OccasionCategory]] = {
    "childbirth": "birth",
    "business": "business_opening",
}

CURRENCY_FIELD_NAMES: Final[tuple[str, ...]] = (
    "currency",
    "currencyCode",
    "currency_code",
    "cultureBase",
    "culture_base",
    "country",
    "countryCode",
    "country_code",
)

CURRENCY_MARKER_TO_UNIT: Final[dict[str, str]] = {
    "ko": "KRW",
    "kr": "KRW",
    "korea": "KRW",
    "southkorea": "KRW",
    "republicofkorea": "KRW",
    "krw": "KRW",
    "won": "KRW",
    "₩": "KRW",
    "원": "KRW",
    "ja": "JPY",
    "jp": "JPY",
    "japan": "JPY",
    "jpy": "JPY",
    "yen": "JPY",
    "¥": "JPY",
    "엔": "JPY",
    "us": "USD",
    "usa": "USD",
    "america": "USD",
    "unitedstates": "USD",
    "usd": "USD",
    "dollar": "USD",
    "$": "USD",
}

MONEY_CALCULATOR_QUESTIONS: Final[dict[OccasionCategory, tuple[str, ...]]] = {
    "birth": (
        "출산 축하금은 얼마가 적당한가요?",
        "출산 선물은 현금이 좋나요, 물건이 좋나요?",
        "직장 동료 출산은 개인적으로 챙겨야 하나요, 단체로 챙겨야 하나요?",
        "친하지 않은 지인의 출산도 챙겨야 하나요?",
        "첫째와 둘째 이상일 때 축하금이 달라지나요?",
        "일본에서는 出産祝い를 언제 주는 게 적절한가요?",
        "일본에서는 출산 축하로 현금을 줘도 되나요?",
    ),
    "wedding": (
        "결혼식 축의금은 얼마가 적당한가요?",
        "결혼식에 참석하지 못하면 축의금을 보내야 하나요?",
        "식사를 안 하면 축의금을 줄여도 되나요?",
        "친구, 동료, 친척, 거래처별 축의금은 어떻게 다른가요?",
        "모바일 청첩장만 받았는데 축의금을 해야 하나요?",
        "계좌이체로 축의금을 보내도 괜찮나요?",
        "일본 결혼식에서는 ご祝儀 봉투를 어떻게 준비해야 하나요?",
        "일본 결혼식에서는 얼마를 넣어야 하나요?",
        "일본 결혼식에서 피해야 하는 금액이나 숫자가 있나요?",
    ),
    "employment": (
        "취업 축하금은 얼마가 적당한가요?",
        "이직 축하도 돈으로 챙겨야 하나요?",
        "첫 취업과 이직은 챙기는 방식이 다른가요?",
        "취업 축하로 현금, 상품권, 선물 중 뭐가 좋나요?",
        "취업한 친구에게 밥을 사주는 것만으로 충분한가요?",
        "상사나 선배의 이직을 축하할 때 현금을 줘도 되나요?",
        "후배나 동생의 취업은 어느 정도 챙기는 게 자연스럽나요?",
        "일본에서는 취업 축하로 현금을 주는 게 자연스러운가요?",
    ),
    "school_admission": (
        "입학 축하금은 얼마가 적당한가요?",
        "초등학교 입학과 대학교 입학은 금액이 달라지나요?",
        "조카 입학은 얼마 정도 챙겨야 하나요?",
        "입학 축하금은 아이에게 직접 줘야 하나요, 부모에게 줘야 하나요?",
        "입학 선물은 현금, 상품권, 물건 중 뭐가 좋나요?",
        "고가 선물을 사도 괜찮나요?",
    ),
    "business_opening": (
        "개업 축하를 어떻게 챙기면 좋을까요?",
    ),
    "first_birthday": (
        "첫돌 축하는 무엇으로, 어느 정도 챙기면 좋을까요?",
        "참석하거나 불참할 때 어떻게 챙기면 좋을까요?",
        "이 관계에서 개인적으로 챙기는 것이 적절할까요?",
    ),
    "funeral": (
        "부의금이나 조의금은 어느 정도가 적절할까요?",
    ),
    "hospital_visit": (
        "병문안 선물이나 위로금은 무엇이 적절할까요?",
    ),
}


def proper_payment_amount(
    language: str,
    histories: list[History],
    question: Any,
    category: str,
    currency: Any | None = None,
) -> AIResponse:
    normalized_category = _normalize_category(category)
    if normalized_category is None:
        allowed = ", ".join((*OCCASION_CATEGORIES, *CATEGORY_ALIASES))
        return {"success": False, "answer": f"category must be one of: {allowed}"}

    invalid_reason = validate_histories(histories)
    if invalid_reason:
        return {"success": False, "answer": invalid_reason}

    raw_currency = currency if currency is not None else _extract_currency_marker(question)
    currency_unit = _resolve_currency_unit(raw_currency)
    prompt = _build_prompt(
        language,
        histories,
        question,
        normalized_category,
        raw_currency=raw_currency,
        currency_unit=currency_unit,
    )
    response = call_gemini(
        prompt,
        system_instruction=_system_instruction_for_category(normalized_category),
        temperature=0.25,
        max_output_tokens=4000,
    )
    if response["success"] and currency_unit:
        response["answer"] = _ensure_recommended_amount_currency(
            response["answer"],
            currency_unit,
        )
    return response


def _build_prompt(
    language: str,
    histories: list[History],
    question: Any,
    category: OccasionCategory,
    *,
    raw_currency: Any,
    currency_unit: str | None,
) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    amount_format_rule = _amount_format_rule(currency_unit)
    amount_line_rule = _amount_line_rule(currency_unit)
    currency_display = _format_raw_currency(raw_currency)
    output_language_rule = language_output_rule(language)
    required_unit_display = currency_unit or "(infer from question.currency/country)"
    return f"""
Task:
Create money-related guidance for the current situation defined by the question data, then
recommend one proper congratulations/condolence spending amount.

Current situation rule:
- The question data below is the user's current situation itself.
- Treat every answered question as a concrete constraint on what the user should spend now.
- This function is the money calculator. Answer only the questions classified exactly as
  "(돈계산기)" for the current category.
- If the incoming question data includes etiquette-villain-prevention or message questions,
  do not answer those questions and do not summarize them. Use them only as private context
  if they directly change the money/gift amount.
- Output only money, gift, group contribution, account transfer, or no-spending guidance that
  is limited to this current situation.
- Do not output advice for other cases, other relationships, other attendance states, other
  cultures, or other timing unless they are explicitly part of the question data.
- Do not replace the current situation with generic category advice.
- Use category customs and payment history only to interpret this exact situation, not to
  expand the answer beyond it.
- If the question data conflicts with payment history or general etiquette, follow the
  question data and explain the uncertainty briefly in the money recommendation.

Output language:
{output_language_rule}

Output rules:
- Return plain text only.
- Output exactly two lines and nothing else.
- First line: one natural prose paragraph about cash, gift, group contribution, account
  transfer, or not spending money. This paragraph must be 300 to 600 characters, including
  spaces and punctuation.
- Second line: {amount_format_rule}
- Do not write headings, numbering, bullet markers, or labels such as Money recommendation or
  Recommended amount.
- The first item must discuss only money, gifts, group contributions, account transfers, or
  why spending money is inappropriate. Do not include visit manners, clothing, photo/SNS
  cautions, message examples, ad ideas, or other etiquette advice.
- Before returning, verify internally that the first item is 300 to 600 characters total,
  including spaces and punctuation.
- {amount_line_rule}
- Explain the concrete social context from the question data, relevant reciprocity from
  payment history, and why the final amount fits inside the first item.
- If there is not enough information, still give the safest conservative amount and briefly
  name the missing money-related factors in the first item.
- Use the payment history only when it is relevant to this person, relationship, category,
  timing, currency/culture marker, or reciprocity context.

Payment history schema note:
- Each history item uses currency to mark the cash/culture context of that past amount.
- currency values are ko, ja, both, unknown, or ISO currency codes such as KRW, JPY, USD.

Current event category:
- key: {category}
- label: {category_label}

Current output currency:
- raw_input: {currency_display}
- required_unit: {required_unit_display}
- The recommended amount must always use this currency unit. Do not switch to another
  country's money and do not omit the unit.

Allowed "(돈계산기)" questions for this category:
{_format_money_calculator_questions(category)}

Current situation constraints from question data:
{_format_question_data(question)}

Payment history:
{pretty_json(histories)}
""".strip()


def _normalize_category(category: str) -> OccasionCategory | None:
    normalized = category.strip()
    normalized = CATEGORY_ALIASES.get(normalized, normalized)
    if is_occasion_category(normalized):
        return normalized
    return None


def _extract_currency_marker(value: Any) -> Any | None:
    if isinstance(value, dict):
        for field_name in CURRENCY_FIELD_NAMES:
            if field_name in value:
                return value[field_name]

        for nested_value in value.values():
            marker = _extract_currency_marker(nested_value)
            if marker is not None:
                return marker
        return None

    if isinstance(value, (list, tuple)):
        for item in value:
            marker = _extract_currency_marker(item)
            if marker is not None:
                return marker
        return None

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None

        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            parsed = None
        if parsed is not None:
            marker = _extract_currency_marker(parsed)
            if marker is not None:
                return marker

        match = re.search(
            r"\b(?:currency|currencyCode|currency_code|cultureBase|culture_base|country|countryCode|country_code)\b\s*[:=]\s*['\"]?([A-Za-z_$¥₩원엔]+)",
            stripped,
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1)

    return None


def _resolve_currency_unit(value: Any) -> str | None:
    if value is None:
        return None

    marker = str(value).strip()
    if not marker:
        return None

    normalized = re.sub(r"[\s_\-]+", "", marker.casefold())
    if normalized in {"both", "unknown"}:
        return None

    mapped_unit = CURRENCY_MARKER_TO_UNIT.get(normalized)
    if mapped_unit:
        return mapped_unit

    compact_upper = re.sub(r"[^A-Za-z]", "", marker).upper()
    if len(compact_upper) == 3:
        return compact_upper

    return None


def _format_raw_currency(value: Any) -> str:
    if value is None:
        return "(not provided)"
    if isinstance(value, str):
        return value.strip() or "(not provided)"
    return pretty_json(value)


def _amount_format_rule(currency_unit: str | None) -> str:
    if currency_unit:
        return (
            "exactly one integer followed by one space and "
            f"{currency_unit}."
        )
    return (
        "exactly one integer followed by one space and the currency unit "
        "from the input currency/country."
    )


def _amount_line_rule(currency_unit: str | None) -> str:
    if currency_unit:
        return (
            "The second item must contain one integer with no comma, range, or explanation, "
            f"followed by exactly one space and {currency_unit}. Use 0 {currency_unit} when "
            "money/gift spending is not appropriate."
        )
    return (
        "The second item must contain one integer with no comma, range, or explanation, "
        "followed by exactly one space and the input currency unit. Use 0 with the same "
        "currency unit when money/gift spending is not appropriate."
    )


def _ensure_recommended_amount_currency(answer: str, currency_unit: str) -> str:
    pattern = re.compile(
        r"^(?P<prefix>\s*(?:\d+\.\s*)?Recommended amount\s*:\s*)(?P<value>.*)$",
        flags=re.IGNORECASE | re.MULTILINE,
    )

    def replace_amount_line(match: re.Match[str]) -> str:
        return (
            f"{match.group('prefix')}"
            f"{_format_amount_with_currency(match.group('value'), currency_unit)}"
        )

    normalized_answer, replacement_count = pattern.subn(
        replace_amount_line,
        answer,
        count=1,
    )
    if replacement_count:
        return normalized_answer

    lines = answer.splitlines()
    for index in range(len(lines) - 1, -1, -1):
        if not lines[index].strip():
            continue

        line_match = re.match(r"^(?P<prefix>\s*(?:\d+\.\s*)?)(?P<value>.*)$", lines[index])
        if line_match:
            lines[index] = (
                f"{line_match.group('prefix')}"
                f"{_format_amount_with_currency(line_match.group('value'), currency_unit)}"
            )
        else:
            lines[index] = _format_amount_with_currency(lines[index], currency_unit)
        return "\n".join(lines)

    return f"0 {currency_unit}"


def _format_amount_with_currency(value: str, currency_unit: str) -> str:
    amount_match = re.search(r"\d[\d,]*", value)
    if not amount_match:
        return f"0 {currency_unit}"

    amount = re.sub(r"\D", "", amount_match.group(0))
    return f"{amount} {currency_unit}"


def _system_instruction_for_category(category: OccasionCategory) -> str:
    if category == "birth":
        category_instruction = BIRTH_SYSTEM_INSTRUCTION
    elif category == "wedding":
        category_instruction = WEDDING_SYSTEM_INSTRUCTION
    elif category == "employment":
        category_instruction = EMPLOYMENT_SYSTEM_INSTRUCTION
    elif category == "school_admission":
        category_instruction = SCHOOL_ADMISSION_SYSTEM_INSTRUCTION
    elif category == "business_opening":
        category_instruction = BUSINESS_OPENING_SYSTEM_INSTRUCTION
    elif category == "first_birthday":
        category_instruction = FIRST_BIRTHDAY_SYSTEM_INSTRUCTION
    elif category == "funeral":
        category_instruction = FUNERAL_SYSTEM_INSTRUCTION
    elif category == "hospital_visit":
        category_instruction = HOSPITAL_VISIT_SYSTEM_INSTRUCTION
    else:
        category_instruction = ""

    if not category_instruction:
        return BASE_SYSTEM_INSTRUCTION
    return f"{BASE_SYSTEM_INSTRUCTION}\n\n{category_instruction}"


def _format_money_calculator_questions(category: OccasionCategory) -> str:
    questions = MONEY_CALCULATOR_QUESTIONS.get(category, ())
    return "\n".join(f"- {question}" for question in questions)


def _format_question_data(question: Any) -> str:
    if isinstance(question, str):
        return pretty_question(question)
    return pretty_json(question)
