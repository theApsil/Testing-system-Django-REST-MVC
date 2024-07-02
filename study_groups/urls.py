from django.urls import path
from .views import UserStudyGroupsView, UserResultsView, ActiveTestsView, TestDetailView, UserAnswerView, CompleteTestView

urlpatterns = [
    path('user-groups/', UserStudyGroupsView.as_view(), name='user-groups'),
    path('active-tests/', ActiveTestsView.as_view(), name='active-tests'),
    path('test/<int:test_id>/', TestDetailView.as_view(), name='test-detail'),
    path('submit-answer/', UserAnswerView.as_view(), name='submit-answer'),
    path('complete-test/<int:test_id>/', CompleteTestView.as_view(), name='complete-test'),
    path('results/', UserResultsView.as_view(), name='user-results'),
]
