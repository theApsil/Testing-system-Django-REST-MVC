from django.urls import path
from rest_framework.routers import SimpleRouter

from solutions.views import StudentSolutionViewSet, StudentSolveTaskView

router = SimpleRouter()
router.register('solutions', StudentSolutionViewSet)

additional_url_patterns = [
    path('solutions/<int:solution_id>/variants/<int:variant_id>',
         StudentSolveTaskView.as_view())
]
urlpatterns = router.urls + additional_url_patterns
