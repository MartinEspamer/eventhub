from django.test import Client,TestCase
from django.urls import reverse

from app.models import User
from refunds.models import Refund


class RefundIntegrationTest(TestCase):

    def setUp(self):
        # Configuración mínima
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.refund = Refund.objects.create(
            user=self.user,
            ticket_code="1",
            reason="Opcion 1",
        )
        self.client = Client()
    
    def test_muestra_mensaje_de_advertencia_si_hay_solicitud_pendiente(self):
        """
        Verifica que el sistema muestra un mensaje cuando de advertencia cuando ya existe una solicitud en pendiente para un ticket.
        """
        self.client.login(username="testuser", password="password123")
        resp = self.client.get(reverse('refunds:refund_add'))
        
        self.assertIn('warning_message', resp.context)
        self.assertIn(f"Tienes solicitudes de reembolso pendientes para los tickets: {self.refund.ticket_code}.", resp.context['warning_message']['message'])