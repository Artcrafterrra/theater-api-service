from django.test import TestCase
from django.utils import timezone
from cinema.models import TheatreHall, Play, Performance, Ticket

import cinema.signals  # noqa: F401


class TestPerformanceSignals(TestCase):
    def test_tickets_created_on_performance_create(self):
        hall = TheatreHall.objects.create(name="Main", rows=3, seats_in_row=4)
        play = Play.objects.create(title="Hamlet")
        perf = Performance.objects.create(
            play=play, theatre_hall=hall, show_time=timezone.now()
        )

        self.assertIsNotNone(perf.id)
        self.assertEqual(Ticket.objects.filter(performance=perf).count(), 12)

        self.assertTrue(
            Ticket.objects.filter(performance=perf, row=1, seat=1).exists()
        )
        self.assertTrue(
            Ticket.objects.filter(performance=perf, row=3, seat=4).exists()
        )
