from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now, timedelta

from app.models import Event, Favorite, User


class FavoriteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='password')
        self.event = Event.objects.create(
            title='Evento de prueba',
            description='Descripción del evento de prueba',
            scheduled_at=now() + timedelta(days=2),
            organizer=self.user
        )

    def test_toggle_favorite_add(self):
        self.client.login(username='user', password='password')
        url = reverse('toggle_favorite', args=[self.event.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=self.user, event=self.event).exists())

    def test_toggle_favorite_remove(self):
        self.client.login(username='user', password='password')
        Favorite.objects.create(user=self.user, event=self.event)
        url = reverse('toggle_favorite', args=[self.event.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Favorite.objects.filter(user=self.user, event=self.event).exists())
