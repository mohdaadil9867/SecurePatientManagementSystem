from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

from decimal import Decimal
import os


# ============================================================
# PAGE
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4


# ============================================================
# COLORS
# ============================================================

NAVY = colors.HexColor("#063B5C")
DARK_NAVY = colors.HexColor("#062D49")

TEAL = colors.HexColor("#009C95")
DARK_TEAL = colors.HexColor("#007C78")

GREEN = colors.HexColor("#16A085")
LIGHT_GREEN = colors.HexColor("#EAF8F5")

LIGHT_BLUE = colors.HexColor("#EEF7FC")
VERY_LIGHT = colors.HexColor("#F8FBFD")

TEXT = colors.HexColor("#17324D")
MUTED = colors.HexColor("#66788A")

BORDER = colors.HexColor("#C8DDE5")

WHITE = colors.white

RED = colors.HexColor("#D64545")
YELLOW = colors.HexColor("#F4B942")


# ============================================================
# FONT SETUP
# ============================================================

def register_fonts():

    font_paths = [

        (
            "DejaVuSans",
            "C:/Windows/Fonts/DejaVuSans.ttf",
            "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
        ),

        (
            "Arial",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ),

        (
            "LiberationSans",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ),

        (
            "DejaVuLinux",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
    ]

    for regular_name, regular_path, bold_path in font_paths:

        if os.path.exists(regular_path):

            try:

                pdfmetrics.registerFont(
                    TTFont(
                        regular_name,
                        regular_path
                    )
                )

                if os.path.exists(bold_path):

                    pdfmetrics.registerFont(
                        TTFont(
                            regular_name + "-Bold",
                            bold_path
                        )
                    )

                    return (
                        regular_name,
                        regular_name + "-Bold"
                    )

                return (
                    regular_name,
                    regular_name
                )

            except Exception:
                pass

    return (
        "Helvetica",
        "Helvetica-Bold"
    )


FONT, BOLD_FONT = register_fonts()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):

    if value is None:
        value = Decimal("0")

    return f"₹ {Decimal(value):,.2f}"


def draw_text(
    c,
    text,
    x,
    y,
    size=10,
    color=TEXT,
    font=FONT,
):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, str(text))


def draw_right_text(
    c,
    text,
    x,
    y,
    size=10,
    color=TEXT,
    font=FONT,
):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawRightString(x, y, str(text))


def draw_center_text(
    c,
    text,
    x,
    y,
    size=10,
    color=TEXT,
    font=FONT,
):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(x, y, str(text))


def draw_section_title(
    c,
    title,
    x,
    y,
    width,
    color=DARK_TEAL,
):

    # Ribbon

    c.setFillColor(color)

    c.roundRect(
        x,
        y - 2,
        width,
        25,
        6,
        fill=1,
        stroke=0
    )

    # Small white icon circle

    c.setFillColor(WHITE)

    c.circle(
        x + 15,
        y + 10,
        7,
        fill=1,
        stroke=0
    )

    # Title

    draw_text(
        c,
        title.upper(),
        x + 29,
        y + 5,
        size=10,
        color=WHITE,
        font=BOLD_FONT,
    )


def draw_info_card(
    c,
    x,
    y,
    width,
    height,
    icon_letter,
    title,
    value,
    second_title=None,
    second_value=None,
):

    # Card

    c.setFillColor(WHITE)

    c.setStrokeColor(BORDER)

    c.setLineWidth(0.8)

    c.roundRect(
        x,
        y,
        width,
        height,
        9,
        fill=1,
        stroke=1
    )

    # Icon

    icon_x = x + 25

    icon_y = y + height / 2

    c.setFillColor(NAVY)

    c.circle(
        icon_x,
        icon_y,
        16,
        fill=1,
        stroke=0
    )

    draw_center_text(
        c,
        icon_letter,
        icon_x,
        icon_y - 4,
        size=11,
        color=WHITE,
        font=BOLD_FONT,
    )

    # Text

    text_x = x + 50

    draw_text(
        c,
        title,
        text_x,
        y + height - 25,
        size=8,
        color=MUTED,
        font=BOLD_FONT,
    )

    draw_text(
        c,
        value,
        text_x,
        y + height - 43,
        size=13,
        color=TEAL,
        font=BOLD_FONT,
    )

    if second_title:

        draw_text(
            c,
            second_title,
            text_x,
            y + 21,
            size=7.5,
            color=MUTED,
            font=BOLD_FONT,
        )

        draw_text(
            c,
            second_value,
            text_x,
            y + 8,
            size=8.5,
            color=TEXT,
            font=FONT,
        )


