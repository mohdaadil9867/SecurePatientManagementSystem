from django import forms

from .models import (
    Patient,
    MedicalRecord,
    Billing,
    InsuranceClaim,
)
from django.contrib.auth.forms import PasswordChangeForm

class PatientForm(forms.ModelForm):

    class Meta:
        model = Patient

        fields = [
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "blood_group",
            "phone_number",
            "email",
            "address",
            "profile_photo",
            "status",
        ]

        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "gender": forms.Select(
                attrs={"class": "form-select"}
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "blood_group": forms.Select(
                attrs={"class": "form-select"}
            ),

            "phone_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),

            "profile_photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*"
                }
            ),
            
            "status": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input"
                }
            ),
        }
        
# Patient Insurance Claim Form


class PatientInsuranceClaimForm(forms.ModelForm):

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

        widgets = {

            "bill": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "insurance_company": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "policy_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter policy number"
                }
            ),

            "claim_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Enter claim amount"
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter claim reason"
                }
            ),

            "supporting_document": forms.ClearableFileInput(
                attrs={
                    "class": "form-control"
                }
            ),
        }



# =========================================================
# MEDICAL RECORD FORM
# =========================================================

class MedicalRecordForm(forms.ModelForm):

    class Meta:
        model = MedicalRecord

        fields = [
            "patient",
            "doctor",
            "doctor_name",
            "department",
            "diagnosis",
            "symptoms",
            "treatment",
            "prescription",
            "medical_report",
            "visit_date",
            "next_visit",
            "remarks",
            "status",
        ]

        widgets = {

            "patient": forms.Select(
                attrs={"class": "form-select"}
            ),

            "doctor": forms.Select(
                attrs={"class": "form-select"}
            ),

            "doctor_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "department": forms.TextInput(
                attrs={"class": "form-control"}
            ),

            "diagnosis": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "symptoms": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "treatment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "prescription": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "medical_report": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),

            "visit_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "next_visit": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "remarks": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "status": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }


# =========================================================
# BILLING FORM
# =========================================================

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

            "medical_record": forms.Select(
                attrs={"class": "form-select"}
            ),

            "consultation_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "medicine_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "laboratory_fee": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "other_charges": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                }
            ),

            "payment_status": forms.Select(
                attrs={"class": "form-select"}
            ),

            "payment_method": forms.Select(
                attrs={"class": "form-select"}
            ),

            "bill_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }
        # =========================================================
# INSURANCE CLAIM FORM
# =========================================================

class InsuranceClaimForm(forms.ModelForm):

    class Meta:
        model = InsuranceClaim

        fields = [
            "medical_record",
            "bill",
            "insurance_company",
            "policy_number",
            "claim_amount",
            "reason",
            "supporting_document",
        ]

        widgets = {

            "medical_record": forms.Select(
                attrs={"class": "form-select"}
            ),

            "bill": forms.Select(
                attrs={"class": "form-select"}
            ),

            "insurance_company": forms.Select(
                attrs={"class": "form-select"}
            ),

            "policy_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter policy number"
                }
            ),

            "claim_amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "placeholder": "Enter claim amount"
                }
            ),

            "reason": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter claim reason"
                }
            ),

            "supporting_document": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }
class PatientPasswordChangeForm(PasswordChangeForm): pass