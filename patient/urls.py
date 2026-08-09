from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

from .views import (
    PatientViewSet,
    MedicalRecordViewSet,
    BillingViewSet,
    download_bill,
)

router = DefaultRouter()

router.register(r'patients', PatientViewSet)
router.register(r'medical-records', MedicalRecordViewSet)
router.register(r'bills', BillingViewSet)

urlpatterns = [

    # -------------------
    # Patient Portal
    # -------------------

path(
        "patient/login/",
        views.patient_login,
        name="patient_login",
),

path(
    "patient/profile/",
    views.patient_profile,
    name="patient_profile",
),
    

 path(
        "patient/dashboard/",
        views.patient_dashboard,
        name="patient_dashboard",
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
    # -------------------
    # Bill PDF
    # -------------------

    path(
        "bill/<int:pk>/pdf/",
        download_bill,
        name="download-bill",
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
    "patient/logout/",
    views.patient_logout,
    name="patient_logout",
),

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
    "insurance/logout/",
    views.insurance_logout,
    name="insurance_logout",
),
path(
    "patient/change-password/",
    views.change_password,
    name="change_password",
),
path(
    "insurance/claims/",
    views.insurance_claim_list,
    name="insurance_claim_list",
),
path(
    "insurance/claim/<int:pk>/",
    views.insurance_claim_detail,
    name="insurance_claim_detail",
),
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
    "billing/logout/",
    views.billing_logout,
    name="billing_logout",
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
    "billing/create/",
    views.create_bill,
    name="create_bill",
),
path(
    "billing/download/",
    views.download_bill,
    name="download_bill",
),
path(
    "billing/profile/",
    views.billing_profile,
    name="billing_profile",
),
path(
    "doctor/records/",
    views.doctor_records,
    name="doctor_records",
),

path(
    "doctor/record/<int:pk>/edit/",
    views.edit_medical_record,
    name="edit_medical_record",
),

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
    "doctor/logout/",
    views.doctor_logout,
    name="doctor_logout",
),
path(
    "doctor/patients/",
    views.doctor_patients,
    name="doctor_patients",
),
]

urlpatterns += router.urls