from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import History
from .serializers import HistoryReadSerializer, HistoryWriteSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class HistoryCreateView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = HistoryWriteSerializer(
            data=request.data,
            context={"user": request.user},
        )
        if not serializer.is_valid():
            return Response(
                {"success": False, "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        history = serializer.save()
        return Response({"success": True, "historyId": history.id})


class HistoryListView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        histories = History.objects.filter(user=request.user)
        target_name = request.query_params.get("targetName")
        if target_name:
            histories = histories.filter(target_name=target_name)

        histories = histories.order_by("-date", "-created_at", "-id")
        serializer = HistoryReadSerializer(histories, many=True)
        return Response({"success": True, "histories": serializer.data})


class HistoryDetailView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def get_history(self, request, history_id):
        return History.objects.filter(id=history_id, user=request.user).first()

    def get(self, request, history_id):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        history = self.get_history(request, history_id)
        if not history:
            return Response(
                {"success": False, "detail": "History not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = HistoryReadSerializer(history)
        return Response({"success": True, "history": serializer.data})

    def post(self, request, history_id):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        history = self.get_history(request, history_id)
        if not history:
            return Response(
                {"success": False, "detail": "History not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = HistoryWriteSerializer(instance=history, data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        history = serializer.save()
        read_serializer = HistoryReadSerializer(history)
        return Response({"success": True, "history": read_serializer.data})

    def delete(self, request, history_id):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        history = self.get_history(request, history_id)
        if not history:
            return Response(
                {"success": False, "detail": "History not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        history.delete()
        return Response({"success": True})
