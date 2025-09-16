from django.db.models.signals import post_save
from django.dispatch import receiver
from cinema.models import Performance, Ticket


@receiver(post_save, sender=Performance)
def create_tickets_for_performance(
    sender, instance: Performance, created, **kwargs
):
    if not created:
        return
    hall = instance.theatre_hall
    rows = hall.rows
    seats = hall.seats_in_row

    bulk = [
        Ticket(performance=instance, row=r, seat=s)
        for r in range(1, rows + 1)
        for s in range(1, seats + 1)
    ]
    Ticket.objects.bulk_create(bulk, ignore_conflicts=True)
