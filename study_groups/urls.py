from django.urls import path
from .views import (UserStudyGroupsView, UserResultsView, ActiveTestsView, TestDetailView, UserAnswerView,
                    CompleteTestView, ProfileView, TeacherGroupsView, TestsView, GroupStudentsView)

urlpatterns = [
    path('user-groups/', UserStudyGroupsView.as_view(), name='user-groups'),
    path('active-tests/', ActiveTestsView.as_view(), name='active-tests'),
    path('test/<int:test_id>/', TestDetailView.as_view(), name='test-detail'),
    path('submit-answer/', UserAnswerView.as_view(), name='submit-answer'),
    path('complete-test/<int:test_id>/', CompleteTestView.as_view(), name='complete-test'),
    path('results/', UserResultsView.as_view(), name='user-results'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/teacher-groups/', TeacherGroupsView.as_view(), name='teacher-groups'),
    path('api/tests/', TestsView.as_view(), name='tests'),
    path('api/group-students/<int:group_id>/', GroupStudentsView.as_view(), name='group-students'),
]
