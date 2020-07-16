from datetime import datetime, timedelta

from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.decorators import action

from .models import Post, Like
from .serializers import UserSignupSerializer, UserLoginSerializer, \
                         UserActivitySerializer, PostSerializer, \
                         AnalyticsSerializer


class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {'message': 'User signup successfully',
                    'result': 'New user created: ' + request.data['email']}
        return Response(response, status=status.HTTP_200_OK)


class UserLoginView(generics.RetrieveAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {'message': 'User logged in successfully',
                    'result': 'User logged in: ' + request.data['email'],
                    'token': serializer.data['token']}
        return Response(response, status=status.HTTP_200_OK)


class UserActivityView(generics.ListAPIView):
    '''Get info about user's last login and request'''
    serializer_class = UserActivitySerializer
    permission_classes = (IsAuthenticated, )
    authentication_class = JSONWebTokenAuthentication

    def get_queryset(self):
        email = self.request.query_params.get('email')

        queryset = get_user_model().objects.filter(email=email). \
                    values('last_login', 'last_activity')

        return queryset


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, )
    authentication_class = JSONWebTokenAuthentication

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        '''Like post'''
        post = Post.objects.get(id=pk)
        user = request.user

        # Check that post already liked by user
        try:
            Like.objects.get(user=user.id, post=post.id)
            response = {'message': '''You can't like this post twice''',
                        'result': 'No action with post: ' + post.title}
        # Like if post already not liked by user
        except:
            Like.objects.create(user=user, post=post)
            response = {'message': 'You liked this post',
                        'result': 'Liked post: ' + post.title}
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def unlike(self, request, pk=None):
        '''Unlike post'''
        post = Post.objects.get(id=pk)
        user = request.user

        # Try unlike if post already liked by user
        try:
            like = Like.objects.get(user=user.id, post=post.id)
            like.delete()
            response = {'message': 'You unliked this post',
                        'result': 'Unliked post: ' + post.title}
        # Error message if post not liked
        except:
            response = {'message': '''You can't unlike post which you not liked before''',
                        'result': 'No action with post: ' + post.title}
        return Response(response, status=status.HTTP_200_OK)


class AnalyticsView(generics.ListAPIView):
    '''
    Get analytics about likes aggregated by day

    Sample query: /api/analytics/?date_from=2020-02-02&date_to=2020-02-15
    '''
    serializer_class = AnalyticsSerializer
    permission_classes = (IsAuthenticated, )
    authentication_class = JSONWebTokenAuthentication

    def get_queryset(self):
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        day_increment = timedelta(days=1)
        date_to_corrected = (datetime.strptime(date_to, '%Y-%m-%d').date() +
                             day_increment).strftime("%Y-%m-%d")

        queryset = Like.objects.filter(created_at__gte=date_from,
                    created_at__lt=date_to_corrected). \
                    values('created_at__date').order_by('created_at__date'). \
                    annotate(likes=Count('id'))

        return queryset
