from django.urls import path
from .views import (UserStudyGroupsView, UserResultsView, ActiveTestsView, TestDetailView, UserAnswerView,
                    CompleteTestView, ProfileView, TeacherGroupsView, TestsView, GroupStudentsView, GroupTestsView,
                    StudentTestResultView, GenerateReportView, CreateQuestionView, AllQuestionsView, CreateTestView)

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
    path('api/all-questions/', AllQuestionsView.as_view(), name='all-questions'),
    path('api/create-test/', CreateTestView.as_view(), name='create-test'),
    path('api/create-question/', CreateQuestionView.as_view(), name='create-question'),
    path('api/generate-report/<int:student_id>/<int:test_id>/', GenerateReportView.as_view(), name='generate-report'),
    path('api/teacher-groups/', TeacherGroupsView.as_view(), name='teacher-groups'),
    path('api/group-students/<int:group_id>/', GroupStudentsView.as_view(), name='group-students'),
    path('api/group-tests/<int:group_id>/', GroupTestsView.as_view(), name='group-tests'),
    path('api/student-test-result/<int:student_id>/<int:test_id>/', StudentTestResultView.as_view(), name='student-test-result'),
]
