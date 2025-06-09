from django import forms

from .models import Refund


class RefundForm(forms.ModelForm):
    reason = forms.ChoiceField(
        label="Motivo del reembolso *",
        choices=[
            ('', 'Selecciona un motivo'),
            ('option1', 'Opción 1'),
            ('option2', 'Opción 2'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}), 
        error_messages={'required': 'Indique la razón de la solicitud de reembolso.'}
    )

    accept_policy = forms.BooleanField(
        label="Entiendo y acepto la política de reembolsos.",
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'Debes aceptar la política de reembolsos para continuar.'}
    )

    class Meta:
        model = Refund
        fields = ["ticket_code", "reason", "detail"]
        
        widgets = {
            "ticket_code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Escribe el código del ticket aquí...",
            }),
            "detail": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Proporciona más información sobre tu solicitud...",
                "rows": 5,
            }),
        }
        error_messages = {
            "ticket_code": {
                "required": "Indique el código del ticket.",
            },
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_ticket_code(self):
        """
        Valida que no exista ya una solicitud de reembolso pendiente
        para el mismo ticket por parte del mismo usuario.
        """
        ticket_code = self.cleaned_data.get("ticket_code")
        
        if not ticket_code:
            return ticket_code
        
        query = Refund.objects.filter(
            user=self.user,
            ticket_code=ticket_code,
            status='pending'
        )

        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        if query.exists():
            raise forms.ValidationError("Ya tienes una solicitud de reembolso pendiente para este ticket.")
    
        return ticket_code