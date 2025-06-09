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
        self.page.click("button[type='submit']")
        
        warning_alert_locator = self.page.locator(".alert")
        if warning_alert_locator.count() > 0:
            warning_alert = warning_alert_locator.first
            expect(warning_alert).to_be_visible()
            expect(warning_alert).to_contain_text("solicitud")
        else:
            field_errors_locator = self.page.locator(".text-danger")
            if field_errors_locator.count() > 0:
                error_field = field_errors_locator.first
                expect(error_field).to_be_visible()
                expect(error_field).to_contain_text("solicitud")

        self.assertEqual(Refund.objects.count(), 1)