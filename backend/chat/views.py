from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from form.models import Form
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
            answer = get_gemini_answer(chat_item.question)
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

        chat_items = form.chat_items.order_by("created_at")
        read_serializer = ChatItemReadSerializer(chat_items, many=True)
        return Response({"success": True, "chatItems": read_serializer.data})
