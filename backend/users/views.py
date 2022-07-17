from django.contrib.auth import get_user_model
from djoser.views import UserViewSet, User
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Follow
from .serializers import (CurrentUserSubscriptionsSerizlizer,
                          ManageSubscribeSerizlizer, UserSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny, ]


class ManageSubscribeView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        follower = request.user

        if author == follower:
            return Response(
                {'error': 'Нельзя подписываться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)

        if Follow.objects.filter(user=follower, author=author).exists():
            return Response(
                {'error': 'Вы уже подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(user=follower, author=author)
        serializer = ManageSubscribeSerizlizer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        follower = request.user

        follow = Follow.objects.filter(user=follower, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Подписка не найдена'},
            status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        profile = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(profile, context={'request': request})
        return Response(serializer.data)


class CurrentUserSubscriptionsView(ListAPIView):
    permission_classes = [IsAuthenticated, ]
    pagination_class = PageNumberPagination
    serializer_class = CurrentUserSubscriptionsSerizlizer
    allowed_methods = ['GET', ]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)
