from datetime import date

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.db.models import Q, Exists, OuterRef
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils import timezone

from rest_framework import filters, viewsets
from rest_framework.permissions import DjangoModelPermissions

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor

from .models import (
    Patient,
    MedicalRecord,
    Billing,
    InsuranceClaim,
    InsuranceCompany,
)

from .serializers import (
    PatientSerializer,
    MedicalRecordSerializer,
    BillingSerializer,
)

from .forms import (
    InsuranceClaimForm,
    PatientPasswordChangeForm,
    BillingForm,
    MedicalRecordForm,
    PatientForm,
)

# =========================================================
# REST API
# =========================================================


class PatientViewSet(viewsets.ModelViewSet):

    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [DjangoModelPermissions]

    search_fields = [
        "patient_id",
        "first_name",
        "last_name",
        "phone_number",
        "email",
    ]

    ordering_fields = [
        "patient_id",
        "first_name",
        "last_name",
        "created_at",
        "date_of_birth",
    ]

    ordering = ["patient_id"]

    def perform_destroy(self, instance):

        instance.status = False
        instance.save()


class MedicalRecordViewSet(viewsets.ModelViewSet):

    queryset = MedicalRecord.objects.filter(status=True)
    serializer_class = MedicalRecordSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "patient__patient_id",
        "patient__first_name",
        "patient__last_name",
        "doctor_name",
        "department",
        "diagnosis",
    ]

    ordering_fields = [
        "visit_date",
        "doctor_name",
        "department",
        "created_at",
    ]

    ordering = ["-visit_date"]


class BillingViewSet(viewsets.ModelViewSet):

    queryset = Billing.objects.all()
    serializer_class = BillingSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "medical_record__patient__patient_id",
        "medical_record__patient__first_name",
        "medical_record__patient__last_name",
    ]

    ordering_fields = [
        "bill_date",
        "total_amount",
    ]

    ordering = ["-bill_date"]


# =========================================================
# COMMON BILLING ACCESS HELPER
# =========================================================
#
# Logic:
#
# 1. Patient assigned to Billing Staff 1
#    -> Billing Staff 1 can access.
#
# 2. Patient assigned to Billing Staff 2
#    -> Billing Staff 2 can access.
#
# 3. Patient has no billing staff assigned
#    -> All Billing Staff can access.
#
# =========================================================


def billing_access_q(user):

    return (
        Q(
            medical_record__patient__assigned_billing_staff=user
        )
        |
        Q(
            medical_record__patient__assigned_billing_staff__isnull=True
        )
    )


def billing_record_access_q(user):

    return (
        Q(
            patient__assigned_billing_staff=user
        )
        |
        Q(
            patient__assigned_billing_staff__isnull=True
        )
    )


# =========================================================
# HOME
# =========================================================


def home(request):

    return render(
        request,
        "home.html"
    )


# =========================================================
# PATIENT PORTAL
# =========================================================


def patient_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(request, user)

            return redirect(
                "patient_dashboard"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "patient/login.html"
    )


@login_required
def patient_dashboard(request):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    medical_count = MedicalRecord.objects.filter(
        patient=patient
    ).count()

    billing_count = Billing.objects.filter(
        medical_record__patient=patient
    ).count()

    claim_count = InsuranceClaim.objects.filter(
        patient=patient
    ).count()

    recent_records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by(
        "-created_at"
    )[:5]

    return render(
        request,
        "patient/dashboard.html",
        {
            "patient": patient,
            "medical_count": medical_count,
            "billing_count": billing_count,
            "claim_count": claim_count,
            "recent_records": recent_records,
        }
    )


@login_required
def patient_profile(request):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    return render(
        request,
        "patient/profile.html",
        {
            "patient": patient,
        }
    )


@login_required
def patient_medical_records(request):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by(
        "-visit_date"
    )

    return render(
        request,
        "patient/medical_records.html",
        {
            "patient": patient,
            "records": records,
        }
    )


@login_required
def patient_billing(request):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    bills = Billing.objects.filter(
        medical_record__patient=patient
    ).order_by(
        "-bill_date"
    )

    return render(
        request,
        "patient/billing.html",
        {
            "patient": patient,
            "bills": bills,
        }
    )


# =========================================================
# PATIENT BILL PDF
# =========================================================


@login_required
def patient_download_bill(request, pk):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    bill = get_object_or_404(
        Billing,
        pk=pk,
        medical_record__patient=patient
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="Bill_{bill.bill_number}.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=A4
    )

    width, height = A4

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawString(
        50,
        height - 60,
        "SECURE PATIENT SYSTEM"
    )

    pdf.setFont(
        "Helvetica-Bold",
        16
    )

    pdf.drawString(
        50,
        height - 100,
        "MEDICAL BILL"
    )

    y = height - 150

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        50,
        y,
        f"Bill Number: {bill.bill_number}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Patient ID: {patient.patient_id}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Patient Name: {patient.first_name} {patient.last_name}"
    )

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Bill Date: {bill.bill_date}"
    )

    y -= 50

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        50,
        y,
        "Billing Details"
    )

    y -= 30

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        70,
        y,
        f"Consultation Fee: Rs. {bill.consultation_fee}"
    )

    y -= 25

    pdf.drawString(
        70,
        y,
        f"Medicine Fee: Rs. {bill.medicine_fee}"
    )

    y -= 25

    pdf.drawString(
        70,
        y,
        f"Laboratory Fee: Rs. {bill.laboratory_fee}"
    )

    y -= 25

    pdf.drawString(
        70,
        y,
        f"Other Charges: Rs. {bill.other_charges}"
    )

    y -= 40

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        70,
        y,
        f"TOTAL: Rs. {bill.total_amount}"
    )

    y -= 35

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        70,
        y,
        f"Payment Method: {bill.payment_method}"
    )

    y -= 25

    pdf.drawString(
        70,
        y,
        f"Payment Status: {bill.payment_status}"
    )

    pdf.setFont(
        "Helvetica-Oblique",
        9
    )

    pdf.drawString(
        50,
        50,
        "This is a computer-generated bill."
    )

    pdf.save()

    return response


