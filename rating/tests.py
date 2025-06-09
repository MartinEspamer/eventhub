# Test unitario para la función event_rating_avg

import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from app.models import Event
from rating.models import Rating
from rating.templatetags.rating_tags import event_rating_avg


class EventRatingAvgTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='test_user',
            password='12345'
        )

        # Evento de prueba
        self.event = Event.objects.create(
            title='test_event',
            description='test_event_description',
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.user,
        )

    # Reseña de prueba
    def test_no_ratings(self):
        result = event_rating_avg(self.event)
        self.assertIn("Sin reseñas", result)

    # Calificaciones de prueba
    def test_with_ratings(self):
        Rating.objects.create(
            event=self.event,
            user=self.user,
            title = "test_title_1",
            text = "test_text_1",
            rating = 4,
            created_at = timezone.now(),
            )
        Rating.objects.create(
            event=self.event,
            user=self.user,
            title = "test_title_2",
            text = "test_text_2",
            rating = 5,
            created_at = timezone.now(),
        )
        Rating.objects.create(
            event=self.event,
            user=self.user,
            title = "test_title_3",
            text = "test_text_3",
            rating = 5,
            created_at = timezone.now(),
        )

        result = event_rating_avg(self.event)

        self.assertIn("<strong id='avg-value'>4,7</strong>", result) # Al ser 4,666..., el promedio se ve como 4,7
        self.assertIn("<span id='avg-ratings-count'>(3 Reseñas)</span>", result)