from rest_framework import filters
from rest_framework import viewsets
from .serializers import PatientSerializer
from .pagination import PatientPagination
from rest_framework.permissions import IsAuthenticated
from .models import (
    Patient,
    MedicalRecord,
    Billing,
    InsuranceClaim,
)
from .serializers import (
    PatientSerializer,
    MedicalRecordSerializer,
    BillingSerializer,
)
from rest_framework.permissions import DjangoModelPermissions
from django.http import HttpResponse
from .pdf import generate_bill_pdf
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import InsuranceClaimForm
from .forms import (
    InsuranceClaimForm,
    PatientPasswordChangeForm,
    BillingForm,

)
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q, Sum
from datetime import date

from .forms import MedicalRecordForm

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [DjangoModelPermissions]

    # Search Fields
    search_fields = [
        'patient_id',
        'first_name',
        'last_name',
        'phone_number',
        'email',
    ]

    # Ordering Fields
    ordering_fields = [
        'patient_id',
        'first_name',
        'last_name',
        'created_at',
        'date_of_birth',
    ]

    # Default Ordering
    ordering = ['patient_id'] 

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

from rest_framework.decorators import api_view

@api_view(["GET"])
def download_bill(request, pk):

    bill = Billing.objects.get(pk=pk)

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{bill.bill_number}.pdf"'
    )

    generate_bill_pdf(response, bill)

    return response




def patient_login(request):

    if request.user.is_authenticated:
        return redirect("patient_dashboard")

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

            return redirect("patient_dashboard")

        else:

            return render(
                request,
                "patient/login.html",
                {
                    "error": "Invalid Username or Password"
                }
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
    ).order_by("-created_at")[:5]

    return render(
        request,
        "patient/dashboard.html",
        {
            "patient": patient,
            "medical_count": medical_count,
            "billing_count": billing_count,
            "claim_count": claim_count,
            "recent_records": recent_records,
        },
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
        },
    )

@login_required
def insurance_dashboard(request):

    return render(
        request,
        "patient/insurance_dashboard.html"
    )


@login_required
def my_insurance_claims(request):

    return render(
        request,
        "patient/my_claims.html"
    )

@login_required
def apply_insurance_claim(request):

    patient = get_object_or_404(
    Patient,
    user=request.user
)

    if request.method == "POST":

        form = InsuranceClaimForm(
            request.POST,
            request.FILES,
        )

        form.fields["bill"].queryset = Billing.objects.filter(
            medical_record__patient=patient
        )

        if form.is_valid():

            bill = form.cleaned_data["bill"]

            claim = form.save(commit=False)

            claim.patient = patient
            claim.bill = bill
            claim.medical_record = bill.medical_record

            claim.save()

            return redirect("patient_claims")

    else:

        form = InsuranceClaimForm()

        form.fields["bill"].queryset = Billing.objects.filter(
            medical_record__patient=patient
        )

    return render(
        request,
        "patient/apply_claim.html",
        {
            "form": form,
        },
    )

@login_required
def patient_logout(request):

    logout(request)

    return redirect("patient_login")


@login_required
def patient_medical_records(request):

    patient = get_object_or_404(
    Patient,
    user=request.user
)

    medical_records = MedicalRecord.objects.filter(
        patient=patient
    ).order_by("-visit_date")

    return render(
        request,
        "patient/medical_records.html",
        {
            "patient": patient,
            "medical_records": medical_records,
        },
    )

@login_required
def patient_billing(request):

    patient = get_object_or_404(
    Patient,
    user=request.user
)

    bills = Billing.objects.filter(
        medical_record__patient=patient
    ).order_by("-bill_date")

    total_amount = sum(
        bill.total_amount for bill in bills
    )

    paid_amount = sum(
        bill.total_amount
        for bill in bills
        if bill.payment_status == "Paid"
    )

    pending_amount = total_amount - paid_amount

    return render(
        request,
        "patient/billing.html",
        {
            "patient": patient,
            "bills": bills,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "pending_amount": pending_amount,
        },
    )

@login_required
def patient_claims(request):

    patient = get_object_or_404(
    Patient,
    user=request.user
)

    claims = InsuranceClaim.objects.filter(
        patient=patient
    ).order_by("-created_at")

    total_claims = claims.count()

    pending = claims.filter(
        claim_status="Pending"
    ).count()

    approved = claims.filter(
        claim_status="Approved"
    ).count()

    rejected = claims.filter(
        claim_status="Rejected"
    ).count()

    return render(
        request,
        "patient/claims.html",
        {
            "claims": claims,
            "total_claims": total_claims,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
        },
    )
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

            return redirect("patient_dashboard")

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



def insurance_login(request):

    if request.user.is_authenticated:
        return redirect("insurance_dashboard")

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

            return redirect("insurance_dashboard")

        return render(
            request,
            "insurance/login.html",
            {
                "error": "Invalid Username or Password"
            },
        )

    return render(
        request,
        "insurance/login.html"
    )