# =========================================================
# PATIENT INSURANCE CLAIMS
# =========================================================


@login_required
def patient_claims(request):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    claims = InsuranceClaim.objects.select_related(
        "insurance_company",
        "medical_record",
        "bill",
    ).filter(
        patient=patient,
        status=True
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "patient/claims.html",
        {
            "claims": claims,
            "total_claims": claims.count(),
            "pending": claims.filter(
                claim_status="Pending"
            ).count(),
            "approved": claims.filter(
                claim_status="Approved"
            ).count(),
            "rejected": claims.filter(
                claim_status="Rejected"
            ).count(),
        }
    )


@login_required
def patient_insurance_claims(request):

    patient = get_object_or_404(
        Patient,
        user=request.user,
        status=True
    )

    claims = InsuranceClaim.objects.filter(
        patient=patient,
        status=True,
    ).select_related(
        "insurance_company",
        "medical_record",
        "bill"
    )

    return render(
        request,
        "patient/insurance_claims.html",
        {
            "patient": patient,
            "claims": claims,
        }
    )


@login_required
def my_insurance_claims(request):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    claims = InsuranceClaim.objects.filter(
        patient=patient
    )

    return render(
        request,
        "patient/my_claims.html",
        {
            "claims": claims
        }
    )


@login_required
def apply_insurance_claim(request):

    patient = get_object_or_404(
        Patient,
        user=request.user
    )

    medical_records = MedicalRecord.objects.filter(
        patient=patient
    )

    bills = Billing.objects.filter(
        medical_record__patient=patient
    )

    companies = InsuranceCompany.objects.filter(
        status=True
    )

    if request.method == "POST":

        form = InsuranceClaimForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            claim = form.save(
                commit=False
            )

            claim.patient = patient

            medical_record_id = request.POST.get(
                "medical_record"
            )

            claim.medical_record = get_object_or_404(
                MedicalRecord,
                id=medical_record_id,
                patient=patient
            )

            bill_id = request.POST.get(
                "bill"
            )

            claim.bill = get_object_or_404(
                Billing,
                id=bill_id,
                medical_record=claim.medical_record
            )

            insurance_company_id = request.POST.get(
                "insurance_company"
            )

            claim.insurance_company = get_object_or_404(
                InsuranceCompany,
                id=insurance_company_id,
                status=True
            )

            claim.claim_status = "Pending"
            claim.approved_amount = 0
            claim.verified_date = None
            claim.status = True

            claim.save()

            messages.success(
                request,
                "Insurance claim submitted successfully."
            )

            return redirect(
                "patient_claims"
            )

    else:

        form = InsuranceClaimForm()

    return render(
        request,
        "patient/apply_claim.html",
        {
            "form": form,
            "medical_records": medical_records,
            "bills": bills,
            "companies": companies,
        }
    )


# =========================================================
# PATIENT PASSWORD / LOGOUT
# =========================================================


@login_required
def change_password(request):

    if request.method == "POST":

        form = PatientPasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect(
                "patient_dashboard"
            )

    else:

        form = PatientPasswordChangeForm(
            request.user
        )

    return render(
        request,
        "patient/change_password.html",
        {
            "form": form
        }
    )


@login_required
def patient_logout(request):

    logout(request)

    return redirect(
        "home"
    )


# =========================================================
# INSURANCE LOGIN
# =========================================================


def insurance_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.groups.filter(
                name="Insurance"
            ).exists():

                login(
                    request,
                    user
                )

                return redirect(
                    "insurance_dashboard"
                )

        return render(
            request,
            "insurance/login.html",
            {
                "error":
                "Invalid username or password."
            }
        )

    return render(
        request,
        "insurance/login.html"
    )


# =========================================================
# INSURANCE HELPER
# =========================================================


def get_logged_in_insurance_company(request):

    return get_object_or_404(
        InsuranceCompany,
        user=request.user
    )


# =========================================================
# INSURANCE DASHBOARD
# =========================================================


@login_required
def insurance_dashboard(request):

    company = get_object_or_404(
        InsuranceCompany,
        user=request.user
    )

    claims = InsuranceClaim.objects.select_related(
        "patient",
        "medical_record",
        "bill"
    ).filter(
        insurance_company=company
    )

    pending_claims = claims.filter(
        claim_status="Pending"
    ).count()

    under_review_claims = claims.filter(
        claim_status="Under Review"
    ).count()

    approved_claims = claims.filter(
        claim_status="Approved"
    ).count()

    rejected_claims = claims.filter(
        claim_status="Rejected"
    ).count()

    total_claims = claims.count()

    recent_claims = claims.order_by(
        "-created_at"
    )[:5]

    notifications = claims.filter(
        claim_status="Pending"
    ).order_by(
        "-created_at"
    )[:5]

    return render(
        request,
        "insurance/dashboard.html",
        {
            "company": company,
            "total_claims": total_claims,
            "pending_claims": pending_claims,
            "under_review_claims": under_review_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "recent_claims": recent_claims,
            "notifications": notifications,
        }
    )


# =========================================================
# INSURANCE CLAIM LIST
# =========================================================


