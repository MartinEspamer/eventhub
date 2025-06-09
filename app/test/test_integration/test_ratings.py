# Test de integracion para muestreo de calificaciones promedio en la página de detalle del evento

import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from app.models import Event, User
from rating.models import Rating


class TestEventRatingsIntegration(TestCase):
    def setUp(self):
        # Crear un usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@test.com",
            password="password123",
            is_organizer=True,
        )

        # Crear evento de prueba
        self.event1 = Event.objects.create(
            title="Evento 1",
            description="Descripción del evento 1",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )

    def test_event_detail_avg_rating_with_ratings(self):
            # Crear ratings de prueba
            Rating.objects.create(
                event=self.event1,
                user=self.organizer,
                title = "test_title_1",
                text = "test_text_1",
                rating = 2,
                created_at = timezone.now(),
                )
            Rating.objects.create(
                event=self.event1,
                user=self.organizer,
                title = "test_title_2",
                text = "test_text_2",
                rating = 3,
                created_at = timezone.now(),
            )

            # Login con usuario organizador
            self.client.login(username="organizador", password="password123")
            response = self.client.get(reverse("event_detail", args=[self.event1.pk]))

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "<strong id='avg-value'>")
            self.assertContains(response, "2,5") # Se mostrara con punto (".") o con coma (",") dependiendo del idioma definido en eventhub/settings.py
            self.assertContains(response, "</strong>")

            self.assertContains(response, "<span id='avg-ratings-count'>")
            self.assertContains(response, "(2 Reseñas)")
            self.assertContains(response, "</span>")

            self.assertContains(response, "<i id='avg-star' class='bi bi-star-fill text-warning'></i>") # Icono de estrella

    def test_event_detail_avg_rating_with_no_ratings(self):
        # Login con usuario organizador
        self.client.login(username="organizador", password="password123")
        response = self.client.get(reverse("event_detail", args=[self.event1.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sin reseñas")