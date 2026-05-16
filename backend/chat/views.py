import json

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from form.models import Form
from history.models import History
from utils.gemini import get_gemini_answer

from .models import ChatItem
from .serializers import (
    ChatCreateSerializer,
    ChatItemReadSerializer,
    ChatListQuerySerializer,
)


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
        "cultureBase": history.culture_base,
        "category": history.category,
        "date": history.date.isoformat(),
    }


def build_chat_memory(chat_items):
    chat_items = list(chat_items)
    if not chat_items:
        return ""

    first_chat = chat_items[0]
    memory = [
        "사전 질문:",
        first_chat.question,
        first_chat.answer,
    ]

    extra_chats = chat_items[1:]
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
            success, answer = get_gemini_answer(
                get_user_language(request.user),
                histories,
                chat_item.question,
                build_chat_memory(previous_chat_items),
            )
        except Exception:
            return Response(
                {
                    "success": False,
                    "chatItemId": chat_item.id,
                    "status": chat_item.status,
                    "detail": "Failed to get chat answer.",
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

        form = Form.objects.filter(
            id=serializer.validated_data["formId"],
            user=request.user,
        ).first()
        if not form:
            return Response(
                {"success": False, "detail": "Form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        chat_items = form.chat_items.order_by("created_at", "id")
        read_serializer = ChatItemReadSerializer(chat_items, many=True)
        return Response({"success": True, "chatItems": read_serializer.data})
