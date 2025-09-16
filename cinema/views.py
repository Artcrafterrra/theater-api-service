from rest_framework import viewsets, permissions, decorators, response, status
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from cinema.models import (
    Actor,
    Genre,
    TheatreHall,
    Play,
    Performance,
    Ticket,
    Reservation,
)
from cinema.serializers import (
    ActorSerializer,
    GenreSerializer,
    TheatreHallSerializer,
    PlaySerializer,
    PerformanceSerializer,
    TicketSerializer,
    ReservationCreateSerializer,
    ReservationListSerializer,
    TicketShortSerializer,
)


class StaffWriteReadOnlyElse(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


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


class PlayViewSet(StaffWriteReadOnlyElse):
    queryset = Play.objects.prefetch_related("actors", "genres").all()
    serializer_class = PlaySerializer
    filterset_fields = {
        "genres": ["in"],
        "actors": ["in"],
    }
    search_fields = ["title"]
    ordering_fields = ["title"]


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

    @decorators.action(detail=True, methods=["get"])
    def available_seats(self, request, pk=None):
        perf = self.get_object()
        qs = (
            perf.tickets.filter(reservation__isnull=True)
            .values("row", "seat")
            .order_by("row", "seat")
        )
        return response.Response(list(qs))


class ReservationViewSet(
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user
        ).prefetch_related("tickets")

    def get_serializer_class(self):
        if self.action == "create":
            return ReservationCreateSerializer
        return ReservationListSerializer

    def list(self, request):
        ser = self.get_serializer(self.get_queryset(), many=True)
        return response.Response(ser.data)

    def create(self, request):
        ser = self.get_serializer(
            data=request.data, context={"request": request}
        )
        ser.is_valid(raise_exception=True)
        reservation = ser.save()
        out = ReservationListSerializer(reservation)
        return response.Response(out.data, status=status.HTTP_201_CREATED)
