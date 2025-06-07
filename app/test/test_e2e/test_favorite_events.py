import datetime
import re

from django.utils import timezone
from playwright.sync_api import expect

from app.models import Event, User
from app.test.test_e2e.base import BaseE2ETest


class FavoriteEventsE2ETest(BaseE2ETest):
    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(
            username="username",
            password="password",
            email="username@example.com",
            is_organizer=False,
        )

        self.event = Event.objects.create(
            title="Evento Favorito",
            description="Test de favoritos",
            scheduled_at=timezone.localtime() + datetime.timedelta(days=5),
            organizer=self.user
        )

    def test_mark_and_unmark_favorite(self):
        self.login_user("username", "password")
        self.page.goto(f"{self.live_server_url}/events/")

        row = self.page.locator("table tbody tr", has_text="Evento Favorito")
        favorite_btn = row.locator("a.favorite-btn")

        # Verificamos que tiene el icono vacio
        expect(favorite_btn.locator("i")).to_have_class(re.compile("bi-heart$"))
        favorite_btn.click()

        self.page.locator("input#favorites_only").check()

        # Verificamos que aparece solo el evento marcado
        rows = self.page.locator("table tbody tr")
        expect(rows).to_have_count(1)
        expect(rows.nth(0)).to_contain_text("Evento Favorito")

        favorite_btn = self.page.locator("table tbody tr a.favorite-btn")
        favorite_btn.click()

        self.page.locator("input#favorites_only").check()

        rows = self.page.locator("table tbody tr")
        expect(rows).to_have_count(1)
        expect(rows.nth(0)).to_contain_text("No hay eventos disponibles")
