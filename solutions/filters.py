import django_filters
from django.db.models import Exists, OuterRef
from django_filters import FilterSet

from tests.models import Task


class TestSolutionFilterSet(FilterSet):

    topic_id = django_filters.NumberFilter(method='filter_by_topic')
    created = django_filters.DateTimeFromToRangeFilter()

    def filter_by_topic(self, qs, name, value):
        return qs.filter(Exists(Task.objects.filter(topic_id=value, tests=OuterRef('test'))))
