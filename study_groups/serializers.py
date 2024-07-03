from rest_framework import serializers
from .models import StudyGroup, Test, Question, Answer, UserTestStatus, UserAnswer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'is_staff']


class StudyGroupSerializer(serializers.ModelSerializer):
    teacher = UserSerializer()
    members = UserSerializer(many=True)

    class Meta:
        model = StudyGroup
        fields = ['study_group_id', 'study_group_name', 'study_group_img_link', 'teacher', 'members']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'image', 'answers']


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'title', 'description', 'cover_image', 'questions']


class UserTestStatusSerializer(serializers.ModelSerializer):
    test = TestSerializer()

    class Meta:
        model = UserTestStatus
        fields = ['test', 'is_completed', 'score', 'grade']


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['user', 'question', 'selected_answer']


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'title', 'description', 'cover_image', 'questions']