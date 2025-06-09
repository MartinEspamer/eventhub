from playwright.sync_api import expect
from app.models import User
from refunds.models import Refund

from .base import BaseE2ETest


class RefundCreationE2ETest(BaseE2ETest):

    def setUp(self):
        super().setUp()

        self.user = User.objects.create_user(
            username="username",
            password="password",
            email="username@example.com",
            is_organizer=False,
        )
        Refund.objects.create(
            user=self.user,
            ticket_code="1",
            reason="option1"
        )

    def test_user_no_puede_solicitar_refund_de_ticket_con_refund_pendiente(self):
        """Test E2E para validación de límite de 1 solicitud pendiente por ticket"""
        
        self.login_user("username", "password")
        self.page.goto(f"{self.live_server_url}/refunds/add/")
        
        page_title = self.page.locator("h3")
        expect(page_title).to_contain_text("Formulario de Solicitud")
        self.page.get_by_label("Código de ticket *").fill("1")
        self.page.get_by_label("Motivo del reembolso *").select_option(index=1) 
        self.page.get_by_label("Entiendo y acepto la política de reembolsos.").check()
        self.page.locator("form#refund-form button[type='submit']").click()

        field_error = self.page.locator(".text-danger", has_text="Ya tienes una solicitud de reembolso pendiente")
        expect(field_error).to_be_visible()
        expect(field_error).to_contain_text("solicitud de reembolso pendiente")
