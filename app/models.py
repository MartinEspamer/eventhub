from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from category.models import Category


class User(AbstractUser):
    is_organizer = models.BooleanField(default=False)

    @classmethod
    def validate_new_user(cls, email, username, password, password_confirm):
        errors = {}

        if email is None:
            errors["email"] = "El email es requerido"
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Ya existe un usuario con este email"

        if username is None:
            errors["username"] = "El username es requerido"
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Ya existe un usuario con este nombre de usuario"

        if password is None or password_confirm is None:
            errors["password"] = "Las contraseñas son requeridas"
        elif password != password_confirm:
            errors["password"] = "Las contraseñas no coinciden"

        return errors


class Event(models.Model):
    EVENT_STATUS_CHOICES = [
        ('activo', 'Activo'),
        ('cancelado', 'Cancelado'),
        ('reprogramado', 'Reprogramado'),
        ('agotado', 'Agotado'),
        ('finalizado', 'Finalizado'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_at = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name="events")
    status = models.CharField(
        max_length=20,
        choices=EVENT_STATUS_CHOICES,
        default='activo',
    )

    def __str__(self):
        return self.title

    @classmethod
    def get_upcoming_events(cls):
        return cls.objects.filter(
            scheduled_at__gte=timezone.localtime(),
            status__in=['activo', 'reprogramado']
        ).order_by("scheduled_at")

    @classmethod
    def get_all_events(cls):
        return cls.objects.all().order_by("scheduled_at")

    @classmethod
    def validate(cls, title, description, scheduled_at):
        errors = {}

        if title == "":
            errors["title"] = "Por favor ingrese un titulo"

        if description == "":
            errors["description"] = "Por favor ingrese una descripcion"

        return errors

    @classmethod
    def new(cls, title, description, scheduled_at, organizer, status='activo'):
        errors = Event.validate(title, description, scheduled_at)

        if len(errors.keys()) > 0:
            return False, errors

        Event.objects.create(
            title=title,
            description=description,
            scheduled_at=scheduled_at,
            organizer=organizer,
            status=status
        )

        return True, None

    def update(self, title=None, description=None, scheduled_at=None, organizer=None, status=None): 
        
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if scheduled_at is not None:
            self.scheduled_at = scheduled_at
        if organizer is not None:
            self.organizer = organizer
        if status is not None:
            self.status = status
        
        self.save()

    def get_ratings_avg(self):
        from rating.models import Rating
        avg = Rating.objects.filter(event=self).aggregate(avg=Avg('rating'))['avg']
        if avg is None:
            return None
        return round(avg, 1)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="favorites")
    class Meta:
        unique_together = ('user', 'event')
