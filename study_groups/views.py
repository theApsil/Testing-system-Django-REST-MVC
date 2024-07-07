import os
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from docx import Document
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Test, Question, Answer, UserAnswer, UserTestStatus, StudyGroup
from .serializers import TestSerializer, UserTestStatusSerializer, UserSerializer, QuestionSerializer
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


class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id, test_id):
        try:
            # Получаем данные теста и ответов
            test_status = UserTestStatus.objects.get(user_id=student_id, test_id=test_id)
            user = test_status.user
            user_answers = UserAnswer.objects.filter(user_id=student_id, question__test_id=test_id)
            errors = [answer for answer in user_answers if not answer.selected_answer.is_correct]

            # Загружаем шаблон
            template_path = os.path.join(settings.BASE_DIR, 'docs', 'anal.docx')
            if not os.path.exists(template_path):
                logger.error(f"Template not found: {template_path}")
                return JsonResponse({"error": "Template not found"}, status=404)

            document = Document(template_path)

            # Функция для замены маркеров в тексте, сохраняя форматирование
            def replace_text_in_paragraph(paragraph, var, value):
                for run in paragraph.runs:
                    if var in run.text:
                        run.text = run.text.replace(var, value)

            # Замена переменных в тексте
            current_date = datetime.now().strftime("%d.%m.%Y")
            variables = {
                'DATE': current_date,
                'Фамилия Имя': f'{user.last_name} {user.first_name}',
                'Балл': str(test_status.score),
                'Оценка': str(test_status.grade),
                'TEST_NAME': test_status.test.title
            }

            for paragraph in document.paragraphs:
                for var, value in variables.items():
                    replace_text_in_paragraph(paragraph, var, value)

            styles = document.styles
            try:
                heading2_style = styles['Heading 2']
            except KeyError:
                heading2_style = styles.add_style('Heading 2', 1)
                heading2_style.font.name = 'Times New Roman'
                heading2_style.font.size = Pt(14)
                heading2_style.font.bold = True

            # Добавляем список ошибок
            document.add_heading('Список ошибок', level=2)
            for error in errors:
                document.add_paragraph(f'Вопрос: {error.question.text}')
                document.add_paragraph(f'Ваш ответ: {error.selected_answer.text}')
                correct_answer = [a.text for a in error.question.answers.all() if a.is_correct]
                document.add_paragraph(f'Правильный ответ: {", ".join(correct_answer)}')
                document.add_paragraph()

            # Сохраняем документ
            report_path = os.path.join(settings.MEDIA_ROOT, f'report_{student_id}_{test_id}.docx')
            document.save(report_path)

            # Отправляем файл пользователю
            with open(report_path, 'rb') as file:
                response = HttpResponse(file.read(),
                                        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename=report_{student_id}_{test_id}.docx'
                return response
        except UserTestStatus.DoesNotExist:
            logger.error(f"Test status not found for user {student_id} and test {test_id}")
            return JsonResponse({"error": "Test status not found"}, status=404)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)


class CreateQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        text = request.data.get('text')
        image = request.FILES.get('image')
        answers_data = json.loads(request.data.get('answers'))

        question = Question.objects.create(text=text, image=image)

        for answer_data in answers_data:
            Answer.objects.create(
                question=question,
                text=answer_data['text'],
                is_correct=answer_data['is_correct']
            )

        return Response({'message': 'Задание успешно создано'}, status=status.HTTP_201_CREATED)


class AllQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class CreateTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        description = request.data.get('description')
        group_id = request.data.get('study_group')
        question_ids = request.data.get('questions', [])

        if not title or not description:
            return Response({'error': 'Title and description are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Создание теста
        test = Test.objects.create(
            title=title,
            description=description,
            cover_image='/static/img/img_4.png',
            study_group_id=group_id
        )

        questions = Question.objects.filter(id__in=question_ids)
        test.questions.set(questions)
        test.save()

        serializer = TestSerializer(test)
        return Response(serializer.data, status=status.HTTP_201_CREATED)