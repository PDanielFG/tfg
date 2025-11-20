from rest_framework.routers import DefaultRouter
from .api import MysqlLogLineViewSet

router = DefaultRouter()
router.register("", MysqlLogLineViewSet, basename="logs")

urlpatterns = router.urls
