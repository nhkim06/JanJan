from __future__ import annotations

try:
    from .message_service import message_writing_guide
    from .type_def import AIResponse, History
except ImportError:  # pragma: no cover - supports direct script execution
    from message_service import message_writing_guide
    from type_def import AIResponse, History


def message_guide(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
    category: str = "",
) -> AIResponse:
    return message_writing_guide(language, histories, question, memory, category)


if __name__ == "__main__":
    import json

    # 시스템이 허용하는 카테고리만 사용해야 합니다 (birth, wedding, employment 등)
    scenarios = [
        {
            "name": "친한 친구의 결혼 (편한 사이)",
            "category": "wedding",
            # 'birthday'를 'wedding'이나 다른 허용된 카테고리로 변경
            "history": [{"targetName": "절친", "received": True, "value": 100000, "currency": "ko", "category": "wedding", "date": "2025-01-01"}],
            "survey": [
                {"question": "상대와의 관계", "answer": "매우 가까운 친구"},
                {"question": "참석 여부", "answer": "참석함"}
            ]
        },
        {
            "name": "직장 상사의 자녀 돌잔치 (격식 필요)",
            "category": "first_birthday",
            # 'none' 대신 유효한 카테고리 입력
            "history": [{"targetName": "팀장님", "received": False, "value": 0, "currency": "ko", "category": "first_birthday", "date": "2024-05-01"}],
            "survey": [
                {"question": "상대와의 관계", "answer": "상사/선배"},
                {"question": "참석 여부", "answer": "불참함 (메시지만 전달)"}
            ]
        }
    ]

    print(f"{'='*20} 메시지 톤 테스트 시작 {'='*20}\n")

    for sc in scenarios:
        print(f"▶ 시나리오: {sc['name']}")
        survey_json = json.dumps(sc['survey'], ensure_ascii=False)
        
        # etiquette_api.py 내부의 func 또는 analyze_etiquette를 호출하세요.
        result = message_guide("ko", sc['history'], survey_json, "", sc['category'])
        
        if result["success"]:
            print(f"추천 메시지: {result['answer']}")
        else:
            print(f"오류 발생: {result['answer']}")
        print("-" * 50)