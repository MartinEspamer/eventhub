from django.db import models

from django.conf import settings 
from django.utils import timezone
from django.core.exceptions import ValidationError

# Aclaración: agrego un atributo y modifico uno existente -> status reemplaza a approved ya que 
# en la imagen se observa que puede tener valor pendiente, aprobado o rechazado.
# Agrego detalle ya que se observa en la imagen pero no estaba en el diagrama.

OPCIONES = [
    ('pending', 'Pendiente'),
    ('approved', 'Aprobado'),
    ('rejected', 'Rechazado'),
]

class Refund(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name='refunds')

    status = models.CharField(
        max_length=15,
        choices=OPCIONES,
        default='pending'
    )

    approval_date = models.DateField(
        null=True,
        blank=True
    )

    ticket_code = models.TextField()
    reason = models.TextField()
    detail = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def puede_crear_para_ticket(cls, user, ticket_code):
        existente = cls.objects.filter(user=user, ticket_code=ticket_code)

        if existente.filter(status='pending').exists():
            return False, "Ya tienes una solicitud de reembolso pendiente para este ticket. No puedes crear una nueva solicitud hasta que la anterior sea procesada."

        if existente.filter(status='approved').exists():
            return False, "Ya tienes una solicitud de reembolso aprobada para este ticket. No puedes crear otra solicitud para el mismo ticket."

        return True, "Puedes crear la solicitud"

    def save(self, *args, **kwargs):
        if not self.pk:
            existing_refunds = Refund.objects.filter(
                user=self.user,
                ticket_code=self.ticket_code
            )

            if existing_refunds.filter(status='pending').exists():
                raise ValidationError("Ya tienes una solicitud de reembolso pendiente para este ticket. No puedes crear una nueva solicitud hasta que la anterior sea procesada.")

            if existing_refunds.filter(status='approved').exists():
                raise ValidationError("Ya tienes una solicitud de reembolso aprobada para este ticket. No puedes crear otra solicitud para el mismo ticket.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} – {self.ticket_code}"