from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from .validators import (
    validate_name,
    validate_phone,
    validate_date_of_birth,
)
from .utils import generate_patient_id
from .managers import ActivePatientManager
from django.contrib.auth.models import User


class Patient(models.Model):

    patient_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        blank=True,
        null=True,
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="patient_profile",
    )

    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    first_name = models.CharField(
        max_length=100,
        validators=[validate_name],
    )

    last_name = models.CharField(
        max_length=100,
        validators=[validate_name],
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
    )

    date_of_birth = models.DateField(
        validators=[validate_date_of_birth],
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
    )

    phone_number = models.CharField(
        max_length=10,
        validators=[validate_phone],
    )

    email = models.EmailField(
        unique=True
    )

    address = models.TextField()

    profile_photo = models.ImageField(
    upload_to="patient_photos/",
    blank=True,
    null=True
)
    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"

    class Meta:
        permissions = [
            (
                "view_patient_details",
                "Can view patient details"
            ),
            (
                "edit_patient_details",
                "Can edit patient details"
            ),
            (
                "delete_patient_details",
                "Can delete patient details"
            ),
        ]

    objects = models.Manager()
    active_objects = ActivePatientManager()

    @property
    def age(self):

        from datetime import date

        today = date.today()

        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (
                    self.date_of_birth.month,
                    self.date_of_birth.day
                )
            )
        )

    def clean(self):

        super().clean()

        if (
            Patient.objects
            .exclude(pk=self.pk)
            .filter(email=self.email)
            .exists()
        ):
            raise ValidationError(
                {
                    "email": "Email already exists."
                }
            )

    def save(self, *args, **kwargs):

        # --------------------------------
        # 1. Save patient first
        # --------------------------------

        super().save(*args, **kwargs)

        # --------------------------------
        # 2. Generate Patient ID
        # --------------------------------

        if not self.patient_id:

            self.patient_id = f"PAT{self.pk:04d}"

            Patient.objects.filter(
                pk=self.pk
            ).update(
                patient_id=self.patient_id
            )

        # --------------------------------
        # 3. Create patient login account
        # --------------------------------

        if self.user_id is None:

            user = User.objects.create_user(
                username=self.patient_id,
                password="patient@123",
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
            )

            Patient.objects.filter(
                pk=self.pk
            ).update(
                user=user
            )

            # Keep current object updated
            self.user = user

        # --------------------------------
        # 4. Update existing patient user
        # --------------------------------

        else:

            user = self.user

            user.first_name = self.first_name
            user.last_name = self.last_name
            user.email = self.email

            user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "email",
                ]
            )

    def __str__(self):

        return (
            f"{self.patient_id} - "
            f"{self.first_name} "
            f"{self.last_name}"
        )
class MedicalRecord(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="medical_records"
    )
    doctor = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="medical_records",
    null=True,
    blank=True,
)

    doctor_name = models.CharField(
        max_length=100
    )

    department = models.CharField(
        max_length=100
    )

    diagnosis = models.TextField()

    symptoms = models.TextField()

    treatment = models.TextField()

    prescription = models.TextField()

    medical_report = models.FileField(
        upload_to="medical_reports/",
        blank=True,
        null=True
    )

    visit_date = models.DateField()

    next_visit = models.DateField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True
    )

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-visit_date"]

        permissions = [
            ("view_medical_record", "Can view medical records"),
            ("edit_medical_record", "Can edit medical records"),
            ("delete_medical_record", "Can delete medical records"),
        ]

    def clean(self):

        if self.next_visit:

            if self.next_visit < self.visit_date:

                raise ValidationError(
                    "Next visit date cannot be earlier than visit date."
                )

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.patient.patient_id} | {self.visit_date} | {self.department}"

class Billing(models.Model):

    bill_number = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        blank=True,
        null=True
    )

    PAYMENT_STATUS = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
    ]

    PAYMENT_METHOD = [
        ("Cash", "Cash"),
        ("Card", "Card"),
        ("UPI", "UPI"),
    ]

    medical_record = models.OneToOneField(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="bill"
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    medicine_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    laboratory_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    other_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="Pending"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        default="Cash"
    )

    bill_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-bill_date"]

        permissions = [
            ("view_bill", "Can view bills"),
            ("edit_bill", "Can edit bills"),
            ("download_bill", "Can download bills"),
        ]

    def clean(self):

        fees = [
            self.consultation_fee,
            self.medicine_fee,
            self.laboratory_fee,
            self.other_charges,
        ]

        for fee in fees:

            if fee < 0:

                raise ValidationError(
                    "Charges cannot be negative."
                )

    def save(self, *args, **kwargs):

        self.full_clean()

        self.total_amount = (
            self.consultation_fee
            + self.medicine_fee
            + self.laboratory_fee
            + self.other_charges
        )

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new:

            self.bill_number = f"BILL{self.pk:04d}"

            Billing.objects.filter(
                pk=self.pk
            ).update(
                bill_number=self.bill_number
            )

            self.bill_number = f"BILL{self.pk:04d}"

    def __str__(self):

        return self.bill_number