@login_required
def insurance_dashboard(request):

    company = request.user.insurance_company

    pending = InsuranceClaim.objects.filter(
        insurance_company=company,
        claim_status="Pending"
    ).count()

    review = InsuranceClaim.objects.filter(
        insurance_company=company,
        claim_status="Under Review"
    ).count()

    approved = InsuranceClaim.objects.filter(
        insurance_company=company,
        claim_status="Approved"
    ).count()

    rejected = InsuranceClaim.objects.filter(
        insurance_company=company,
        claim_status="Rejected"
    ).count()

    recent_claims = InsuranceClaim.objects.filter(
        insurance_company=company
    ).order_by("-created_at")[:5]

    notifications = InsuranceClaim.objects.filter(
        insurance_company=company,
        claim_status="Pending"
    ).order_by("-created_at")[:10]

    return render(
        request,
        "insurance/dashboard.html",
        {
            "pending": pending,
            "review": review,
            "approved": approved,
            "rejected": rejected,
            "recent_claims": recent_claims,
            "notifications": notifications,
        
        },
    )
@login_required
def insurance_logout(request):

    logout(request)

    return redirect("insurance_login")


@login_required
def insurance_claim_list(request):

    company = request.user.insurance_company

    claims = InsuranceClaim.objects.filter(
        insurance_company=company
    ).select_related(
        "patient",
        "bill",
        "medical_record"
    )

    search = request.GET.get("search")

    status = request.GET.get("status")

    if search:

        claims = claims.filter(

            Q(claim_id__icontains=search) |

            Q(patient__patient_id__icontains=search) |

            Q(patient__first_name__icontains=search)

        )

    if status:

        claims = claims.filter(

            claim_status=status

        )

    claims = claims.order_by("-created_at")

    return render(

        request,

        "insurance/claim_list.html",

        {

            "claims": claims,

            "search": search,

            "status": status,

        },

    )


@login_required
def insurance_claim_detail(request, pk):

    claim = get_object_or_404(
        InsuranceClaim,
        pk=pk
    )

    patient = claim.patient
    medical_record = claim.medical_record
    bill = claim.bill

    if request.method == "POST":

        claim.claim_status = request.POST.get("status")

        claim.approved_amount = request.POST.get(
            "approved_amount"
        )

        claim.remarks = request.POST.get(
            "remarks"
        )

        claim.verified_date = timezone.now()

        claim.save()

        return redirect("insurance_claim_list")

    return render(
        request,
        "insurance/claim_detail.html",
        {
            "claim": claim,
            "patient": patient,
            "medical_record": medical_record,
            "bill": bill,
        },
    )
@login_required
def insurance_profile(request):

    company = request.user.insurance_company

    total_claims = InsuranceClaim.objects.filter(
        insurance_company=company
    ).count()

    approved_amount = InsuranceClaim.objects.filter(
        insurance_company=company,
        claim_status="Approved"
    ).aggregate(
        Sum("approved_amount")
    )["approved_amount__sum"] or 0

    return render(
        request,
        "insurance/profile.html",
        {
            "company": company,
            "total_claims": total_claims,
            "approved_amount": approved_amount,
        },
    )
    
def billing_login(request):

     if request.user.is_authenticated:
        return redirect("billing_dashboard")

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

            return redirect("billing_dashboard")

        return render(
            request,
            "billing/login.html",
            {
                "error": "Invalid Username or Password"
            },
        )

     return render(
        request,
        "billing/login.html"
    )

@login_required
def billing_dashboard(request):

    total_bills = Billing.objects.count()

    paid = Billing.objects.filter(
        payment_status="Paid"
    ).count()

    pending = Billing.objects.filter(
        payment_status="Pending"
    ).count()

    recent_bills = Billing.objects.order_by(
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
        },
    )
@login_required
def billing_list(request):

    bills = Billing.objects.select_related(
        "medical_record",
        "medical_record__patient",
    )

    query = request.GET.get("q")

    if query:

        bills = bills.filter(
            Q(bill_number__icontains=query) |
            Q(medical_record__patient__patient_id__icontains=query)
        )

    bills = bills.order_by("-bill_date")

    return render(
        request,
        "billing/billing_list.html",
        {
            "bills": bills,
            "query": query,
        },
    )
@login_required
def edit_bill(request, pk):

    bill = get_object_or_404(
        Billing,
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

            return redirect("billing_list")

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
        },
    )
@login_required
def billing_logout(request):

    logout(request)

    return redirect("billing_login")

@login_required
def create_bill(request):

    if request.method == "POST":

        form = BillingForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Bill created successfully."
            )

            return redirect("billing_list")

    else:

        form = BillingForm()

    return render(
        request,
        "billing/create_bill.html",
        {
            "form": form,
        },
    )
@login_required
def delete_bill(request, pk):

    bill = get_object_or_404(
        Billing,
        pk=pk
    )

    if request.method == "POST":

        bill.delete()

        messages.success(
            request,
            "Bill deleted successfully."
        )

        return redirect("billing_list")

    return render(
        request,
        "billing/delete_bill.html",
        {
            "bill": bill,
        },
    )
@login_required
def billing_profile(request):

    return render(
        request,
        "billing/profile.html",
        {
            "user": request.user,
        },
    )
today = timezone.now()

