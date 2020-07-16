from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from .views import UserSignupView, UserLoginView, \
                   UserActivityView, PostViewSet, AnalyticsView

router = routers.DefaultRouter()
router.register('posts', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('user/signup', UserSignupView.as_view()),
    path('user/login', UserLoginView.as_view()),
    path('user/activity/', UserActivityView.as_view()),
    path('analytics/', AnalyticsView.as_view()),
]
