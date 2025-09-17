from typing import List, Tuple
from django.db import transaction
from rest_framework import serializers
from cinema.models import (
    Actor,
    Genre,
    TheatreHall,
    Play,
    Performance,
    Ticket,
    Reservation,
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class TheatreHallSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class PlaySerializer(serializers.ModelSerializer):
    actors = serializers.PrimaryKeyRelatedField(
        queryset=Actor.objects.all(), many=True, required=False
    )
    genres = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), many=True, required=False
    )

    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres")


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class PlayReadSerializer(serializers.ModelSerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ("id", "title", "description", "actors", "genres")


class PerformanceReadSerializer(serializers.ModelSerializer):
    play = PlayReadSerializer(read_only=True)
    theatre_hall = TheatreHallSerializer(read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "play", "theatre_hall", "show_time")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance", "reservation")
        read_only_fields = ("reservation",)


class SeatSerializer(serializers.Serializer):
    row = serializers.IntegerField(min_value=1)
    seat = serializers.IntegerField(min_value=1)


class ReservationCreateSerializer(serializers.Serializer):
    performance = serializers.PrimaryKeyRelatedField(
        queryset=Performance.objects.all()
    )
    seats = SeatSerializer(many=True)

    def validate(self, attrs):
        performance: Performance = attrs["performance"]
        hall = performance.theatre_hall
        pairs: List[Tuple[int, int]] = [
            (it["row"], it["seat"]) for it in attrs["seats"]
        ]

        if len(pairs) != len(set(pairs)):
            raise serializers.ValidationError("Duplicate seats in request.")

        for r, s in pairs:
            if not (1 <= r <= hall.rows) or not (1 <= s <= hall.seats_in_row):
                raise serializers.ValidationError(
                    f"Seat r{r}/s{s} out of hall bounds ({hall.rows}x{hall.seats_in_row})."
                )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        performance: Performance = validated_data["performance"]
        pairs: List[Tuple[int, int]] = [
            (it["row"], it["seat"]) for it in validated_data["seats"]
        ]

        with transaction.atomic():
            reservation = Reservation.objects.create(user=user)
            to_update: list[Ticket] = []
            for r, s in pairs:
                t = Ticket.objects.select_for_update().get(
                    performance=performance, row=r, seat=s
                )
                if t.reservation_id is not None:
                    raise serializers.ValidationError(
                        f"Seat r{r}/s{s} is already reserved."
                    )
                t.reservation = reservation
                to_update.append(t)

            Ticket.objects.bulk_update(to_update, ["reservation"])
            return reservation


class TicketShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat")


class ReservationListSerializer(serializers.ModelSerializer):
    tickets = TicketShortSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")
