import json
import logging

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from form.models import Form
from history.models import History
from utils.gemini import (
    __wrapper_ai_yk_question as ai_yk_question_wrapper,
    __wrapper_mj_etiquette as mj_etiquette_wrapper,
    __wrapper_ai_yk_payment as ai_yk_payment_wrapper,
)

from .models import ChatItem
from .serializers import (
    ChatCreateSerializer,
    ChatItemReadSerializer,
    ChatListQuerySerializer,
)


logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def get_user_language(user):
    profile = getattr(user, "profile", None)
    if profile and profile.language:
        return profile.language
    return "ko"


def format_history_for_gemini(history):
    return {
        "targetName": history.target_name,
        "received": history.received,
        "value": history.value,
        "currency": history.currency,
        "category": history.category,
        "date": history.date.isoformat(),
    }


def build_chat_memory(chat_items):
    chat_items = list(chat_items)
    if not chat_items:
        return ""

    first_chats = chat_items[:3]
    first_chat_memory_parts = []
    for chat_item in first_chats:
        first_chat_memory_parts.extend([chat_item.question, chat_item.answer])
    first_chat_memory = "\n".join(first_chat_memory_parts)
    memory = [
        "사전 질문:",
        first_chat_memory,
    ]

    extra_chats = chat_items[3:]
    if extra_chats:
        memory.extend(["", "추가 질문:"])
        for chat_item in extra_chats:
            memory.append(
                json.dumps(
                    {
                        "question": chat_item.question,
                        "answer": chat_item.answer,
                    },
                    ensure_ascii=False,
                )
            )

    return "\n".join(memory)


def build_current_context(form, category):
    return {
        "category": category,
        "targetName": form.target_name,
        "cultureBase": form.culture_base,
        "answers": form.answers,
    }


class ChatCreateView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = ChatCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        form = Form.objects.filter(
            id=serializer.validated_data["formId"],
            user=request.user,
        ).first()
        if not form:
            return Response(
                {"success": False, "detail": "Form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        chat_item = ChatItem.objects.create(
            form=form,
            question=serializer.validated_data["question"],
        )

        try:
            histories = [
                format_history_for_gemini(history)
                for history in History.objects.filter(
                    user=request.user,
                    target_name=form.target_name,
                ).order_by("date", "created_at", "id")
            ]
            previous_chat_items = form.chat_items.filter(
                status=ChatItem.Status.SUCCESS,
            ).exclude(id=chat_item.id).order_by("created_at", "id")
            category = serializer.validated_data.get("category") or form.category
            
            cnt = ChatItem.objects.filter(
                form=form,
            ).count()

            if chat_item.question == "__CHAT_ITEM__":
                chat_item.question = json.dumps(chat_item.form.answers, ensure_ascii=False)
                chat_item.save(update_fields=["question", "updated_at"])

            memory = build_chat_memory(previous_chat_items)
            if cnt == 0:
                gemini_result = ai_yk_payment_wrapper(
                    get_user_language(request.user),
                    histories,
                    chat_item.question,
                    memory,
                    current_context=build_current_context(form, category),
                    category=category,
                    target_name=form.target_name,
                    culture_base=form.culture_base,
                )

            elif cnt == 1:
                gemini_result = mj_etiquette_wrapper(
                    get_user_language(request.user),
                    histories,
                    chat_item.question,
                    memory,
                    category,
                )
            else:
                gemini_result = ai_yk_question_wrapper(
                    get_user_language(request.user),
                    histories,
                    chat_item.question,
                    memory,
                    current_context=build_current_context(form, category),
                    category=category,
                    target_name=form.target_name,
                    culture_base=form.culture_base,
                )

            success = gemini_result["success"]
            answer = gemini_result["answer"]
        except Exception as exc:
            logger.exception("Failed to get chat answer.")
            return Response(
                {
                    "success": False,
                    "chatItemId": chat_item.id,
                    "status": chat_item.status,
                    "detail": f"Failed to get chat answer: {exc}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not success:
            return Response(
                {
                    "success": False,
                    "chatItemId": chat_item.id,
                    "status": chat_item.status,
                    "detail": answer,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        chat_item.answer = answer
        chat_item.status = ChatItem.Status.SUCCESS
        chat_item.save(update_fields=["answer", "status", "updated_at"])

        return Response(
            {
                "success": True,
                "chatItemId": chat_item.id,
                "status": chat_item.status,
                "answer": chat_item.answer,
            }
        )


class ChatListView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = ChatListQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {"success": False, "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        chat_items = ChatItem.objects.filter(form__user=request.user)
        form_id = serializer.validated_data.get("formId")
        if form_id is not None:
            form = Form.objects.filter(id=form_id, user=request.user).first()
            if not form:
                return Response(
                    {"success": False, "detail": "Form not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            chat_items = chat_items.filter(form=form)

        chat_items = chat_items.order_by("created_at", "id")
        read_serializer = ChatItemReadSerializer(chat_items, many=True)
        return Response({"success": True, "chatItems": read_serializer.data})


class ChatDetailView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def get(self, request, chat_item_id):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        chat_item = ChatItem.objects.select_related("form").filter(
            id=chat_item_id,
            form__user=request.user,
        ).first()
        if not chat_item:
            return Response(
                {"success": False, "detail": "Chat item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ChatItemReadSerializer(chat_item)
        return Response({"success": True, "chatItem": serializer.data})