def draw_field(
    c,
    label,
    value,
    x,
    y,
    value_color=TEXT,
):

    draw_text(
        c,
        label,
        x,
        y + 14,
        size=7.5,
        color=MUTED,
        font=BOLD_FONT,
    )

    draw_text(
        c,
        value,
        x,
        y,
        size=10,
        color=value_color,
        font=BOLD_FONT,
    )


def draw_footer_line(c):

    c.setStrokeColor(TEAL)

    c.setLineWidth(3)

    c.line(
        0,
        28,
        PAGE_WIDTH,
        28
    )


# ============================================================
# HEADER
# ============================================================

def draw_header(c):

    header_height = 115

    # White header background

    c.setFillColor(WHITE)

    c.rect(
        0,
        PAGE_HEIGHT - header_height,
        PAGE_WIDTH,
        header_height,
        fill=1,
        stroke=0
    )

    # Decorative dark-blue right block

    c.setFillColor(NAVY)

    points = [

        PAGE_WIDTH - 170,
        PAGE_HEIGHT,

        PAGE_WIDTH,
        PAGE_HEIGHT,

        PAGE_WIDTH,
        PAGE_HEIGHT - 82,

        PAGE_WIDTH - 135,
        PAGE_HEIGHT - 82,

    ]

    path = c.beginPath()

    path.moveTo(points[0], points[1])

    path.lineTo(points[2], points[3])

    path.lineTo(points[4], points[5])

    path.lineTo(points[6], points[7])

    path.close()

    c.drawPath(
        path,
        fill=1,
        stroke=0
    )

    # Logo shield

    logo_x = 65

    logo_y = PAGE_HEIGHT - 55

    c.setFillColor(DARK_TEAL)

    c.circle(
        logo_x,
        logo_y,
        26,
        fill=1,
        stroke=0
    )

    # Medical cross

    c.setFillColor(WHITE)

    c.rect(
        logo_x - 4,
        logo_y - 13,
        8,
        26,
        fill=1,
        stroke=0
    )

    c.rect(
        logo_x - 13,
        logo_y - 4,
        26,
        8,
        fill=1,
        stroke=0
    )

    # Brand

    draw_text(
        c,
        "SECURE PATIENT SYSTEM",
        105,
        PAGE_HEIGHT - 48,
        size=19,
        color=NAVY,
        font=BOLD_FONT,
    )

    draw_text(
        c,
        "Your Health, Our Priority",
        105,
        PAGE_HEIGHT - 68,
        size=9,
        color=MUTED,
        font=FONT,
    )

    # ECG line

    c.setStrokeColor(TEAL)

    c.setLineWidth(1.5)

    ecg_y = PAGE_HEIGHT - 66

    ecg = [
        (235, ecg_y),
        (255, ecg_y),
        (262, ecg_y + 8),
        (268, ecg_y - 8),
        (274, ecg_y + 16),
        (281, ecg_y - 5),
        (288, ecg_y),
        (315, ecg_y),
    ]

    for i in range(len(ecg) - 1):

        c.line(
            ecg[i][0],
            ecg[i][1],
            ecg[i + 1][0],
            ecg[i + 1][1]
        )

    # Medical Bill

    draw_center_text(
        c,
        "MEDICAL BILL",
        PAGE_WIDTH - 82,
        PAGE_HEIGHT - 55,
        size=17,
        color=WHITE,
        font=BOLD_FONT,
    )

    draw_center_text(
        c,
        "OFFICIAL INVOICE",
        PAGE_WIDTH - 82,
        PAGE_HEIGHT - 72,
        size=7,
        color=colors.HexColor("#B9E8E4"),
        font=BOLD_FONT,
    )

    # Header divider

    c.setFillColor(TEAL)

    c.rect(
        0,
        PAGE_HEIGHT - header_height,
        PAGE_WIDTH,
        3,
        fill=1,
        stroke=0
    )