@login_required
def insurance_claim_list(request):

    insurance_company = (
        get_logged_in_insurance_company(request)
    )

    claims = InsuranceClaim.objects.select_related(
        "patient",
        "bill",
        "medical_record",
        "insurance_company"
    ).filter(
        insurance_company=insurance_company
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        claims = claims.filter(
            Q(
                claim_id__icontains=search
            )
            |
            Q(
                patient__patient_id__icontains=search
            )
            |
            Q(
                patient__first_name__icontains=search
            )
            |
            Q(
                patient__last_name__icontains=search
            )
            |
            Q(
                bill__bill_number__icontains=search
            )
        )

    status = request.GET.get(
        "status",
        ""
    ).strip()

    if status:

        claims = claims.filter(
            claim_status=status
        )

    claims = claims.order_by(
        "-created_at"
    )

    return render(
        request,
        "insurance/claims.html",
        {
            "claims": claims,
            "search": search,
            "status": status,
            "insurance_company": insurance_company,
        }
    )


# =========================================================
# INSURANCE CLAIM DETAIL
# =========================================================


@login_required
def insurance_claim_detail(request, pk):

    company = get_object_or_404(
        InsuranceCompany,
        user=request.user,
        status=True
    )

    claim = get_object_or_404(
        InsuranceClaim.objects.select_related(
            "patient",
            "medical_record",
            "bill",
            "insurance_company"
        ),
        pk=pk,
        insurance_company=company
    )

    medical_records = MedicalRecord.objects.filter(
        patient=claim.patient,
        status=True
    ).order_by(
        "-visit_date"
    )

    bills = Billing.objects.filter(
        medical_record__patient=claim.patient
    ).order_by(
        "-bill_date"
    )

    if request.method == "POST":

        claim.claim_status = request.POST.get(
            "claim_status"
        )

        claim.approved_amount = (
            request.POST.get(
                "approved_amount"
            )
            or 0
        )

        claim.remarks = request.POST.get(
            "remarks",
            ""
        )

        claim.save()

        messages.success(
            request,
            "Claim decision updated successfully."
        )

        return redirect(
            "insurance_claim_detail",
            pk=claim.pk
        )

    return render(
        request,
        "insurance/claim_detail.html",
        {
            "claim": claim,
            "patient": claim.patient,
            "medical_record": claim.medical_record,
            "medical_records": medical_records,
            "bill": claim.bill,
            "bills": bills,
            "insurance_company": company,
        }
    )


# =========================================================
# APPROVED CLAIMS
# =========================================================


@login_required
def approved_claims(request):

    insurance_company = (
        get_logged_in_insurance_company(request)
    )

    claims = InsuranceClaim.objects.select_related(
        "patient",
        "bill",
        "medical_record",
        "insurance_company"
    ).filter(
        insurance_company=insurance_company,
        claim_status="Approved"
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        claims = claims.filter(
            Q(
                claim_id__icontains=search
            )
            |
            Q(
                patient__patient_id__icontains=search
            )
            |
            Q(
                patient__first_name__icontains=search
            )
            |
            Q(
                patient__last_name__icontains=search
            )
        )

    claims = claims.order_by(
        "-created_at"
    )

    return render(
        request,
        "insurance/approved_claims.html",
        {
            "claims": claims,
            "search": search,
            "status": "Approved",
            "insurance_company": insurance_company,
        }
    )


# =========================================================
# REJECTED CLAIMS
# =========================================================


@login_required
def rejected_claims(request):

    insurance_company = (
        get_logged_in_insurance_company(request)
    )

    claims = InsuranceClaim.objects.select_related(
        "patient",
        "bill",
        "medical_record",
        "insurance_company"
    ).filter(
        insurance_company=insurance_company,
        claim_status="Rejected"
    )

    search = request.GET.get(
        "search",
        ""
    ).strip()

    if search:

        claims = claims.filter(
            Q(
                claim_id__icontains=search
            )
            |
            Q(
                patient__patient_id__icontains=search
            )
            |
            Q(
                patient__first_name__icontains=search
            )
            |
            Q(
                patient__last_name__icontains=search
            )
        )

    claims = claims.order_by(
        "-created_at"
    )

    return render(
        request,
        "insurance/rejected_claims.html",
        {
            "claims": claims,
            "search": search,
            "status": "Rejected",
            "insurance_company": insurance_company,
        }
    )


# =========================================================
# INSURANCE REPORTS
# =========================================================


@login_required
def insurance_reports(request):

    insurance_company = (
        get_logged_in_insurance_company(request)
    )

    claims = InsuranceClaim.objects.filter(
        insurance_company=insurance_company
    )

    total_claims = claims.count()

    approved_claims = claims.filter(
        claim_status="Approved"
    ).count()

    rejected_claims = claims.filter(
        claim_status="Rejected"
    ).count()

    pending_claims = claims.filter(
        claim_status="Pending"
    ).count()

    under_review_claims = claims.filter(
        claim_status="Under Review"
    ).count()

    total_claim_amount = sum(
        claim.claim_amount
        for claim in claims
    )

    total_approved_amount = sum(
        claim.approved_amount
        for claim in claims
    )

    return render(
        request,
        "insurance/reports.html",
        {
            "insurance_company": insurance_company,
            "total_claims": total_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "pending_claims": pending_claims,
            "under_review_claims": under_review_claims,
            "total_claim_amount": total_claim_amount,
            "total_approved_amount": total_approved_amount,
        }
    )


# =========================================================
# INSURANCE PROFILE / PASSWORD / LOGOUT
# =========================================================


@login_required
def insurance_profile(request):

    company = InsuranceCompany.objects.filter(
        user=request.user
    ).first()

    if not company:

        return render(
            request,
            "insurance/profile.html",
            {
                "company": None,
                "error":
                    "No insurance company profile is linked to this account."
            }
        )

    return render(
        request,
        "insurance/profile.html",
        {
            "company": company
        }
    )


@login_required
def insurance_change_password(request):

    if request.method == "POST":

        old_password = request.POST.get(
            "old_password"
        )

        new_password = request.POST.get(
            "new_password"
        )

        confirm_password = request.POST.get(
            "confirm_password"
        )

        if not request.user.check_password(
            old_password
        ):

            return render(
                request,
                "insurance/change_password.html",
                {
                    "error":
                        "Current password is incorrect."
                }
            )

        if new_password != confirm_password:

            return render(
                request,
                "insurance/change_password.html",
                {
                    "error":
                        "New passwords do not match."
                }
            )

        if len(new_password) < 8:

            return render(
                request,
                "insurance/change_password.html",
                {
                    "error":
                        "Password must contain at least 8 characters."
                }
            )

        request.user.set_password(
            new_password
        )

        request.user.save()

        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect(
            "insurance_change_password"
        )

    return render(
        request,
        "insurance/change_password.html"
    )


@login_required
def insurance_notifications(request):

    company = get_logged_in_insurance_company(
        request
    )

    notifications = InsuranceClaim.objects.filter(
        insurance_company=company,
        claim_status="Pending"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "insurance/notifications.html",
        {
            "notifications": notifications
        }
    )


def insurance_logout(request):

    logout(request)

    return redirect(
        "home"
    )


# =========================================================
# BILLING LOGIN
# =========================================================


def billing_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            if user.groups.filter(
                name="Billing Staff"
            ).exists():

                login(
                    request,
                    user
                )

                return redirect(
                    "billing_dashboard"
                )

            return render(
                request,
                "billing/login.html",
                {
                    "error":
                        "You are not authorized as Billing Staff."
                }
            )

        return render(
            request,
            "billing/login.html",
            {
                "error":
                    "Invalid Username or Password"
            }
        )

    return render(
        request,
        "billing/login.html"
    )


# =========================================================
# BILLING DASHBOARD
# =========================================================


@login_required
def billing_dashboard(request):

    if not request.user.groups.filter(
        name="Billing Staff"
    ).exists():

        return HttpResponseForbidden(
            "You are not authorized to access Billing."
        )

    bills = Billing.objects.filter(
        billing_access_q(request.user)
    )

    total_bills = bills.count()

    paid = bills.filter(
        payment_status="Paid"
    ).count()

    pending = bills.filter(
        payment_status="Pending"
    ).count()

    recent_bills = bills.select_related(
        "medical_record",
        "medical_record__patient",
    ).order_by(
        "-bill_date"
    )[:5]

    return render(
        request,
        "billing/dashboard.html",
        {
            "total_bills": total_bills,
            "paid": paid,
            "pending": pending,
            "recent_bills": recent_bills,
        }
    )


# =========================================================
# BILLING LIST
# =========================================================


@login_required
def billing_list(request):

    if not request.user.groups.filter(
        name="Billing Staff"
    ).exists():

        return HttpResponseForbidden(
            "You are not authorized to access Billing."
        )

    bills = Billing.objects.filter(
        billing_access_q(request.user)
    ).select_related(
        "medical_record",
        "medical_record__patient",
    )

    query = request.GET.get(
        "q",
        ""
    ).strip()

    if query:

        bills = bills.filter(
            Q(
                bill_number__icontains=query
            )
            |
            Q(
                medical_record__patient__patient_id__icontains=query
            )
            |
            Q(
                medical_record__patient__first_name__icontains=query
            )
            |
            Q(
                medical_record__patient__last_name__icontains=query
            )
        )

    bills = bills.order_by(
        "-bill_date"
    )

    return render(
        request,
        "billing/billing_list.html",
        {
            "bills": bills,
            "query": query,
        }
    )


# =========================================================
# CREATE BILL
# =========================================================
@login_required
def create_bill(request):

    # Only Billing Staff can access this page
    if not request.user.groups.filter(
        name="Billing Staff"
    ).exists():

        return HttpResponseForbidden(
            "You are not authorized to create bills."
        )

    # --------------------------------------------------
    # Medical records accessible to this billing staff
    # --------------------------------------------------

    accessible_records = MedicalRecord.objects.filter(
        Q(
            patient__assigned_billing_staff=request.user
        )
        |
        Q(
            patient__assigned_billing_staff__isnull=True
        )
    ).select_related(
        "patient",
        "doctor"
    ).order_by(
        "-visit_date"
    )

    if request.method == "POST":

        form = BillingForm(
            request.POST
        )

        # Only accessible medical records
        form.fields[
            "medical_record"
        ].queryset = accessible_records

        if form.is_valid():

            bill = form.save(
                commit=False
            )

            patient = bill.medical_record.patient

            # --------------------------------------------------
            # Security check
            # --------------------------------------------------

            if (
                patient.assigned_billing_staff
                and
                patient.assigned_billing_staff != request.user
            ):

                return HttpResponseForbidden(
                    "This patient is not assigned to your billing department."
                )

            bill.save()

            messages.success(
                request,
                "Bill created successfully."
            )

            return redirect(
                "billing_list"
            )

    else:

        form = BillingForm()

        form.fields[
            "medical_record"
        ].queryset = accessible_records

    return render(
        request,
        "billing/create_bill.html",
        {
            "form": form,
            "medical_records": accessible_records,
        },
    )



# =========================================================
# EDIT BILL
# =========================================================


@login_required
def edit_bill(request, pk):

    if not request.user.groups.filter(
        name="Billing Staff"
    ).exists():

        return HttpResponseForbidden(
            "You are not authorized to edit bills."
        )

    bill = get_object_or_404(
        Billing,
        billing_access_q(request.user),
        pk=pk
    )

    if request.method == "POST":

        form = BillingForm(
            request.POST,
            instance=bill
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Bill updated successfully."
            )

            return redirect(
                "billing_list"
            )

    else:

        form = BillingForm(
            instance=bill
        )

    return render(
        request,
        "billing/edit_bill.html",
        {
            "form": form,
            "bill": bill,
        }
    )


# =========================================================
# DELETE BILL
# =========================================================


@login_required
def delete_bill(request, pk):

    if not request.user.groups.filter(
        name="Billing Staff"
    ).exists():

        return HttpResponseForbidden(
            "You are not authorized to delete bills."
        )

    bill = get_object_or_404(
        Billing.objects.filter(
         billing_access_q(request.user)
        ),
        pk=pk
    )

    if request.method == "POST":

        bill.delete()

        messages.success(
            request,
            "Bill deleted successfully."
        )

        return redirect(
            "billing_list"
        )

    return render(
        request,
        "billing/delete_bill.html",
        {
            "bill": bill,
        }
    )


# =========================================================
# BILLING PROFILE / LOGOUT
# =========================================================


@login_required
def billing_profile(request):

    return render(
        request,
        "billing/profile.html",
        {
            "user": request.user,
        }
    )


@login_required
def billing_logout(request):

    logout(request)

    return redirect(
        "home"
    )


# =========================================================
# BILL PDF
# =========================================================


@login_required
def download_bill(request, pk):

    bill = get_object_or_404(
        Billing,
        pk=pk
    )

    patient = bill.medical_record.patient
    medical_record = bill.medical_record

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="Bill_{bill.bill_number}.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=A4
    )

    width, height = A4

    # =====================================================
    # COLORS
    # =====================================================

    navy = HexColor("#0B203B")
    blue = HexColor("#0D6EFD")
    light_blue = HexColor("#EAF3FF")
    light_gray = HexColor("#F5F7FA")
    dark_gray = HexColor("#374151")
    gray = HexColor("#6B7280")
    green = HexColor("#198754")
    white = colors.white

    # =====================================================
    # BACKGROUND
    # =====================================================

    pdf.setFillColor(
        light_gray
    )

    pdf.rect(
        0,
        0,
        width,
        height,
        fill=1,
        stroke=0
    )

    margin = 35

    pdf.setFillColor(
        white
    )

    pdf.roundRect(
        margin,
        35,
        width - (margin * 2),
        height - 70,
        15,
        fill=1,
        stroke=0
    )

    # =====================================================
    # HEADER
    # =====================================================

    pdf.setFillColor(
        navy
    )

    pdf.roundRect(
        margin,
        height - 145,
        width - (margin * 2),
        100,
        12,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        blue
    )

    pdf.circle(
        75,
        height - 95,
        22,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        white
    )

    pdf.setFont(
        "Helvetica-Bold",
        18
    )

    pdf.drawCentredString(
        75,
        height - 101,
        "+"
    )

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawString(
        110,
        height - 88,
        "SECURE PATIENT SYSTEM"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        110,
        height - 108,
        "Secure Patient Data & Insurance Management System"
    )

    pdf.setFont(
        "Helvetica-Bold",
        15
    )

    pdf.drawRightString(
        width - 55,
        height - 88,
        "MEDICAL BILL"
    )

    # =====================================================
    # BILL INFORMATION
    # =====================================================

    y = height - 180

    pdf.setFillColor(
        dark_gray
    )

    pdf.setFont(
        "Helvetica-Bold",
        10
    )

    pdf.drawString(
        55,
        y,
        "BILL NUMBER"
    )

    pdf.drawString(
        230,
        y,
        "BILL DATE"
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        55,
        y - 18,
        str(bill.bill_number)
    )

    pdf.drawString(
        230,
        y - 18,
        str(bill.bill_date)
    )

    # =====================================================
    # PATIENT INFORMATION
    # =====================================================

    y -= 70

    pdf.setFillColor(
        light_blue
    )

    pdf.roundRect(
        55,
        y - 75,
        width - 110,
        75,
        8,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        navy
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        70,
        y - 22,
        "PATIENT INFORMATION"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.setFillColor(
        dark_gray
    )

    pdf.drawString(
        70,
        y - 43,
        f"Patient ID: {patient.patient_id}"
    )

    pdf.drawString(
        230,
        y - 43,
        f"Patient Name: {patient.first_name} {patient.last_name}"
    )

    pdf.drawString(
        70,
        y - 61,
        f"Phone: {patient.phone_number}"
    )

    # =====================================================
    # MEDICAL RECORD
    # =====================================================

    y -= 110

    pdf.setFillColor(
        navy
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        55,
        y,
        "MEDICAL RECORDS"
    )

    pdf.setStrokeColor(
        HexColor("#D9E2EC")
    )

    pdf.line(
        55,
        y - 7,
        width - 55,
        y - 7
    )

    department_name = getattr(
        medical_record,
        "department",
        None
    )

    if not department_name:

        department_name = getattr(
            medical_record,
            "department_name",
            None
        )

    diagnosis = getattr(
        medical_record,
        "diagnosis",
        None
    )

    symptoms = getattr(
        medical_record,
        "symptoms",
        None
    )

    visit_date = getattr(
        medical_record,
        "visit_date",
        None
    )

    if diagnosis and symptoms:

        diagnosis_symptoms = (
            f"Diagnosis: {diagnosis}; "
            f"Symptoms: {symptoms}"
        )

    elif diagnosis:

        diagnosis_symptoms = str(
            diagnosis
        )

    elif symptoms:

        diagnosis_symptoms = str(
            symptoms
        )

    else:

        diagnosis_symptoms = "N/A"

    table_y = y - 35

    pdf.setFillColor(
        HexColor("#EAF3FF")
    )

    pdf.roundRect(
        55,
        table_y - 5,
        width - 110,
        25,
        5,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        navy
    )

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawString(
        70,
        table_y + 3,
        "DEPARTMENT"
    )

    pdf.drawString(
        190,
        table_y + 3,
        "DIAGNOSIS / SYMPTOMS"
    )

    pdf.drawRightString(
        width - 70,
        table_y + 3,
        "VISIT DATE"
    )

    row_y = table_y - 28

    pdf.setFillColor(
        HexColor("#FAFBFC")
    )

    pdf.roundRect(
        55,
        row_y - 8,
        width - 110,
        30,
        5,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        dark_gray
    )

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawString(
        70,
        row_y + 2,
        str(
            department_name or "N/A"
        )[:18]
    )

    pdf.drawString(
        190,
        row_y + 2,
        str(
            diagnosis_symptoms
        )[:38]
    )

    pdf.drawRightString(
        width - 70,
        row_y + 2,
        str(
            visit_date or "N/A"
        )
    )

    y = row_y - 35

    # =====================================================
    # BILLING DETAILS
    # =====================================================

    pdf.setFillColor(
        navy
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        55,
        y,
        "BILLING DETAILS"
    )

    pdf.setStrokeColor(
        HexColor("#D9E2EC")
    )

    pdf.line(
        55,
        y - 7,
        width - 55,
        y - 7
    )

    table_y = y - 35

    pdf.setFillColor(
        HexColor("#F0F4F8")
    )

    pdf.rect(
        55,
        table_y - 5,
        width - 110,
        25,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        navy
    )

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawString(
        70,
        table_y + 3,
        "DESCRIPTION"
    )

    pdf.drawRightString(
        width - 70,
        table_y + 3,
        "AMOUNT"
    )

    items = [
        (
            "Consultation Fee",
            bill.consultation_fee
        ),
        (
            "Medicine Fee",
            bill.medicine_fee
        ),
        (
            "Laboratory Fee",
            bill.laboratory_fee
        ),
        (
            "Other Charges",
            bill.other_charges
        ),
    ]

    row_y = table_y - 28

    pdf.setFont(
        "Helvetica",
        10
    )

    for index, (name, amount) in enumerate(items):

        if index % 2 == 0:

            pdf.setFillColor(
                HexColor("#FAFBFC")
            )

            pdf.rect(
                55,
                row_y - 6,
                width - 110,
                24,
                fill=1,
                stroke=0
            )

        pdf.setFillColor(
            dark_gray
        )

        pdf.drawString(
            70,
            row_y + 2,
            name
        )

        pdf.drawRightString(
            width - 70,
            row_y + 2,
            f"Rs. {amount}"
        )

        row_y -= 25

    # =====================================================
    # TOTAL
    # =====================================================

    total_y = row_y - 5

    pdf.setFillColor(
        light_blue
    )

    pdf.roundRect(
        55,
        total_y - 30,
        width - 110,
        38,
        7,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        navy
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        70,
        total_y - 15,
        "TOTAL AMOUNT"
    )

    pdf.setFillColor(
        blue
    )

    pdf.drawRightString(
        width - 70,
        total_y - 15,
        f"Rs. {bill.total_amount}"
    )

    # =====================================================
    # PAYMENT INFORMATION
    # =====================================================

    payment_y = total_y - 65

    pdf.setFillColor(
        navy
    )

    pdf.setFont(
        "Helvetica-Bold",
        13
    )

    pdf.drawString(
        55,
        payment_y,
        "PAYMENT INFORMATION"
    )

    pdf.setStrokeColor(
        HexColor("#D9E2EC")
    )

    pdf.line(
        55,
        payment_y - 7,
        width - 55,
        payment_y - 7
    )

    box_y = payment_y - 58

    pdf.setFillColor(
        HexColor("#F8FAFC")
    )

    pdf.roundRect(
        55,
        box_y,
        width - 110,
        42,
        7,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(
        dark_gray
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        70,
        box_y + 25,
        f"Payment Method: {bill.payment_method}"
    )

    pdf.drawString(
        300,
        box_y + 25,
        f"Payment Status: {bill.payment_status}"
    )

    # =====================================================
    # FOOTER
    # =====================================================

    footer_y = 58

    pdf.setStrokeColor(
        HexColor("#D9E2EC")
    )

    pdf.line(
        55,
        footer_y + 20,
        width - 55,
        footer_y + 20
    )

    pdf.setFillColor(
        gray
    )

    pdf.setFont(
        "Helvetica",
        8
    )

    pdf.drawCentredString(
        width / 2,
        footer_y + 7,
        "This is a computer-generated medical bill."
    )

    pdf.drawCentredString(
        width / 2,
        footer_y - 7,
        "Secure Patient Data & Insurance Management System"
    )

    pdf.save()

    return response


# =========================================================
# DOCTOR LOGIN
# =========================================================


def doctor_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            if user.groups.filter(
                name="Doctor"
            ).exists():

                login(
                    request,
                    user
                )

                return redirect(
                    "doctor_dashboard"
                )

            return render(
                request,
                "doctor/login.html",
                {
                    "error":
                        "You are not authorized as Doctor."
                }
            )

        return render(
            request,
            "doctor/login.html",
            {
                "error":
                    "Invalid Username or Password"
            }
        )

    return render(
        request,
        "doctor/login.html"
    )


# =========================================================
# DOCTOR DASHBOARD
# =========================================================


@login_required
def doctor_dashboard(request):

    total_patients = MedicalRecord.objects.filter(
        doctor=request.user
    ).values(
        "patient"
    ).distinct().count()

    total_records = MedicalRecord.objects.filter(
        doctor=request.user
    ).count()

    today_visits = MedicalRecord.objects.filter(
        doctor=request.user,
        visit_date=date.today()
    ).count()

    recent_records = MedicalRecord.objects.filter(
        doctor=request.user
    ).order_by(
        "-visit_date"
    )[:5]

    return render(
        request,
        "doctor/dashboard.html",
        {
            "total_patients": total_patients,
            "total_records": total_records,
            "today_visits": today_visits,
            "recent_records": recent_records,
        }
    )


# =========================================================
# DOCTOR PATIENT LIST
# =========================================================


@login_required
def doctor_patients(request):

    search = request.GET.get(
        "search",
        ""
    ).strip()

    patients = Patient.objects.filter(
        status=True,
        assigned_doctor=request.user
    ).order_by(
        "-created_at"
    )

    if search:

        patients = patients.filter(
            Q(
                patient_id__icontains=search
            )
            |
            Q(
                first_name__icontains=search
            )
            |
            Q(
                last_name__icontains=search
            )
        )

    patients = patients.annotate(
        has_medical_record=Exists(
            MedicalRecord.objects.filter(
                patient=OuterRef("pk")
            )
        )
    )

    return render(
        request,
        "doctor/patients.html",
        {
            "patients": patients,
            "search": search,
        }
    )


# =========================================================
# DOCTOR ADD PATIENT
# =========================================================
#
# Doctor can select Billing Staff.
#
# If doctor selects Billing 1:
#     only Billing 1 can access.
#
# If doctor does NOT select billing:
#     all Billing Staff can access.
#
# =========================================================


@login_required
def doctor_add_patient(request):

    billing_staff = User.objects.filter(
        groups__name="Billing Staff",
        is_active=True
    ).distinct()

    if request.method == "POST":

        form = PatientForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            patient = form.save(
                commit=False
            )

            patient.assigned_doctor = (
                request.user
            )

            billing_id = request.POST.get(
                "assigned_billing_staff"
            )

            if billing_id:

                patient.assigned_billing_staff = (
                    get_object_or_404(
                        User,
                        id=billing_id,
                        groups__name="Billing Staff",
                        is_active=True
                    )
                )

            else:

                # No billing staff selected.
                # All Billing Staff can access.
                patient.assigned_billing_staff = None

            patient.save()

            messages.success(
                request,
                "Patient added successfully."
            )

            return redirect(
                "doctor_patients"
            )

    else:

        form = PatientForm()

    return render(
        request,
        "doctor/add_patient.html",
        {
            "form": form,
            "billing_staff": billing_staff,
        }
    )


# =========================================================
# DOCTOR PATIENT DETAIL
# =========================================================


@login_required
def doctor_patient_detail(request, pk):

    patient = get_object_or_404(
        Patient,
        pk=pk,
        status=True,
        assigned_doctor=request.user
    )

    records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by(
        "-visit_date"
    )

    return render(
        request,
        "doctor/patient_detail.html",
        {
            "patient": patient,
            "records": records,
        }
    )


# =========================================================
# ADD MEDICAL RECORD
# =========================================================


@login_required
def add_medical_record(request, patient_id):

    patient = get_object_or_404(
        Patient,
        pk=patient_id,
        status=True,
        assigned_doctor=request.user
    )

    if request.method == "POST":

        form = MedicalRecordForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            record = form.save(
                commit=False
            )

            # Patient automatically comes from URL.
            record.patient = patient

            # Doctor automatically comes from login.
            record.doctor = request.user

            record.doctor_name = (
                request.user.get_full_name()
                or request.user.username
            )

            record.save()

            messages.success(
                request,
                "Medical record added successfully."
            )

            return redirect(
                "doctor_patient_detail",
                pk=patient.pk
            )

    else:

        form = MedicalRecordForm(
            initial={
                "doctor_name":
                    request.user.get_full_name()
                    or request.user.username
            }
        )

    return render(
        request,
        "doctor/add_record.html",
        {
            "form": form,
            "patient": patient,
        }
    )


# =========================================================
# EDIT PATIENT
# =========================================================


@login_required
def edit_patient(request, pk):

    patient = get_object_or_404(
        Patient,
        pk=pk,
        status=True
    )

    is_hospital = request.user.is_staff

    is_doctor = request.user.groups.filter(
        name="Doctor"
    ).exists()

    is_billing = request.user.groups.filter(
        name="Billing Staff"
    ).exists()

    # Doctor can edit only assigned patients.
    if is_doctor and not is_hospital:

        if patient.assigned_doctor != request.user:

            return HttpResponseForbidden(
                "You are not authorized to edit this patient."
            )

    # Billing staff cannot edit patient information.
    if is_billing and not is_hospital:

        return HttpResponseForbidden(
            "Billing staff cannot edit patient information."
        )

    doctors = User.objects.filter(
        groups__name="Doctor",
        is_active=True
    ).distinct()

    billing_staff = User.objects.filter(
        groups__name="Billing Staff",
        is_active=True
    ).distinct()

    if request.method == "POST":

        form = PatientForm(
            request.POST,
            request.FILES,
            instance=patient
        )

        if form.is_valid():

            patient = form.save(
                commit=False
            )

            # Only Hospital Admin can change assignments.
            if is_hospital:

                doctor_id = request.POST.get(
                    "assigned_doctor"
                )

                billing_id = request.POST.get(
                    "assigned_billing_staff"
                )

                if doctor_id:

                    patient.assigned_doctor = (
                        get_object_or_404(
                            User,
                            id=doctor_id,
                            groups__name="Doctor",
                            is_active=True
                        )
                    )

                if billing_id:

                    patient.assigned_billing_staff = (
                        get_object_or_404(
                            User,
                            id=billing_id,
                            groups__name="Billing Staff",
                            is_active=True
                        )
                    )

                else:

                    # No billing staff = all billing staff
                    # can access.
                    patient.assigned_billing_staff = None

            patient.save()

            messages.success(
                request,
                "Patient information updated successfully."
            )

            if is_doctor:

                return redirect(
                    "doctor_patient_detail",
                    pk=patient.pk
                )

            return redirect(
                "hospital_patients"
            )

    else:

        form = PatientForm(
            instance=patient
        )

    return render(
        request,
        "hospital/edit_patient.html",
        {
            "form": form,
            "patient": patient,
            "doctors": doctors,
            "billing_staff": billing_staff,
        }
    )


# =========================================================
# EDIT MEDICAL RECORD
# =========================================================


@login_required
def edit_medical_record(request, pk):

    record = get_object_or_404(
        MedicalRecord,
        pk=pk,
        patient__assigned_doctor=request.user
    )

    if request.method == "POST":

        form = MedicalRecordForm(
            request.POST,
            request.FILES,
            instance=record
        )

        if form.is_valid():

            record = form.save(
                commit=False
            )

            record.doctor = request.user

            record.doctor_name = (
                request.user.get_full_name()
                or request.user.username
            )

            record.save()

            messages.success(
                request,
                "Medical record updated successfully."
            )

            return redirect(
                "doctor_patient_detail",
                pk=record.patient.id
            )

    else:

        form = MedicalRecordForm(
            instance=record
        )

    return render(
        request,
        "doctor/edit_record.html",
        {
            "form": form,
            "record": record,
        }
    )


# =========================================================
# DELETE MEDICAL RECORD
# =========================================================


@login_required
def delete_medical_record(request, pk):

    record = get_object_or_404(
        MedicalRecord,
        pk=pk,
        doctor=request.user
    )

    patient_id = record.patient.id

    record.delete()

    messages.success(
        request,
        "Record Deleted Successfully."
    )

    return redirect(
        "doctor_patient_detail",
        pk=patient_id
    )


# =========================================================
# DOCTOR OTHER PAGES
# =========================================================


@login_required
def doctor_appointments(request):

    appointments = MedicalRecord.objects.filter(
        doctor=request.user
    ).order_by(
        "-visit_date"
    )

    return render(
        request,
        "doctor/appointments.html",
        {
            "appointments": appointments,
        }
    )


@login_required
def doctor_reports(request):

    total_patients = MedicalRecord.objects.filter(
        doctor=request.user
    ).values(
        "patient"
    ).distinct().count()

    total_visits = MedicalRecord.objects.filter(
        doctor=request.user
    ).count()

    return render(
        request,
        "doctor/reports.html",
        {
            "total_patients": total_patients,
            "total_visits": total_visits,
        }
    )


@login_required
def doctor_records(request):

    records = MedicalRecord.objects.filter(
        doctor=request.user
    ).select_related(
        "patient"
    ).order_by(
        "-visit_date"
    )

    return render(
        request,
        "doctor/records.html",
        {
            "records": records,
        }
    )


@login_required
def doctor_prescriptions(request):

    records = MedicalRecord.objects.filter(
        doctor=request.user
    ).select_related(
        "patient"
    ).order_by(
        "-visit_date"
    )

    return render(
        request,
        "doctor/prescriptions.html",
        {
            "records": records,
        }
    )


@login_required
def doctor_change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect(
                "doctor_dashboard"
            )

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "doctor/change_password.html",
        {
            "form": form
        }
    )


@login_required
def doctor_logout(request):

    logout(request)

    return redirect(
        "home"
    )


@login_required
def doctor_profile(request):

    return render(
        request,
        "doctor/profile.html",
        {
            "doctor": request.user,
        }
    )


# =========================================================
# HOSPITAL / RECEPTION
# =========================================================


def hospital_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.is_staff:

                login(
                    request,
                    user
                )

                return redirect(
                    "hospital_dashboard"
                )

            messages.error(
                request,
                "You are not authorized as Hospital Admin."
            )

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "hospital/login.html"
    )


@login_required
def hospital_dashboard(request):

    patients = Patient.objects.all()

    total_patients = patients.count()

    active_patients = patients.filter(
        status=True
    ).count()

    inactive_patients = patients.filter(
        status=False
    ).count()

    recent_patients = patients.order_by(
        "-created_at"
    )[:5]

    return render(
        request,
        "hospital/dashboard.html",
        {
            "total_patients": total_patients,
            "active_patients": active_patients,
            "inactive_patients": inactive_patients,
            "recent_patients": recent_patients,
        }
    )


@login_required
def hospital_patients(request):

    patients = Patient.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "hospital/patients.html",
        {
            "patients": patients,
        }
    )


