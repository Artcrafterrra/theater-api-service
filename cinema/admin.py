from django.contrib import admin

from cinema.models import Actor, Genre, TheatreHall, Play, Performance, Ticket, Reservation


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name")
    search_fields = ("first_name", "last_name")


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(TheatreHall)
class TheatreHallAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rows", "seats_in_row", "capacity")


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    filter_horizontal = ("actors", "genres")


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("id", "play", "theatre_hall", "show_time")
    list_filter = ("theatre_hall", "play")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "performance", "row", "seat", "reservation")
    list_filter = ("performance", "reservation")
    search_fields = ("performance__play__title",)

