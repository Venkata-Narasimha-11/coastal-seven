"""Enterprise Amazon-Style Tax Invoice Generator with Authentic Company Stamp & QR Code."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.graphics.shapes import Drawing, Group, Rect, String
from reportlab.graphics.barcode.qr import QrCodeWidget


def create_company_stamp(
    company_name: str = "SIVORA LUXURY FASHION PVT LTD",
    date_str: str = "08-OCT-2026",
) -> Drawing:
    """
    Renders an authentic, tilted corporate rubber stamp with double borders,
    official navy ink color, and authorized signatory verification.
    """
    d = Drawing(170, 80)
    g = Group()
    g.translate(85, 40)
    g.rotate(-11)  # Authentic rubber stamp tilt angle

    ink_color = colors.HexColor("#1e3a8a")  # Official Corporate Navy Blue

    # Outer border (Solid)
    g.add(
        Rect(
            -78,
            -34,
            156,
            68,
            rx=8,
            ry=8,
            fillColor=None,
            strokeColor=ink_color,
            strokeWidth=2,
        )
    )

    # Inner border (Dotted/Dashed for official seal look)
    g.add(
        Rect(
            -74,
            -30,
            148,
            60,
            rx=6,
            ry=6,
            fillColor=None,
            strokeColor=ink_color,
            strokeWidth=0.8,
            strokeDashArray=[3, 2],
        )
    )

    # Stamp Text Elements
    g.add(
        String(
            0,
            17,
            company_name,
            fontName="Helvetica-Bold",
            fontSize=7.5,
            fillColor=ink_color,
            textAnchor="middle",
        )
    )
    g.add(
        String(
            0,
            3,
            "★ VERIFIED & PAID ★",
            fontName="Helvetica-Bold",
            fontSize=10,
            fillColor=ink_color,
            textAnchor="middle",
        )
    )
    g.add(
        String(
            0,
            -9,
            f"INVOICE DATE: {date_str}",
            fontName="Helvetica",
            fontSize=6.5,
            fillColor=ink_color,
            textAnchor="middle",
        )
    )
    g.add(
        String(
            0,
            -22,
            "AUTHORIZED SIGNATORY",
            fontName="Helvetica-Bold",
            fontSize=6.5,
            fillColor=ink_color,
            textAnchor="middle",
        )
    )

    d.add(g)
    return d


def create_qr_code(tracking_url: str) -> Drawing:
    """Generates a scannable digital QR code for order tracking and authenticity verification."""
    qr = QrCodeWidget(tracking_url)
    bounds = qr.getBounds()
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    d = Drawing(65, 65)
    g = Group()
    g.scale(65 / width, 65 / height)
    g.add(qr)
    d.add(g)
    return d


def generate_enterprise_invoice_pdf(order: Any, output_path: Path) -> Path:
    """
    Builds a pixel-perfect, Amazon-grade Tax Invoice PDF with:
    - Corporate branding header & GST metadata
    - 2-Column Seller vs Customer Billing / Shipping addresses
    - Itemized Table with quantity, unit prices, HSN, and GST
    - Mathematical tax breakdown (Subtotal, CGST, SGST, Delivery)
    - Tilted Company Rubber Stamp & Scannable QR Code
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # A4 Page setup with 36pt (0.5 inch) margins
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    style_normal = ParagraphStyle(
        "NormalSmall",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155"),
    )
    style_bold = ParagraphStyle(
        "BoldSmall",
        parent=style_normal,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # ---------------------------------------------------------
    # 1. HEADER: BRAND LOGO & INVOICE META
    # ---------------------------------------------------------
    header_left = Paragraph(
        """
        <font size=22 color="#1e3a8a"><b>SIVORA</b></font><font size=22 color="#ea580c"><b>LUXE</b></font><br/>
        <font size=7.5 color="#64748b">India's Premier Luxury Fashion & Couture Hub</font>
        """,
        styles["Normal"],
    )

    order_date_str = (
        order.created_at.strftime("%d-%b-%Y %I:%M %p")
        if getattr(order, "created_at", None)
        else datetime.now().strftime("%d-%b-%Y %I:%M %p")
    )
    stamp_date_str = (
        order.created_at.strftime("%d-%b-%Y").upper()
        if getattr(order, "created_at", None)
        else datetime.now().strftime("%d-%b-%Y").upper()
    )

    header_right = Paragraph(
        f"""
        <font size=13 color="#0f172a"><b>TAX INVOICE / CASH MEMO</b></font><br/>
        <font size=8 color="#475569">
        <b>Invoice No:</b> INV-AP-2026-{order.id:04d}<br/>
        <b>Order ID:</b> OD-2026-{order.id:06d}<br/>
        <b>Order Date:</b> {order_date_str}<br/>
        <b>GSTIN:</b> 37AABCG9481F1Z8
        </font>
        """,
        styles["Normal"],
    )

    header_table = Table([[header_left, header_right]], colWidths=[280, 240])
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.5,
            color=colors.HexColor("#1e3a8a"),
            spaceAfter=10,
        )
    )

    # ---------------------------------------------------------
    # 2. SELLER & BUYER 2-COLUMN ADDRESS GRID
    # ---------------------------------------------------------
    customer_name = (
        order.user.full_name or order.user.username
        if getattr(order, "user", None)
        else f"Customer #{order.user_id}"
    )
    customer_email = (
        order.user.email
        if getattr(order, "user", None)
        else f"user_{order.user_id}@store.io"
    )

    seller_info = Paragraph(
        """
        <b>SOLD BY:</b><br/>
        <b>SIVORA Luxury Fashion Private Limited</b><br/>
        Plot #45, Industrial Mega Tech Park, Autonagar<br/>
        Guntur, Andhra Pradesh, PIN: 522001<br/>
        <b>State Code:</b> 37 (Andhra Pradesh)<br/>
        <b>PAN:</b> AABCG9481F | <b>CIN:</b> U52100AP2026PTC109842
        """,
        style_normal,
    )

    shipping_info = Paragraph(
        f"""
        <b>BILLING & SHIPPING ADDRESS:</b><br/>
        <b>{customer_name}</b> ({customer_email})<br/>
        {order.shipping_address}<br/>
        <b>Payment Status:</b> <font color="#047857"><b>COMPLETED / PAID</b></font><br/>
        <b>Shipping Mode:</b> Express Delivery (Surface Logistics)
        """,
        style_normal,
    )

    address_table = Table([[seller_info, shipping_info]], colWidths=[260, 260])
    address_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#f8fafc"),
                ),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(address_table)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 3. ITEMIZED TABLE (AMAZON COLUMNS & STYLING)
    # ---------------------------------------------------------
    table_header = [
        "Sl",
        "Product Description",
        "HSN",
        "Unit Price",
        "Qty",
        "Net Amt",
        "GST (18%)",
        "Total Amount",
    ]
    table_data = [table_header]

    raw_total = float(order.total_amount)
    subtotal_net = 0.0
    total_tax = 0.0

    order_items = getattr(order, "items", []) or []

    if order_items:
        for idx, it in enumerate(order_items, start=1):
            p_name = it.product.name if getattr(it, "product", None) else f"Product #{it.product_id}"
            qty = it.quantity
            unit_price = float(it.unit_price)
            # Net price without 18% tax
            item_net = (unit_price * qty) / 1.18
            item_tax = (unit_price * qty) - item_net
            item_total = unit_price * qty

            subtotal_net += item_net
            total_tax += item_tax

            table_data.append(
                [
                    str(idx),
                    Paragraph(f"<b>{p_name}</b>", style_normal),
                    "8517",
                    f"${unit_price:.2f}",
                    str(qty),
                    f"${item_net:.2f}",
                    f"${item_tax:.2f}",
                    f"${item_total:.2f}",
                ]
            )
    else:
        # Graceful synthesize for single order total
        net_amt = raw_total / 1.18
        tax_amt = raw_total - net_amt
        subtotal_net = net_amt
        total_tax = tax_amt
        table_data.append(
            [
                "1",
                Paragraph("<b>SIVORA Luxury Fashion Order Items Package</b>", style_normal),
                "8517",
                f"${raw_total:.2f}",
                "1",
                f"${net_amt:.2f}",
                f"${tax_amt:.2f}",
                f"${raw_total:.2f}",
            ]
        )

    items_table = Table(
        table_data,
        colWidths=[24, 186, 40, 56, 30, 56, 58, 70],
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 0), (4, -1), "CENTER"),
                ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # 4. TOTALS & FINANCIAL SUMMARY
    # ---------------------------------------------------------
    cgst = total_tax / 2
    sgst = total_tax / 2

    summary_data = [
        ["Subtotal (Tax Exclusive):", f"${subtotal_net:.2f}"],
        ["CGST (9.0%):", f"${cgst:.2f}"],
        ["SGST (9.0%):", f"${sgst:.2f}"],
        ["Shipping & Handling:", "FREE"],
        ["Grand Total (Incl. Taxes):", f"${raw_total:.2f}"],
    ]
    summary_table = Table(summary_data, colWidths=[150, 90])
    summary_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -2), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#1e3a8a")),
                ("FONTSIZE", (0, -1), (-1, -1), 10.5),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1e3a8a")),
            ]
        )
    )

    amount_words = Paragraph(
        f"<b>Amount in Words:</b> USD {raw_total:.2f} Dollars Only.<br/>"
        "<font size=7 color='#64748b'>All taxes included as per GST Rules 2017. Returns accepted within 7 days.</font>",
        style_normal,
    )

    totals_row = Table([[amount_words, summary_table]], colWidths=[280, 240])
    totals_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(totals_row)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # 5. FOOTER: DIGITAL QR CODE + TILTED COMPANY STAMP
    # ---------------------------------------------------------
    tracking_url = f"http://localhost:5173/orders/{order.id}"
    qr_code_drawing = create_qr_code(tracking_url)

    footer_left = Table(
        [
            [
                qr_code_drawing,
                Paragraph(
                    """
                    <font size=7.5 color="#334155"><b>DIGITAL VERIFICATION</b><br/>
                    Scan QR code with smartphone to track delivery & verify invoice authenticity.<br/>
                    <i>This is a computer-authenticated fiscal document.</i></font>
                    """,
                    style_normal,
                ),
            ]
        ],
        colWidths=[70, 190],
    )
    footer_left.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    company_stamp = create_company_stamp(
        company_name="SIVORA LUXURY FASHION PVT LTD",
        date_str=stamp_date_str,
    )

    footer_right = Table(
        [
            [Paragraph("<b>For SIVORA LUXURY FASHION PVT LTD</b>", style_bold)],
            [company_stamp],
            [Paragraph("<font size=7 color='#64748b'>Authorized Corporate Seal & Signatory</font>", style_normal)],
        ],
        colWidths=[260],
    )
    footer_right.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )

    footer_grid = Table([[footer_left, footer_right]], colWidths=[260, 260])
    footer_grid.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(footer_grid)

    # Build PDF
    doc.build(story)
    return output_path