class InsuranceCompany(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="insurance_company"
    )

    company_name = models.CharField(
        max_length=100,
        unique=True
    )

    registration_number = models.CharField(
        max_length=50,
        unique=True
    )

    contact_person = models.CharField(
        max_length=100
    )

    phone_number = models.CharField(
        max_length=10,
        validators=[validate_phone]
    )

    email = models.EmailField(
        unique=True
    )

    address = models.TextField()

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["company_name"]

        permissions = [
            ("view_company", "Can view insurance company"),
            ("edit_company", "Can edit insurance company"),
            ("verify_claim", "Can verify insurance claim"),
            ("approve_claim", "Can approve insurance claim"),
            ("reject_claim", "Can reject insurance claim"),
        ]

    def save(self, *args, **kwargs):

        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new and self.user is None:

            username = self.company_name

            if not User.objects.filter(username=username).exists():

                user = User.objects.create_user(
                    username=username,
                    password="insurance@123",
                    first_name=self.company_name,
                    email=self.email,
                )

                self.user = user

                InsuranceCompany.objects.filter(
                    pk=self.pk
                ).update(user=user)

        elif self.user:

            self.user.first_name = self.company_name
            self.user.email = self.email
            self.user.save()

    def __str__(self):
        return self.company_name

class InsuranceClaim(models.Model):

    CLAIM_STATUS = [
        ("Pending", "Pending"),
        ("Under Review", "Under Review"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="insurance_claims"
    )

    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="insurance_claims"
    )

    bill = models.OneToOneField(
        Billing,
        on_delete=models.CASCADE,
        related_name="insurance_claim"
    )

    insurance_company = models.ForeignKey(
        InsuranceCompany,
        on_delete=models.CASCADE,
        related_name="insurance_claims"
    )

    claim_id = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        blank=True,
        null=True
    )

    policy_number = models.CharField(
        max_length=50
    )

    claim_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    reason = models.TextField()

    remarks = models.TextField(
        blank=True
    )

    supporting_document = models.FileField(
        upload_to="insurance_documents/",
        blank=True,
        null=True
    )

    claim_status = models.CharField(
        max_length=20,
        choices=CLAIM_STATUS,
        default="Pending"
    )

    applied_date = models.DateField(
        default=timezone.now
    )

    verified_date = models.DateField(
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-created_at"]

        permissions = [
            ("verify_claim", "Can verify insurance claim"),
            ("approve_claim", "Can approve insurance claim"),
            ("reject_claim", "Can reject insurance claim"),
        ]

    def clean(self):

        if self.bill_id and self.claim_amount:

            if self.claim_amount > self.bill.total_amount:

                raise ValidationError(
                    "Claim amount cannot exceed total bill amount."
                )

        if (
            self.claim_amount
            and self.approved_amount
            and self.approved_amount > self.claim_amount
        ):

            raise ValidationError(
                "Approved amount cannot exceed claim amount."
            )

        if self.medical_record_id and self.patient_id:

            if self.medical_record.patient != self.patient:

                raise ValidationError(
                    "Medical Record does not belong to this patient."
                )

        if self.bill_id and self.patient_id:

            if self.bill.medical_record.patient != self.patient:

                raise ValidationError(
                    "Bill does not belong to this patient."
                )

    def save(self, *args, **kwargs):

        self.full_clean()

        is_new = self.pk is None

        if (
            self.claim_status in ["Approved", "Rejected"]
            and self.verified_date is None
        ):
            self.verified_date = timezone.now().date()

        super().save(*args, **kwargs)

        if is_new:
         self.claim_id = f"CLM{self.pk:04d}"

         InsuranceClaim.objects.filter(
           pk=self.pk
         ).update(
             claim_id=self.claim_id
         )

         self.claim_id = f"CLM{self.pk:04d}"

            
    def __str__(self):
      return self.claim_id or f"Insurance Claim #{self.pk}"