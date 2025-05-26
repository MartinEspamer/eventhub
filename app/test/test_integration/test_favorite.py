from django.test import TestCase
from django.urls import reverse
from app.models import User, Event, Favorite
from django.utils.timezone import now, timedelta

class FavoriteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.event = Event.objects.create(
            title='Evento Test',
            description='Descripción del evento',
            scheduled_at=now() + timedelta(days=2),
            organizer=self.user
        )

    def test_toggle_favorite_adds_favorite(self):
        self.client.login(username='user', password='pass')
        url = reverse('toggle_favorite', args=[self.event.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Favorite.objects.filter(user=self.user, event=self.event).exists())

    def test_toggle_favorite_removes_favorite(self):
        self.client.login(username='user', password='pass')
        Favorite.objects.create(user=self.user, event=self.event)
        url = reverse('toggle_favorite', args=[self.event.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertFalse(Favorite.objects.filter(user=self.user, event=self.event).exists())
