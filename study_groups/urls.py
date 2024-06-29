
from django.urls import path
from .views import UserStudyGroupsView

urlpatterns = [
    path('user-groups/', UserStudyGroupsView.as_view(), name='user-groups'),
]