# ============================================================
# PATIENT INFORMATION
# ============================================================

def draw_patient_section(
    c,
    patient,
    y,
):

    x = 40

    width = PAGE_WIDTH - 80

    height = 75

    # Background

    c.setFillColor(LIGHT_GREEN)

    c.setStrokeColor(colors.HexColor("#A8DCD6"))

    c.roundRect(
        x,
        y - height,
        width,
        height,
        8,
        fill=1,
        stroke=1
    )

    draw_section_title(
        c,
        "Patient Information",
        x,
        y - 2,
        150,
        TEAL
    )

    # Vertical separators

    c.setStrokeColor(colors.HexColor("#A8DCD6"))

    c.line(
        x + 180,
        y - 25,
        x + 180,
        y - 66
    )

    c.line(
        x + 360,
        y - 25,
        x + 360,
        y - 66
    )

    # Patient ID

    draw_field(
        c,
        "PATIENT ID",
        patient.patient_id or "N/A",
        x + 20,
        y - 49,
        TEAL
    )

    # Name

    full_name = (
        f"{patient.first_name} "
        f"{patient.last_name}"
    )

    draw_field(
        c,
        "PATIENT NAME",
        full_name,
        x + 205,
        y - 49,
        NAVY
    )

    # Phone

    draw_field(
        c,
        "PHONE",
        patient.phone_number or "N/A",
        x + 385,
        y - 49,
        TEAL
    )

    return y - height - 15


# ============================================================
# MEDICAL RECORD
# ============================================================

def draw_medical_section(
    c,
    medical_record,
    y,
):

    x = 40

    width = PAGE_WIDTH - 80

    height = 72

    c.setFillColor(LIGHT_BLUE)

    c.setStrokeColor(
        colors.HexColor("#B9D8E8")
    )

    c.roundRect(
        x,
        y - height,
        width,
        height,
        8,
        fill=1,
        stroke=1
    )

    draw_section_title(
        c,
        "Medical Record",
        x,
        y - 2,
        145,
        NAVY
    )

    # Doctor

    draw_field(
        c,
        "DOCTOR",
        medical_record.doctor_name or "N/A",
        x + 20,
        y - 48,
        NAVY
    )

    # Department

    draw_field(
        c,
        "DEPARTMENT",
        medical_record.department or "N/A",
        x + 190,
        y - 48,
        TEAL
    )

    # Visit date

    visit_date = (
        medical_record.visit_date.strftime("%d %b %Y")
        if medical_record.visit_date
        else "N/A"
    )

    draw_field(
        c,
        "VISIT DATE",
        visit_date,
        x + 385,
        y - 48,
        NAVY
    )

    return y - height - 15


# ============================================================
# BILLING TABLE
# ============================================================

