from django.db.models import Count, Q, OuterRef
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from solutions.filters import TestSolutionFilterSet
from solutions.models import TestSolution, TaskSolution
from solutions.serializers import TestSolutionSerializer
from testing.middlewares import KeyCloakAuth
from testing.subqueries import SubqueryCount
from tests.models import Task, AnswerVariant


class StudentSolutionViewSet(ReadOnlyModelViewSet):
    serializer_class = TestSolutionSerializer
    authentication_classes = [KeyCloakAuth]
    permission_classes = [IsAuthenticated]
    filterset_class = TestSolutionFilterSet

    queryset = TestSolution.objects.annotate(
        score=SubqueryCount(
            TaskSolution.objects.filter(solution_id=OuterRef("id"), chosen_variant__is_correct=True)
        ),
        max_score=Count('test__tasks')
    ).select_related('test')

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class StudentSolveTaskView(GenericAPIView):
    serializer_class = TestSolutionSerializer
    authentication_classes = [KeyCloakAuth]
    permission_classes = [IsAuthenticated]

    @property
    def solution(self):
        return get_object_or_404(TestSolution.objects.filter(user=self.request.user),
                                 pk=self.request.POST.get('solution_id'))

    @property
    def variant(self):
        return get_object_or_404(AnswerVariant, pk=self.request.POST.get('variant_id'))

    @extend_schema(
        responses={200: TestSolutionSerializer}
    )
    def post(self, request, *args, **kwargs):
        if self.variant.task not in self.solution.test.tasks.all():
            raise ValidationError("Task not in test")
        if TaskSolution.objects.filter(solution=self.solution, chosen_variant__task=self.variant.task).exists():
            raise ValidationError("You have already solved this task")

        TaskSolution.objects.create(solution=self.solution, chosen_variant=self.variant)
        serializer = TestSolutionSerializer(instance=self.solution)

        return Response(serializer.data, status=status.HTTP_200_OK)