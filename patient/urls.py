from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    PatientViewSet,
    MedicalRecordViewSet,
    BillingViewSet,
    download_bill,
)


# =========================================================
# REST API ROUTER
# =========================================================

router = DefaultRouter()

router.register(
    r"patients",
    PatientViewSet
)

router.register(
    r"medical-records",
    MedicalRecordViewSet
)

router.register(
    r"bills",
    BillingViewSet
)


# =========================================================
# URL PATTERNS
# =========================================================

urlpatterns = [

    # =====================================================
    # PATIENT PORTAL
    # =====================================================

    path(
        "patient/login/",
        views.patient_login,
        name="patient_login",
    ),

    path(
        "patient/dashboard/",
        views.patient_dashboard,
        name="patient_dashboard",
    ),

    path(
        "patient/profile/",
        views.patient_profile,
        name="patient_profile",
    ),
    path(
    "profile/",
    views.patient_profile,
    name="patient_profile"
),

    path(
        "patient/medical-records/",
        views.patient_medical_records,
        name="patient_medical_records",
    ),

    path(
        "patient/billing/",
        views.patient_billing,
        name="patient_billing",
    ),

    path(
        "patient/claims/",
        views.patient_claims,
        name="patient_claims",
    ),

    path(
        "patient/insurance/apply/",
        views.apply_insurance_claim,
        name="apply_insurance_claim",
    ),

    path(
        "patient/claims/new/",
        views.apply_insurance_claim,
        name="patient_new_claim",
    ),

    path(
        "patient/bill/<int:pk>/download/",
        views.patient_download_bill,
        name="patient_download_bill",
    ),

    path(
        "patient/change-password/",
        views.change_password,
        name="change_password",
    ),

    path(
        "patient/logout/",
        views.patient_logout,
        name="patient_logout",
    ),


    # =========================
# INSURANCE PORTAL
# =========================

path(
    "insurance/login/",
    views.insurance_login,
    name="insurance_login",
),

path(
    "insurance/dashboard/",
    views.insurance_dashboard,
    name="insurance_dashboard",
),

path(
    "insurance/claims/",
    views.insurance_claim_list,
    name="insurance_claim_list",
),

path(
    "insurance/claims/<int:pk>/",
    views.insurance_claim_detail,
    name="insurance_claim_detail",
),

path(
    "insurance/approved/",
    views.approved_claims,
    name="insurance_approved_claims",
),

path(
    "insurance/rejected/",
    views.rejected_claims,
    name="insurance_rejected_claims",
),

path(
    "insurance/reports/",
    views.insurance_reports,
    name="insurance_reports",
),

path(
    "insurance/profile/",
    views.insurance_profile,
    name="insurance_profile",
),

path(
    "insurance/change-password/",
    views.insurance_change_password,
    name="insurance_change_password",
),

path(
    "insurance/notifications/",
    views.insurance_notifications,
    name="insurance_notifications",
),

path(
    "insurance/logout/",
    views.insurance_logout,
    name="insurance_logout",
),


    # =====================================================
    # DOCTOR PORTAL
    # =====================================================

    path(
        "doctor/login/",
        views.doctor_login,
        name="doctor_login",
    ),

    path(
        "doctor/dashboard/",
        views.doctor_dashboard,
        name="doctor_dashboard",
    ),

    path(
        "doctor/patients/",
        views.doctor_patients,
        name="doctor_patients",
    ),

    # IMPORTANT:
    # This matches:
    # doctor_patient_detail(request, pk)

    path(
        "doctor/patient/<int:pk>/",
        views.doctor_patient_detail,
        name="doctor_patient_detail",
    ),

    path(
        "doctor/patient/<int:patient_id>/add-record/",
        views.add_medical_record,
        name="add_medical_record",
    ),

    path(
        "doctor/medical-record/<int:pk>/edit/",
        views.edit_medical_record,
        name="edit_medical_record",
    ),

    path(
        "doctor/records/",
        views.doctor_records,
        name="doctor_records",
    ),
    path(
    "doctor/prescriptions/",
    views.doctor_prescriptions,
    name="doctor_prescriptions",
),
path(
    "doctor/profile/",
    views.doctor_profile,
    name="doctor_profile",
),
    path(
        "doctor/add/patient/",
        views.doctor_add_patient,
        name="doctor_add_patient",
    ),
    path(
    "doctor/change-password/",
    views.doctor_change_password,
    name="doctor_change_password",
),

    path(
        "doctor/logout/",
        views.doctor_logout,
        name="doctor_logout",
    ),


    # =====================================================
    # HOSPITAL PORTAL
    # =====================================================

    path(
        "hospital/login/",
        views.hospital_login,
        name="hospital_login",
    ),

    path(
        "hospital/dashboard/",
        views.hospital_dashboard,
        name="hospital_dashboard",
    ),

    path(
        "hospital/patients/",
        views.hospital_patients,
        name="hospital_patients",
    ),

    path(
        "hospital/patients/add/",
        views.hospital_add_patient,
        name="hospital_add_patient",
    ),

    path(
        "hospital/logout/",
        views.hospital_logout,
        name="hospital_logout",
    ),

    # =====================================================
# BILLING PORTAL
# =====================================================

path(
    "billing/login/",
    views.billing_login,
    name="billing_login",
),

path(
    "billing/dashboard/",
    views.billing_dashboard,
    name="billing_dashboard",
),

path(
    "billing/list/",
    views.billing_list,
    name="billing_list",
),

path(
    "billing/create/",
    views.create_bill,
    name="create_bill",
),

path(
    "billing/edit/<int:pk>/",
    views.edit_bill,
    name="edit_bill",
),

path(
    "billing/delete/<int:pk>/",
    views.delete_bill,
    name="delete_bill",
),

path(
    "billing/download/<int:pk>/",
    views.download_bill,
    name="download_bill",
),

path(
    "billing/profile/",
    views.billing_profile,
    name="billing_profile",
),

path(
    "billing/logout/",
    views.billing_logout,
    name="billing_logout",
),
]


# =========================================================
# API ROUTER URLS
# =========================================================

urlpatterns += router.urls