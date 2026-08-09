from rest_framework import serializers

from datetime import date
from .models import (
    Patient,
    MedicalRecord,
    Billing,
)
import re


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = (
            "patient_id",
            "created_at",
            "updated_at",
        )

    # First Name Validation
    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "First name cannot be empty."
            )

        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError(
                "First name should contain only letters."
            )

        return value.title()

    # Last Name Validation
    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Last name cannot be empty."
            )

        if not value.replace(" ", "").isalpha():
            raise serializers.ValidationError(
                "Last name should contain only letters."
            )

        return value.title()

    # Phone Number Validation
    def validate_phone_number(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        return value

    # Emergency Contact Validation
    def validate_emergency_contact_number(self, value):
        if not re.fullmatch(r"\d{10}", value):
            raise serializers.ValidationError(
                "Emergency contact number must contain exactly 10 digits."
            )

        return value

    # Date of Birth Validation
    def validate_date_of_birth(self, value):
        if value > date.today():
            raise serializers.ValidationError(
                "Date of birth cannot be in the future."
            )

        return value

    # Email Validation
    def validate_email(self, value):
        if Patient.objects.filter(email=value).exists():
            if self.instance is None or self.instance.email != value:
                raise serializers.ValidationError(
                    "This email is already registered."
                )

        return value

class MedicalRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalRecord
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
        )

    def validate_doctor_name(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Doctor name cannot be empty."
            )

        return value.title()

    def validate_department(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Department cannot be empty."
            )

        return value.title()

    def validate_diagnosis(self, value):

        if not value.strip():
            raise serializers.ValidationError(
                "Diagnosis is required."
            )

        return value

    def validate_visit_date(self, value):

        from datetime import date

        if value > date.today():
            raise serializers.ValidationError(
                "Visit date cannot be in the future."
            )

        return value

    def validate(self, data):

        visit = data.get("visit_date")
        next_visit = data.get("next_visit")

        if next_visit and next_visit < visit:
            raise serializers.ValidationError({
                "next_visit":
                "Next visit cannot be before visit date."
            })

        return data


class BillingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Billing
        fields = "__all__"
        read_only_fields = (
            "total_amount",
            "created_at",
        )

    def validate(self, data):

        fees = [
            data.get("consultation_fee", 0),
            data.get("medicine_fee", 0),
            data.get("laboratory_fee", 0),
            data.get("other_charges", 0),
        ]

        for fee in fees:
            if fee < 0:
                raise serializers.ValidationError(
                    "Charges cannot be negative."
                )

        return data