from rest_framework import generics
from .models import StudyGroup
from .serializers import StudyGroupSerializer
from rest_framework.permissions import IsAuthenticated


class UserStudyGroupsView(generics.ListAPIView):
    serializer_class = StudyGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.study_groups.all()
