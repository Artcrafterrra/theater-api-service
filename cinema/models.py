from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Actor(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)

    class Meta:
        unique_together = ("first_name", "last_name")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TheatreHall(models.Model):
    name = models.CharField(max_length=128, unique=True)
    rows = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.rows}x{self.seats_in_row})"

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row


class Play(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    actors = models.ManyToManyField(Actor, related_name="plays", blank=True)
    genres = models.ManyToManyField(Genre, related_name="plays", blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Performance(models.Model):
    play = models.ForeignKey(
        Play, on_delete=models.CASCADE, related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        TheatreHall, on_delete=models.PROTECT, related_name="performances"
    )
    show_time = models.DateTimeField()

    class Meta:
        ordering = ["show_time"]
        unique_together = ("theatre_hall", "show_time")

    def __str__(self) -> str:
        return f"{self.play} @ {self.theatre_hall} on {self.show_time:%Y-%m-%d %H:%M}"


class Reservation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Reservation #{self.id} by {self.user}"


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        related_name="tickets",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ("performance", "row", "seat")
        indexes = [
            models.Index(fields=["performance", "reservation"]),
            models.Index(fields=["performance", "row", "seat"]),
        ]
        ordering = ["row", "seat"]

    def __str__(self) -> str:
        status = (
            "free"
            if self.reservation_id is None
            else f"res:{self.reservation_id}"
        )
        return f"T({self.performance_id}) r{self.row}s{self.seat} [{status}]"

    @property
    def is_free(self) -> bool:
        return self.reservation_id is None
