from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from interaction.models import (
    Follow,
    FollowRequest,
    Block,
    Mute,
    Notification,
)
from interaction.serializers import (
    FollowSerializer,
    FollowRequestSerializer,
    BlockSerializer,
    MuteSerializer,
    NotificationSerializer,
    FeedItemSerializer,
    UserSummarySerializer,
)
from interaction.services.feed import FeedService


class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class UserViewSet(viewsets.GenericViewSet):
    """ViewSet for user social actions."""

    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardPagination

    def get_queryset(self):
        return get_user_model().objects.all()

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def follow(self, request, pk=None):
        """Follow or unfollow a user."""
        target_user = get_object_or_404(get_user_model(), pk=pk)

        if target_user == request.user:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if blocked
        blocked = Block.objects.filter(
            user=target_user, blocked_user=request.user
        ).exists()
        if blocked:
            return Response(
                {"error": "Unable to follow this user."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "DELETE":
            Follow.objects.filter(follower=request.user, following=target_user).delete()
            FollowRequest.objects.filter(
                requester=request.user, target=target_user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # POST - follow
        already_following = Follow.objects.filter(
            follower=request.user, following=target_user
        ).exists()
        if already_following:
            return Response(
                {"error": "Already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if target_user.is_private:
            follow_request, created = FollowRequest.objects.get_or_create(
                requester=request.user,
                target=target_user,
                defaults={"status": "pending"},
            )
            serializer = FollowRequestSerializer(follow_request)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        follow = Follow.objects.create(follower=request.user, following=target_user)
        serializer = FollowSerializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        """List user's followers."""
        user = get_object_or_404(get_user_model(), pk=pk)
        follows = Follow.objects.filter(following=user).select_related("follower")
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        """List who user follows."""
        user = get_object_or_404(get_user_model(), pk=pk)
        follows = Follow.objects.filter(follower=user).select_related("following")
        page = self.paginate_queryset(follows)
        serializer = FollowSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/follow-requests",
        url_name="follow-requests",
    )
    def follow_requests(self, request):
        """List pending follow requests for current user."""
        requests = FollowRequest.objects.filter(
            target=request.user, status="pending"
        ).select_related("requester")
        page = self.paginate_queryset(requests)
        serializer = FollowRequestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="accept",
        url_name="accept-request",
    )
    def accept_request(self, request, pk=None):
        """Accept a follow request."""
        follow_request = get_object_or_404(
            FollowRequest, pk=pk, target=request.user, status="pending"
        )

        with transaction.atomic():
            follow_request.status = "approved"
            follow_request.save()
            Follow.objects.get_or_create(
                follower=follow_request.requester, following=request.user
            )

        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="reject",
        url_name="reject-request",
    )
    def reject_request(self, request, pk=None):
        """Reject a follow request."""
        follow_request = get_object_or_404(
            FollowRequest, pk=pk, target=request.user, status="pending"
        )
        follow_request.status = "rejected"
        follow_request.save()

        serializer = FollowRequestSerializer(follow_request)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def block(self, request, pk=None):
        """Block or unblock a user."""
        target_user = get_object_or_404(get_user_model(), pk=pk)

        if target_user == request.user:
            return Response(
                {"error": "You cannot block yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "DELETE":
            Block.objects.filter(user=request.user, blocked_user=target_user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # POST - block
        with transaction.atomic():
            block, created = Block.objects.get_or_create(
                user=request.user, blocked_user=target_user
            )
            # Remove follows in both directions
            Follow.objects.filter(follower=request.user, following=target_user).delete()
            Follow.objects.filter(follower=target_user, following=request.user).delete()
            FollowRequest.objects.filter(
                requester=request.user, target=target_user
            ).delete()
            FollowRequest.objects.filter(
                requester=target_user, target=request.user
            ).delete()

        serializer = BlockSerializer(block)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def mute(self, request, pk=None):
        """Mute or unmute a user."""
        target_user = get_object_or_404(get_user_model(), pk=pk)

        if target_user == request.user:
            return Response(
                {"error": "You cannot mute yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.method == "DELETE":
            Mute.objects.filter(user=request.user, muted_user=target_user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        mute, created = Mute.objects.get_or_create(
            user=request.user, muted_user=target_user
        )

        serializer = MuteSerializer(mute)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/blocked",
        url_name="blocked-list",
    )
    def blocked_list(self, request):
        """List blocked users."""
        blocks = Block.objects.filter(user=request.user).select_related("blocked_user")
        page = self.paginate_queryset(blocks)
        serializer = BlockSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="me/muted",
        url_name="muted-list",
    )
    def muted_list(self, request):
        """List muted users."""
        mutes = Mute.objects.filter(user=request.user).select_related("muted_user")
        page = self.paginate_queryset(mutes)
        serializer = MuteSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def search(self, request):
        """Search users by name or email."""
        query = request.query_params.get("q", "")
        if len(query) < 2:
            return Response({"results": []})

        # Get users who blocked the requesting user or were blocked by them
        blocked_user_ids = Block.objects.filter(
            Q(user=request.user) | Q(blocked_user=request.user)
        ).values_list("user_id", "blocked_user_id")
        excluded_ids = set()
        for blocker_id, blocked_id in blocked_user_ids:
            excluded_ids.add(blocker_id)
            excluded_ids.add(blocked_id)
        # Don't exclude self from excluded set
        excluded_ids.discard(request.user.pk)
        # But do exclude self from results
        excluded_ids.add(request.user.pk)

        users = (
            get_user_model()
            .objects.filter(Q(name__icontains=query) | Q(email__icontains=query))
            .exclude(pk__in=excluded_ids)[:20]
        )

        serializer = UserSummarySerializer(users, many=True)
        return Response({"results": serializer.data})

    @action(detail=False, methods=["get"])
    def popular(self, request):
        """Get popular users by follower count."""
        queryset = get_user_model().objects.all()

        # If authenticated, exclude blocked users (both directions)
        if request.user.is_authenticated:
            blocked_user_ids = Block.objects.filter(
                Q(user=request.user) | Q(blocked_user=request.user)
            ).values_list("user_id", "blocked_user_id")
            excluded_ids = set()
            for blocker_id, blocked_id in blocked_user_ids:
                excluded_ids.add(blocker_id)
                excluded_ids.add(blocked_id)
            excluded_ids.discard(request.user.pk)
            queryset = queryset.exclude(pk__in=excluded_ids)

        users = queryset.annotate(follower_count=Count("followers_set")).order_by(
            "-follower_count"
        )[:20]

        page = self.paginate_queryset(users)
        serializer = UserSummarySerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def suggested(self, request):
        """Get suggested users based on who you follow."""
        # Get users followed by people you follow
        following_ids = Follow.objects.filter(follower=request.user).values_list(
            "following_id", flat=True
        )

        # Get blocked user IDs (both directions)
        blocked_user_ids = Block.objects.filter(
            Q(user=request.user) | Q(blocked_user=request.user)
        ).values_list("user_id", "blocked_user_id")
        excluded_ids = set()
        for blocker_id, blocked_id in blocked_user_ids:
            excluded_ids.add(blocker_id)
            excluded_ids.add(blocked_id)
        excluded_ids.discard(request.user.pk)

        suggested_ids = (
            Follow.objects.filter(follower_id__in=following_ids)
            .exclude(following=request.user)
            .exclude(following_id__in=following_ids)
            .exclude(following_id__in=excluded_ids)
            .values_list("following_id", flat=True)
            .distinct()[:20]
        )

        users = get_user_model().objects.filter(pk__in=suggested_ids)
        serializer = UserSummarySerializer(users, many=True)
        return Response({"results": serializer.data})


class NotificationViewSet(viewsets.GenericViewSet):
    """ViewSet for notifications."""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def list(self, request):
        """List notifications."""
        queryset = self.get_queryset().select_related("actor")
        page = self.paginate_queryset(queryset)
        serializer = NotificationSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["post"], url_path="read", url_name="mark-read")
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = get_object_or_404(self.get_queryset(), pk=pk)
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="read",
        url_name="mark-all-read",
    )
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().update(is_read=True)
        return Response({"status": "all notifications marked as read"})

    @action(
        detail=False,
        methods=["get"],
        url_path="unread-count",
        url_name="unread-count",
    )
    def unread_count(self, request):
        """Get unread notification count."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})


class FeedViewSet(viewsets.GenericViewSet):
    """ViewSet for activity feed."""

    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def list(self, request):
        """Get activity feed."""
        order = request.query_params.get("order", "chronological")
        feed_items = FeedService.get_feed(request.user, order=order)

        # Manual pagination
        page = self.paginate_queryset(feed_items)
        serializer = FeedItemSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
