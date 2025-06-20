from django.core.exceptions import ValidationError
from django.test import TestCase

from app.models import User
from refunds.models import Refund


class RefundTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario1',
            email='user@example.com',
            password='password123'
        )
        self.refund = Refund.objects.create(
            user=self.user,
            ticket_code="1",
            reason="Opcion 1"
        )
    
    def test_unico_refund_para_ticket_con_refund_pendiente(self):
        with self.assertRaisesMessage(ValidationError, "Ya tienes una solicitud de reembolso pendiente para este ticket. No puedes crear una nueva solicitud hasta que la anterior sea procesada."):
            Refund.objects.create(
                user=self.user,
                ticket_code="1",
                reason="Otro intento para ticket pendiente"
            )
        
        self.assertEqual(Refund.objects.filter(user=self.user, ticket_code="1").count(), 1)

    