from django.http import Http404
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from solutions.models import TestSolution
from solutions.serializers import TestSolutionSerializer
from testing.middlewares import KeyCloakAuth
from tests.models import Test
from tests.serializers import TestSerializer, DetailedTestSerializer


class TestViewSet(ReadOnlyModelViewSet):
    authentication_classes = [KeyCloakAuth]
    permission_classes = [IsAuthenticated]

    serializer_classes = {
        'list': TestSerializer,
        'retrieve': DetailedTestSerializer,
    }
    queryset = Test.objects.all()

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, TestSerializer)

    def get_queryset(self):
        if self.action == 'retrieve':
            return super().get_queryset().prefetch_related('tasks__variants', 'tasks__topic')
        return super().get_queryset()

    @action(methods=['post'], detail=True)
    @extend_schema(request=None, responses={201: TestSolutionSerializer})
    def start(self, request, *args, **kwargs):
        test = self.get_object()
        if TestSolution.objects.filter(test=test, user=request.user).exists():
            raise ValidationError('User already solved this test')

        solution = TestSolution.objects.create(test=test, user=request.user)
        serializer = TestSolutionSerializer(instance=solution)

        return Response(status=status.HTTP_201_CREATED, data=serializer.data)