monthly_revenue = Billing.objects.filter(
    bill_date__month=today.month,
    payment_status="Paid"
).aggregate(
    Sum("total_amount")
)["total_amount__sum"] or 0

today_revenue = Billing.objects.filter(
    bill_date=today.date(),
    payment_status="Paid"
).aggregate(
    Sum("total_amount")
)["total_amount__sum"] or 0

def doctor_login(request):

    if request.user.is_authenticated:
        return redirect("doctor_dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user:

            login(request, user)

            return redirect("doctor_dashboard")

        return render(
            request,
            "doctor/login.html",
            {
                "error": "Invalid Username or Password"
            },
        )

    return render(
        request,
        "doctor/login.html"
    )

@login_required
def doctor_dashboard(request):

    total_patients = MedicalRecord.objects.filter(
        doctor=request.user
    ).values("patient").distinct().count()

    total_records = MedicalRecord.objects.filter(
        doctor=request.user
    ).count()

    today_visits = MedicalRecord.objects.filter(
        doctor=request.user,
        visit_date=date.today()
    ).count()

    recent_records = MedicalRecord.objects.filter(
        doctor=request.user
    ).order_by("-visit_date")[:5]

    return render(
        request,
        "doctor/dashboard.html",
        {
            "total_patients": total_patients,
            "total_records": total_records,
            "today_visits": today_visits,
            "recent_records": recent_records,
        },
    )
@login_required
def doctor_patients(request):

    records = MedicalRecord.objects.filter(
        doctor=request.user
    ).select_related("patient")

    search = request.GET.get("search")

    if search:

        records = records.filter(

            Q(patient__patient_id__icontains=search) |

            Q(patient__first_name__icontains=search) |

            Q(patient__last_name__icontains=search)

        )

    return render(
        request,
        "doctor/patients.html",
        {
            "records": records,
            "search": search,
        },
    )
def doctor_logout(request):
    logout(request)
    return redirect("doctor_login")

@login_required
def doctor_profile(request):

    return render(
        request,
        "doctor/profile.html",
        {
            "doctor": request.user,
        },
    )
@login_required
def doctor_patient_detail(request, pk):

    patient = get_object_or_404(
        Patient,
        pk=pk
    )

    records = MedicalRecord.objects.filter(
        patient=patient,
        doctor=request.user
    )

    return render(
        request,
        "doctor/patient_detail.html",
        {
            "patient": patient,
            "records": records,
        },
    )
@login_required
def add_medical_record(request, patient_id):

    patient = get_object_or_404(
        Patient,
        pk=patient_id
    )

    if request.method == "POST":

        form = MedicalRecordForm(request.POST)

        if form.is_valid():

            record = form.save(commit=False)

            record.patient = patient
            record.doctor = request.user

            record.save()

            messages.success(
                request,
                "Medical Record Added Successfully."
            )

            return redirect(
                "doctor_patient_detail",
                pk=patient.id,
            )

    else:

        form = MedicalRecordForm()

    return render(
        request,
        "doctor/add_record.html",
        {
            "form": form,
            "patient": patient,
        },
    )
@login_required
def edit_medical_record(request, pk):

    record = get_object_or_404(
        MedicalRecord,
        pk=pk,
        doctor=request.user,
    )

    if request.method == "POST":

        form = MedicalRecordForm(
            request.POST,
            instance=record,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Record Updated Successfully."
            )

            return redirect(
                "doctor_patient_detail",
                pk=record.patient.id,
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
        },
    )

@login_required
def edit_medical_record(request, pk):

    record = get_object_or_404(
        MedicalRecord,
        pk=pk,
        doctor=request.user,
    )

    if request.method == "POST":

        form = MedicalRecordForm(
            request.POST,
            instance=record,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Record Updated Successfully."
            )

            return redirect(
                "doctor_patient_detail",
                pk=record.patient.id,
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
        },
    )
@login_required
def delete_medical_record(request, pk):

    record = get_object_or_404(
        MedicalRecord,
        pk=pk,
        doctor=request.user,
    )

    patient_id = record.patient.id

    record.delete()

    messages.success(
        request,
        "Record Deleted Successfully."
    )

    return redirect(
        "doctor_patient_detail",
        pk=patient_id,
    )
@login_required
def doctor_appointments(request):

    appointments = MedicalRecord.objects.filter(
        doctor=request.user
    ).order_by("-visit_date")

    return render(
        request,
        "doctor/appointments.html",
        {
            "appointments": appointments,
        },
    )
@login_required
def doctor_reports(request):

    total_patients = MedicalRecord.objects.filter(
        doctor=request.user
    ).values("patient").distinct().count()

    total_visits = MedicalRecord.objects.filter(
        doctor=request.user
    ).count()

    return render(
        request,
        "doctor/reports.html",
        {
            "total_patients": total_patients,
            "total_visits": total_visits,
        },
    )
@login_required
def doctor_records(request):

    records = MedicalRecord.objects.filter(
        doctor=request.user
    ).select_related("patient").order_by("-visit_date")

    return render(
        request,
        "doctor/records.html",
        {
            "records": records,
        },
    )