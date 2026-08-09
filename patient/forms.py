from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import (
    InsuranceClaim,
    Billing,
    MedicalRecord,
)

class InsuranceClaimForm(forms.ModelForm):

    class Meta:
        model = InsuranceClaim
        fields = [
            "bill",
            "insurance_company",
            "policy_number",
            "claim_amount",
            "reason",
            "supporting_document",
        ]


class PatientPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })


class BillingForm(forms.ModelForm):

    class Meta:
        model = Billing

        fields = [
            "medical_record",
            "consultation_fee",
            "medicine_fee",
            "laboratory_fee",
            "other_charges",
            "payment_status",
            "payment_method",
            "bill_date",
        ]

        widgets = {
            "medical_record": forms.Select(attrs={"class": "form-select"}),
            "consultation_fee": forms.NumberInput(attrs={"class": "form-control"}),
            "medicine_fee": forms.NumberInput(attrs={"class": "form-control"}),
            "laboratory_fee": forms.NumberInput(attrs={"class": "form-control"}),
            "other_charges": forms.NumberInput(attrs={"class": "form-control"}),
            "payment_status": forms.Select(attrs={"class": "form-select"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "bill_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }


# ===========================
# Doctor Portal Form
# ===========================

class MedicalRecordForm(forms.ModelForm):

    class Meta:
        model = MedicalRecord
        fields = "__all__"

        widgets = {
            "visit_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }