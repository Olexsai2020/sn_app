from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import get_user
from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


def get_user_jwt(request):
    user = get_user(request)
    if user.is_authenticated:
        return user
    try:
        user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
        if user_jwt is not None:
            return user_jwt[0]
    except:
        pass
    return user


class UpdateLastActivityMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.user = SimpleLazyObject(lambda: get_user_jwt(request))
        # Check that user is authenticated and isn't AnonymousUser
        if request.user and request.user.id:
            get_user_model().objects.filter(email=request.user.email). \
                             update(last_activity=timezone.now())
