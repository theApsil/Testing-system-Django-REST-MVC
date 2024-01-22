from rest_framework.routers import SimpleRouter

from tests.views import TestViewSet

router = SimpleRouter()

router.register('tests', TestViewSet)

urlpatterns = router.urls
