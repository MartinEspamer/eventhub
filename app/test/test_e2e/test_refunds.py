from playwright.sync_api import expect

from refunds.models import Refund

from .base import BaseE2ETest


class RefundCreationE2ETest(BaseE2ETest):

    def setUp(self):
        super().setUp()
        self.user = self.create_test_user()

        Refund.objects.create(
            user=self.user,
            ticket_code="1",
            reason="option1"
        )

    def test_user_no_puede_solicitar_refund_de_ticket_con_refund_pendiente(self):
        """Test E2E para validación de límite de 1 solicitud pendiente por ticket"""
        self.login_user("usuario_test", "password123")
        self.page.goto(f"{self.live_server_url}/refunds/add/")
        self.page.get_by_label("Código de ticket *").fill("1")
        self.page.get_by_label("Motivo del reembolso *").select_option(label="Opción 2")
        self.page.get_by_label("Entiendo y acepto la política de reembolsos.").check()
        self.page.click("button[type='submit']")
        self.assertEqual(Refund.objects.filter(user=self.user, ticket_code="1").count(), 1)