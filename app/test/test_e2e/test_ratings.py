# Test e2e para muestreo de calificaciones promedio en la página de detalle del evento

import datetime

from django.utils import timezone
from playwright.sync_api import expect

from app.models import Event, User
from app.test.test_e2e.base import BaseE2ETest
from rating.models import Rating


class TestEventRatingsE2E(BaseE2ETest):
    def setUp(self):
        super().setUp()


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
            scheduled_at = timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )

        Rating.objects.create(
                event=self.event1,
                user=self.organizer,
                title = "test_title_1",
                text = "test_text_1",
                rating = 1,
                created_at = timezone.now(),
                )
        Rating.objects.create(
                event=self.event1,
                user=self.organizer,
                title = "test_title_2",
                text = "test_text_2",
                rating = 5,
                created_at = timezone.now(),
            )
    
    def test_organizer_sees_event_rating_avg(self):
        # Login con usuario organizador
        self.login_user("organizador", "password123")

        # Navegar a la página del detalle del evento
        self.page.goto(f"{self.live_server_url}/events/{self.event1.pk}/")

        # Verificar que la calificación promedio se muestra correctamente
        expect(self.page.locator("#avg-value")).to_contain_text("3,0") # Se mostrara con punto (".") o con coma (",") dependiendo del idioma definido en eventhub/settings.py
        expect(self.page.locator("#avg-star")).to_be_visible()
        expect(self.page.locator("#avg-ratings-count")).to_contain_text("(2 Reseñas)")