from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    extend_schema_view,
)
from rest_framework import viewsets, permissions, response

from cinema.models import (
    Actor,
    Genre,
    TheatreHall,
    Play,
    Performance,
    Reservation,
)
from cinema.serializers import (
    ActorSerializer,
    GenreSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PerformanceSerializer,
    ReservationCreateSerializer,
    ReservationListSerializer,
    PerformanceReadSerializer,
    PlayReadSerializer,
)
from cinema.pagination import DefaultPagination


class StaffWriteReadOnlyElse(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    pagination_class = DefaultPagination


class ActorViewSet(StaffWriteReadOnlyElse):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    search_fields = ["first_name", "last_name"]


class GenreViewSet(StaffWriteReadOnlyElse):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fields = ["name"]


class TheatreHallViewSet(StaffWriteReadOnlyElse):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    search_fields = ["name"]


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="genres__in",
                description="Separated list of genre IDs.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="actors__in",
                description="Separated list of actor IDs.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="search",
                description="Search for mane or surname.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="ordering",
                description="Sorting: `title` or `-title`.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        tags=["Plays"],
    ),
    retrieve=extend_schema(tags=["Plays"]),
    create=extend_schema(tags=["Plays"]),
    update=extend_schema(tags=["Plays"]),
    partial_update=extend_schema(tags=["Plays"]),
    destroy=extend_schema(tags=["Plays"]),
)
class PlayViewSet(StaffWriteReadOnlyElse):
    queryset = Play.objects.prefetch_related("actors", "genres").all()
    serializer_class = PlaySerializer
    filterset_fields = {
        "genres": ["in"],
        "actors": ["in"],
    }
    search_fields = ["title"]
    ordering_fields = ["title"]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return PlayReadSerializer
        return PlaySerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name="play",
                description="ID paste",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="show_time__date",
                description="Date seance `YYYY-MM-DD`",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="show_time__gte",
                description="Starts from date/time",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="show_time__lte",
                description="To date/time",
                type=OpenApiTypes.DATETIME,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="ordering",
                description="Sorting: `show_time` or `-show_time`",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        tags=["Performances"],
    ),
    retrieve=extend_schema(tags=["Performances"]),
    create=extend_schema(tags=["Performances"]),
    update=extend_schema(tags=["Performances"]),
    partial_update=extend_schema(tags=["Performances"]),
    destroy=extend_schema(tags=["Performances"]),
)
class PerformanceViewSet(StaffWriteReadOnlyElse):
    queryset = Performance.objects.select_related(
        "play", "theatre_hall"
    ).all()
    serializer_class = PerformanceSerializer
    filterset_fields = {
        "play": ["exact"],
        "show_time": ["date", "gte", "lte"],
    }
    ordering_fields = ["show_time"]

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return PerformanceReadSerializer
        return PerformanceSerializer


@extend_schema_view(
    list=extend_schema(
        description="My booking (only for authenticated users).",
        responses=ReservationListSerializer(many=True),
        tags=["Reservations"],
    ),
    create=extend_schema(
        description=(
            "Create booking places.\n\n"
            "**Attention:** in the `seats` field, provide a list of `row/seat` pairs. "
            "The transaction ensures that occupied seats will not be booked twice."
        ),
        request=ReservationCreateSerializer,
        responses=ReservationListSerializer,
        tags=["Reservations"],
        examples=[],
    ),
)
class ReservationViewSet(
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user
        ).prefetch_related("tickets")

    def get_serializer_class(self):
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationListSerializer

    def list(self, request):
        qs = self.get_queryset()
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return response.Response(ser.data)
