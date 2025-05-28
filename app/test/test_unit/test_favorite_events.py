from django.test import TestCase
from app.models import User, Event, Favorite
from category.models import Category
from django.utils.timezone import now, timedelta

class FavoriteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.organizer = User.objects.create_user(username='organizer', password='password')
        self.category = Category.objects.create(name='Música', is_active=True)
        self.event = Event.objects.create(
            title='Concierto',
            description='Concierto de rock',
            scheduled_at=now() + timedelta(days=3),
            organizer=self.organizer
        )
        self.event.categories.add(self.category)

    def test_create_favorite_successfully(self):
        favorite = Favorite.objects.create(user=self.user, event=self.event)
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.event, self.event)
        self.assertEqual(Favorite.objects.count(), 1)

    def test_duplicate_favorite(self):
        Favorite.objects.create(user=self.user, event=self.event)
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.user, event=self.event)
