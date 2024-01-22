from rest_framework import serializers

from tests.models import Test, Task, Topic, AnswerVariant


class TestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = [
            'id',
            'name',
        ]

class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = [
            'id',
            'name',
        ]


class VariantSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerVariant
        fields = [
            'text'
        ]


class TaskSerializer(serializers.ModelSerializer):

    topic = TopicSerializer
    variants = VariantSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'text',
            'topic',
            'variants',
        ]


class DetailedTestSerializer(serializers.ModelSerializer):

    tasks = TaskSerializer(many=True)

    class Meta:
        model = Test
        fields = [
            'id',
            'name',
            'tasks',
        ]
