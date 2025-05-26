# Test unitario para la función event_rating_avg

from django.test import TestCase
from django.contrib.auth import get_user_model
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
            scheduled_at='2025-05-26',
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
            created_at = "2025-05-26 12:00"
            )
        Rating.objects.create(
            event=self.event,
            user=self.user,
            title = "test_title_2",
            text = "test_text_2",
            rating = 5,
            created_at = "2025-05-26 13:00"
        )

        result = event_rating_avg(self.event)

        self.assertIn("4,5", result)
        self.assertIn("(2 Reseñas)", result)