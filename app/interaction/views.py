from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from interaction.models import (
    Follow, FollowRequest, Block, Mute,
    Notification, NotificationPreference, FeedPreference,
    Badge, UserBadge
)
from interaction.serializers import (
    FollowSerializer, FollowRequestSerializer
)


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.GenericViewSet):
    """ViewSet for user social actions."""
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

    def get_queryset(self):
        return get_user_model().objects.all()

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """Follow or unfollow a user."""
        target_user = get_object_or_404(get_user_model(), pk=pk)

        if target_user == request.user:
            return Response(
                {'error': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if blocked
        if Block.objects.filter(user=target_user, blocked_user=request.user).exists():
            return Response(
                {'error': 'Unable to follow this user.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'DELETE':
            Follow.objects.filter(
                follower=request.user,
                following=target_user
            ).delete()
            FollowRequest.objects.filter(
                requester=request.user,
                target=target_user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # POST - follow
        if Follow.objects.filter(follower=request.user, following=target_user).exists():
            return Response(
                {'error': 'Already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if target_user.is_private:
            follow_request, created = FollowRequest.objects.get_or_create(
                requester=request.user,
                target=target_user,
                defaults={'status': 'pending'}
            )
            serializer = FollowRequestSerializer(follow_request)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        follow = Follow.objects.create(
            follower=request.user,
            following=target_user
        )
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """List user's followers."""
        user = get_object_or_404(get_user_model(), pk=pk)
        follows = Follow.objects.filter(following=user).select_related('follower')
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """List who user follows."""
        user = get_object_or_404(get_user_model(), pk=pk)
        follows = Follow.objects.filter(follower=user).select_related('following')
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated],
            url_path='me/follow-requests', url_name='follow-requests')
    def follow_requests(self, request):
        """List pending follow requests for current user."""
        requests = FollowRequest.objects.filter(
            target=request.user,
            status='pending'
        ).select_related('requester')
        page = self.paginate_queryset(requests)
        serializer = FollowRequestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated],
            url_path='accept', url_name='accept-request')
    def accept_request(self, request, pk=None):
        """Accept a follow request."""
        follow_request = get_object_or_404(
            FollowRequest,
            pk=pk,
            target=request.user,
            status='pending'
        )

        with transaction.atomic():
            follow_request.status = 'approved'
            follow_request.save()
            Follow.objects.get_or_create(
                follower=follow_request.requester,
                following=request.user
            )

        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated],
            url_path='reject', url_name='reject-request')
    def reject_request(self, request, pk=None):
        """Reject a follow request."""
        follow_request = get_object_or_404(
            FollowRequest,
            pk=pk,
            target=request.user,
            status='pending'
        )
        follow_request.status = 'rejected'
        follow_request.save()

        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data)