def draw_billing_table(
    c,
    bill,
    y,
):

    x = 40

    width = PAGE_WIDTH - 80

    draw_section_title(
        c,
        "Billing Details",
        x,
        y,
        145,
        NAVY
    )

    table_y = y - 37

    # Header

    c.setFillColor(NAVY)

    c.roundRect(
        x,
        table_y - 24,
        width,
        25,
        5,
        fill=1,
        stroke=0
    )

    headers = [
        "#",
        "DESCRIPTION",
        "QTY",
        "UNIT PRICE",
        "AMOUNT",
    ]

    header_x = [
        x + 15,
        x + 65,
        x + 295,
        x + 365,
        x + 470,
    ]

    for i, header in enumerate(headers):

        draw_text(
            c,
            header,
            header_x[i],
            table_y - 16,
            size=7.5,
            color=WHITE,
            font=BOLD_FONT,
        )

    # Billing rows

    rows = [

        (
            "1",
            "Consultation Fee",
            bill.consultation_fee
        ),

        (
            "2",
            "Medicine / Pharmacy",
            bill.medicine_fee
        ),

        (
            "3",
            "Laboratory / Diagnostics",
            bill.laboratory_fee
        ),

        (
            "4",
            "Other Charges",
            bill.other_charges
        ),

    ]

    row_y = table_y - 48

    row_height = 29

    for number, description, amount in rows:

        # Row separator

        c.setStrokeColor(
            colors.HexColor("#D7E3E8")
        )

        c.setDash(
            2,
            2
        )

        c.line(
            x + 5,
            row_y - 8,
            x + width - 5,
            row_y - 8
        )

        c.setDash()

        draw_text(
            c,
            number,
            x + 17,
            row_y,
            size=9,
            color=MUTED,
            font=BOLD_FONT,
        )

        draw_text(
            c,
            description,
            x + 65,
            row_y,
            size=9,
            color=TEXT,
            font=FONT,
        )

        draw_text(
            c,
            "1",
            x + 300,
            row_y,
            size=9,
            color=TEXT,
            font=FONT,
        )

        draw_right_text(
            c,
            money(amount).replace("₹ ", ""),
            x + 435,
            row_y,
            size=9,
            color=TEXT,
            font=FONT,
        )

        draw_right_text(
            c,
            money(amount).replace("₹ ", ""),
            x + width - 15,
            row_y,
            size=9,
            color=TEXT,
            font=BOLD_FONT,
        )

        row_y -= row_height

    # Total box

    box_width = 245

    box_height = 92

    box_x = x + width - box_width

    box_y = row_y - box_height + 20

    c.setFillColor(
        colors.HexColor("#EDF8F6")
    )

    c.roundRect(
        box_x,
        box_y,
        box_width,
        box_height,
        8,
        fill=1,
        stroke=0
    )

    # Total labels

    draw_text(
        c,
        "Subtotal",
        box_x + 15,
        box_y + 65,
        size=8.5,
        color=MUTED,
        font=BOLD_FONT,
    )

    draw_right_text(
        c,
        money(bill.total_amount),
        box_x + box_width - 15,
        box_y + 65,
        size=9,
        color=TEXT,
        font=FONT,
    )

    draw_text(
        c,
        "Payment Method",
        box_x + 15,
        box_y + 45,
        size=8.5,
        color=MUTED,
        font=BOLD_FONT,
    )

    draw_right_text(
        c,
        bill.payment_method or "N/A",
        box_x + box_width - 15,
        box_y + 45,
        size=9,
        color=TEXT,
        font=FONT,
    )

    # Divider

    c.setStrokeColor(
        colors.HexColor("#9FCFC9")
    )

    c.setLineWidth(1)

    c.line(
        box_x + 15,
        box_y + 34,
        box_x + box_width - 15,
        box_y + 34
    )

    # Total amount

    draw_text(
        c,
        "TOTAL AMOUNT",
        box_x + 15,
        box_y + 12,
        size=9,
        color=NAVY,
        font=BOLD_FONT,
    )

    c.setFillColor(NAVY)

    c.roundRect(
        box_x + 125,
        box_y + 7,
        105,
        25,
        5,
        fill=1,
        stroke=0
    )

    draw_right_text(
        c,
        money(bill.total_amount),
        box_x + 220,
        box_y + 15,
        size=10,
        color=WHITE,
        font=BOLD_FONT,
    )

    return box_y - 25


# ============================================================
# FOOTER
# ============================================================

