from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Form
from .serializers import FormCreateSerializer, FormReadSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class FormCreateView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = FormCreateSerializer(
            data=request.data,
            context={"user": request.user},
        )
        if not serializer.is_valid():
            return Response(
                {"success": False, "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        form = serializer.save()
        return Response({"success": True, "formId": form.id})


class FormListView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        forms = Form.objects.filter(user=request.user).order_by("-created_at")
        serializer = FormReadSerializer(forms, many=True)
        return Response({"success": True, "forms": serializer.data})


class FormDetailView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = []

    def get(self, request, form_id):
        if not request.user.is_authenticated:
            return Response(
                {"success": False, "detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        form = Form.objects.filter(id=form_id, user=request.user).first()
        if not form:
            return Response(
                {"success": False, "detail": "Form not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FormReadSerializer(form)
        return Response({"success": True, "form": serializer.data})