# =========================================================
# HOSPITAL ADD PATIENT
# =========================================================


@login_required
def hospital_add_patient(request):

    doctors = User.objects.filter(
        groups__name="Doctor",
        is_active=True
    ).distinct()

    billing_staff = User.objects.filter(
        groups__name="Billing Staff",
        is_active=True
    ).distinct()

    if request.method == "POST":

        form = PatientForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            patient = form.save(
                commit=False
            )

            doctor_id = request.POST.get(
                "assigned_doctor"
            )

            billing_id = request.POST.get(
                "assigned_billing_staff"
            )

            patient.assigned_doctor = (
                get_object_or_404(
                    User,
                    id=doctor_id,
                    groups__name="Doctor",
                    is_active=True
                )
            )

            patient.assigned_billing_staff = (
                get_object_or_404(
                    User,
                    id=billing_id,
                    groups__name="Billing Staff",
                    is_active=True
                )
            )

            patient.save()

            messages.success(
                request,
                "Patient registered and assigned successfully."
            )

            return redirect(
                "hospital_patients"
            )

    else:

        form = PatientForm()

    return render(
        request,
        "hospital/add_patient.html",
        {
            "form": form,
            "doctors": doctors,
            "billing_staff": billing_staff,
        }
    )


@login_required
def hospital_logout(request):

    logout(request)

    return redirect(
        "home"
    )