def draw_footer(
    c,
    bill,
):

    footer_height = 72

    footer_y = 0

    # Footer background

    c.setFillColor(DARK_NAVY)

    c.rect(
        0,
        footer_y,
        PAGE_WIDTH,
        footer_height,
        fill=1,
        stroke=0
    )

    # Hospital name

    draw_text(
        c,
        "SECURE PATIENT HOSPITAL",
        40,
        48,
        size=11,
        color=colors.HexColor("#62D6CD"),
        font=BOLD_FONT,
    )

    draw_text(
        c,
        "123 Health Street, Medical City",
        40,
        33,
        size=7.5,
        color=WHITE,
        font=FONT,
    )

    draw_text(
        c,
        "Contact: +91 9876543210",
        40,
        21,
        size=7.5,
        color=WHITE,
        font=FONT,
    )

    # Divider

    c.setStrokeColor(
        colors.HexColor("#3E667D")
    )

    c.line(
        215,
        15,
        215,
        58
    )

    # Notes

    draw_text(
        c,
        "IMPORTANT NOTES",
        235,
        48,
        size=8,
        color=WHITE,
        font=BOLD_FONT,
    )

    draw_text(
        c,
        "• Please keep this bill for your records.",
        235,
        34,
        size=7,
        color=colors.HexColor("#D8E7EF"),
        font=FONT,
    )

    draw_text(
        c,
        "• For billing queries, contact the billing department.",
        235,
        21,
        size=7,
        color=colors.HexColor("#D8E7EF"),
        font=FONT,
    )

    # Thank you circle

    seal_x = PAGE_WIDTH - 65

    seal_y = 37

    c.setStrokeColor(
        colors.HexColor("#65D5CB")
    )

    c.setLineWidth(2)

    c.circle(
        seal_x,
        seal_y,
        25,
        fill=0,
        stroke=1
    )

    draw_center_text(
        c,
        "THANK",
        seal_x,
        seal_y + 4,
        size=7,
        color=WHITE,
        font=BOLD_FONT,
    )

    draw_center_text(
        c,
        "YOU",
        seal_x,
        seal_y - 7,
        size=9,
        color=colors.HexColor("#65D5CB"),
        font=BOLD_FONT,
    )


# ============================================================
# MAIN PDF GENERATOR
# ============================================================

def generate_bill_pdf(response, bill):

    c = canvas.Canvas(
        response,
        pagesize=A4
    )

    c.setTitle(
        f"Medical Bill - {bill.bill_number}"
    )

    # ========================================================
    # HEADER
    # ========================================================

    draw_header(c)

    # ========================================================
    # BILL INFORMATION
    # ========================================================

    y = PAGE_HEIGHT - 135

    draw_info_card(
        c,
        40,
        y - 70,
        250,
        65,
        "#",
        "Bill Number",
        bill.bill_number or "N/A",
        "Bill Date",
        bill.bill_date.strftime("%d %b %Y")
        if bill.bill_date
        else "N/A",
    )

    draw_info_card(
        c,
        305,
        y - 70,
        PAGE_WIDTH - 345,
        65,
        "✓",
        "Payment Status",
        bill.payment_status.upper()
        if bill.payment_status
        else "PENDING",
        "Payment Method",
        bill.payment_method or "N/A",
    )

    y -= 95

    # ========================================================
    # PATIENT
    # ========================================================

    patient = bill.medical_record.patient

    y = draw_patient_section(
        c,
        patient,
        y
    )

    # ========================================================
    # MEDICAL RECORD
    # ========================================================

    medical_record = bill.medical_record

    y = draw_medical_section(
        c,
        medical_record,
        y
    )

    # ========================================================
    # BILLING DETAILS
    # ========================================================

    draw_billing_table(
        c,
        bill,
        y
    )

    # ========================================================
    # FOOTER
    # ========================================================

    draw_footer(
        c,
        bill
    )

    # ========================================================
    # FINISH
    # ========================================================

    c.showPage()

    c.save()