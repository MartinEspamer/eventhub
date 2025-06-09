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
        
        warning_alert = self.page.locator(".alert")
        if warning_alert.count() > 0:
            expect(warning_alert.first).to_be_visible()
            alert_text = warning_alert.first.text_content()
            self.assertIn("solicitud", alert_text.lower()) # type: ignore
        else:
            field_errors = self.page.locator(".text-danger")
            if field_errors.count() > 0:
                expect(field_errors.first).to_be_visible()
                error_text = field_errors.first.text_content()
                self.assertIn("solicitud", error_text.lower()) # type: ignore
        
        self.assertEqual(Refund.objects.count(), 1)