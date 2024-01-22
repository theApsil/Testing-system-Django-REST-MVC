from rest_framework import serializers

from solutions.models import TestSolution
from tests.serializers import TestSerializer


class TestSolutionSerializer(serializers.ModelSerializer):
    test = TestSerializer
    score = serializers.SerializerMethodField()
    max_score = serializers.SerializerMethodField()

    class Meta:
        model = TestSolution
        fields = [
            'test',
            'created',
            'score',
            'max_score',
        ]

    def get_score(self, obj: TestSolution) -> int:
        return getattr(obj, 'score', 0)

    def get_max_score(self, obj: TestSolution) -> int:
        return getattr(obj, 'max_score', 0)


