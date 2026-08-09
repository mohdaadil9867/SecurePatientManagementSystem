from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def generate_bill_pdf(response, bill):

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold",18)

    p.drawString(
        170,
        800,
        "Secure Patient Hospital"
    )

    p.setFont("Helvetica",12)

    p.drawString(50,760,f"Bill Number : {bill.bill_number}")

    p.drawString(
        50,
        740,
        f"Patient : {bill.medical_record.patient.first_name} {bill.medical_record.patient.last_name}"
    )

    p.drawString(
        50,
        720,
        f"Patient ID : {bill.medical_record.patient.patient_id}"
    )

    p.drawString(
        50,
        700,
        f"Doctor : {bill.medical_record.doctor_name}"
    )

    p.line(40,685,550,685)

    p.drawString(
        50,
        660,
        f"Consultation Fee : ₹ {bill.consultation_fee}"
    )

    p.drawString(
        50,
        640,
        f"Medicine Fee : ₹ {bill.medicine_fee}"
    )

    p.drawString(
        50,
        620,
        f"Laboratory Fee : ₹ {bill.laboratory_fee}"
    )

    p.drawString(
        50,
        600,
        f"Other Charges : ₹ {bill.other_charges}"
    )

    p.line(40,585,550,585)

    p.setFont(
        "Helvetica-Bold",
        14
    )

    p.drawString(
        50,
        560,
        f"TOTAL : ₹ {bill.total_amount}"
    )

    p.drawString(
        50,
        530,
        f"Payment Status : {bill.payment_status}"
    )

    p.drawString(
        50,
        510,
        f"Payment Method : {bill.payment_method}"
    )

    p.drawString(
        50,
        470,
        "Thank You For Visiting."
    )

    p.showPage()

    p.save()