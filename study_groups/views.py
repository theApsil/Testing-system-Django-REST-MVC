from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Test, Question, Answer, UserAnswer, UserTestStatus, StudyGroup
from .serializers import TestSerializer, UserTestStatusSerializer, UserSerializer
from rest_framework import generics
from .serializers import StudyGroupSerializer
from rest_framework.permissions import IsAuthenticated
import logging


logger = logging.getLogger(__name__)


class UserStudyGroupsView(generics.ListAPIView):
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.study_groups.all()


class TestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id)
        serializer = TestSerializer(test)
        return Response(serializer.data)


class UserAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        question = get_object_or_404(Question, id=data['question_id'])
        answer = get_object_or_404(Answer, id=data['answer_id'])
        UserAnswer.objects.update_or_create(user=user, question=question, defaults={'selected_answer': answer})
        return Response({"message": "Answer saved"}, status=status.HTTP_200_OK)


class UserResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        test_statuses = UserTestStatus.objects.filter(user=user, is_completed=True)
        results = []
        for test_status in test_statuses:
            user_answers = UserAnswer.objects.filter(user=user, question__test=test_status.test).values_list(
                'selected_answer_id', flat=True)
            result = {
                'test': TestSerializer(test_status.test).data,
                'score': test_status.score,
                'grade': test_status.grade,
                'user_answers': list(user_answers)
            }
            results.append(result)
        return Response(results)


class ActiveTestsView(generics.ListAPIView):
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all groups user is a member of
        groups = user.study_groups.all()
        # Get all tests that belong to these groups and user has not completed
        return Test.objects.filter(
            study_group__in=groups,
            userteststatus__is_completed=False,
            userteststatus__user=user
        )


class CompleteTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, test_id):
        user = request.user
        test = get_object_or_404(Test, id=test_id)
        user_answers = UserAnswer.objects.filter(user=user, question__test=test)
        correct_answers = 0
        for user_answer in user_answers:
            if user_answer.selected_answer.is_correct:
                correct_answers += 1
        score = correct_answers
        grade = 2
        total_questions = test.questions.count()
        if total_questions > 0:
            percentage = (correct_answers / total_questions) * 100
            if percentage >= 86:
                grade = 5
            elif percentage >= 70:
                grade = 4
            elif percentage >= 50:
                grade = 3

        UserTestStatus.objects.update_or_create(user=user, test=test,
                                                defaults={'is_completed': True, 'score': score, 'grade': grade})
        return Response({"message": "Test completed", "score": score, "grade": grade}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class TestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tests = Test.objects.all()
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data)


class TeacherGroupsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_staff:
            return Response({"error": "User is not a teacher"}, status=403)
        groups = StudyGroup.objects.filter(teacher_id=user.id)
        serializer = StudyGroupSerializer(groups, many=True)
        return Response(serializer.data)


class GroupStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        try:
            group = StudyGroup.objects.get(study_group_id=group_id)
            students = group.members.filter(is_staff=False)
            serializer = UserSerializer(students, many=True)
            group_data = {
                "study_group_name": group.study_group_name,
                "teacher": {
                    "first_name": group.teacher.first_name,
                    "last_name": group.teacher.last_name
                },
                "members": serializer.data
            }
            return Response(group_data)
        except StudyGroup.DoesNotExist:
            return Response({"error": "Group not found"}, status=404)


class GroupTestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        try:
            group = StudyGroup.objects.get(study_group_id=group_id)
            tests = group.tests.all()
            serializer = TestSerializer(tests, many=True)
            return Response(serializer.data)
        except StudyGroup.DoesNotExist:
            return Response({"error": "Group not found"}, status=404)


class StudentTestResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id, test_id):
        try:
            test_status = UserTestStatus.objects.get(user_id=student_id, test_id=test_id)
            if not test_status.is_completed:
                return Response({"completed": False})

            user_answers = UserAnswer.objects.filter(user_id=student_id, question__test_id=test_id)
            questions = []
            for answer in user_answers:
                question_data = {
                    "text": answer.question.text,
                    "answer": answer.selected_answer.text,
                    "is_correct": answer.selected_answer.is_correct,
                }
                questions.append(question_data)

            result_data = {
                "completed": True,
                "score": test_status.score,
                "grade": test_status.grade,
                "questions": questions
            }
            logger.info(f"Result data: {result_data}")  # Debugging line
            return Response(result_data)
        except UserTestStatus.DoesNotExist:
            logger.error(f"Test status not found for user {student_id} and test {test_id}")
            return Response({"error": "Test status not found"}, status=404)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": str(e)}, status=500)