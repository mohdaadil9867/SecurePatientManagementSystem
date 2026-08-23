from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Patient,
    MedicalRecord,
    Billing,
    InsuranceClaim,
    InsuranceCompany,
)
readonly_fields = (
)
class MedicalRecordInline(admin.TabularInline):
    model = MedicalRecord
    extra = 1
    fields = (
        "doctor",
        "doctor_name",
        "department",
        "diagnosis",
        "treatment",
        "prescription",
        "visit_date",
        "next_visit",
        "status",
    )
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):

    readonly_fields = ("patient_id",)

    list_display = (
        "patient_id",
        "first_name",
        "last_name",
        "gender",
        "blood_group",
        "phone_number",
        "user",
        "status",
        "photo_preview",
    )

    search_fields = (
        "patient_id",
        "first_name",
        "last_name",
        "phone_number",
        "email",
    )

    list_filter = (
        "gender",
        "blood_group",
        "status",
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" width="60" height="60" '
                'style="border-radius:50%; object-fit:cover;" />'
                '</a>',
                obj.photo.url,
                obj.photo.url
            )
        return "No Photo"

    photo_preview.short_description = "Photo"
@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):

    readonly_fields = (
        "bill_number",
        "total_amount",
    )

    list_display = (
        "bill_number",
        "medical_record",
        "total_amount",
        "payment_status",
        "payment_method",
        "bill_date",
    )

    search_fields = (
        'medical_record__patient__patient_id',
        'medical_record__patient__first_name',
        'medical_record__patient__last_name',
    )

    list_filter = (
        'payment_status',
        'payment_method',
    )
@admin.register(InsuranceClaim)
class InsuranceClaimAdmin(admin.ModelAdmin):

    list_display = (
        "claim_id",
        "patient",
        "insurance_company",
        "policy_number",
        "claim_amount",
        "approved_amount",
        "claim_status",
        "applied_date",
    )

    list_filter = (
        "claim_status",
        "insurance_company",
        "applied_date",
    )

    search_fields = (
    "claim_id",
    "patient__patient_id",
    "patient__first_name",
    "patient__last_name",
    "policy_number",
    "insurance_company__company_name",
)

    ordering = (
        "-applied_date",
    )

    readonly_fields = (
        "claim_id",
        "created_at",
    )
@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "registration_number",
        "contact_person",
        "phone_number",
        "email",
        "status",
    )

    search_fields = (
        "company_name",
        "registration_number",
        "contact_person",
    )

    list_filter = (
        "status",
    )

    ordering = (
        "company_name",
    )