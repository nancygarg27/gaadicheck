import io
import datetime
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable

from sqlmodel import Session, select
from database import engine
from models import Vehicle, Loan, Challan
from anomaly import analyze
from trust_score import calculate_trust_score


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()
    if df_clean.index.name in ["reading_date", "date"]:
        df_clean = df_clean.reset_index()
    df_clean = df_clean.rename(columns={"date": "reading_date", "km": "distance_km"})
    df_clean["distance_km"] = df_clean["distance_km"].astype(int)
    return df_clean


def generate_odometer_chart(df: pd.DataFrame) -> io.BytesIO:
    """Generates Matplotlib timeline graph with Red 'X' markers on anomalies."""
    df_plot = normalize_df(df)
    fig, ax = plt.subplots(figsize=(6.5, 2.2), dpi=150)
    
    df_plot = df_plot.sort_values("reading_date").copy()
    df_plot["reading_date_str"] = df_plot["reading_date"].astype(str)

    ax.plot(df_plot["reading_date_str"], df_plot["distance_km"], marker='o', color='#2980B9', linewidth=2, label="Odometer Track")

    flag_mask = df_plot.get("is_rollback", False) | df_plot.get("is_flatline", False) | df_plot.get("is_jump", False)
    anomalies = df_plot[flag_mask]
    
    if not anomalies.empty:
        ax.scatter(
            anomalies["reading_date_str"], 
            anomalies["distance_km"], 
            color='#C0392B', 
            s=110, 
            zorder=5, 
            marker='x', 
            linewidths=2.5, 
            label="Anomaly Flagged"
        )

    ax.set_title("Odometer Mileage Progression (km)", fontsize=9, fontweight='bold', pad=6)
    ax.set_ylabel("Distance (km)", fontsize=8)
    ax.tick_params(axis='x', rotation=15, labelsize=7)
    ax.tick_params(axis='y', labelsize=7)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.legend(fontsize=7, loc="upper left")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def build_evidence_strings(df: pd.DataFrame) -> list[str]:
    """Generates detailed evidence messages with exact dates and differences."""
    evidence = []
    df_sorted = normalize_df(df).sort_values("reading_date").reset_index(drop=True)

    for i in range(1, len(df_sorted)):
        prev_row = df_sorted.iloc[i - 1]
        curr_row = df_sorted.iloc[i]

        if curr_row.get("is_rollback", False):
            diff = prev_row["distance_km"] - curr_row["distance_km"]
            evidence.append(
                f"<b>Rollback Flag:</b> On {curr_row['reading_date']} ({curr_row['source']}), meter showed "
                f"<b>{curr_row['distance_km']:,} km</b>. On {prev_row['reading_date']} ({prev_row['source']}), it showed "
                f"<b>{prev_row['distance_km']:,} km</b> (unexplained drop of <b>{diff:,} km</b>)."
            )
        elif curr_row.get("is_flatline", False):
            diff = curr_row["distance_km"] - prev_row["distance_km"]
            evidence.append(
                f"<b>Flatline Flag:</b> Meter gained only <b>{diff} km</b> between {prev_row['reading_date']} and "
                f"{curr_row['reading_date']} across multiple service cycles."
            )
        elif curr_row.get("is_jump", False):
            diff = curr_row["distance_km"] - prev_row["distance_km"]
            evidence.append(
                f"<b>Unusual Jump:</b> Meter increased by <b>{diff:,} km</b> between {prev_row['reading_date']} and "
                f"{curr_row['reading_date']}."
            )

    return evidence


def get_recommended_actions(status: str, reasons: list[str], has_active_loan: bool, has_unpaid_challan: bool) -> list[str]:
    """Generates actionable next steps for buyers."""
    actions = []
    reasons_str = " ".join(reasons).lower()

    if "rollback" in reasons_str or status == "Red":
        actions.append("<b>1. Pricing & Verification:</b> Do not purchase at the quoted price. Demand full service logs from the authorized brand dealership.")
    if "flatline" in reasons_str:
        actions.append("<b>2. Mechanical Audit:</b> Have a trusted mechanic physically inspect the instrument cluster and speedometer wiring for disconnection.")
    if has_active_loan:
        actions.append("<b>3. Hypothecation Removal:</b> Require the seller to provide a Bank NOC and confirm hypothecation removal on the RC before transferring funds.")
    if has_unpaid_challan:
        actions.append("<b>4. Pending Dues:</b> Ensure all outstanding traffic fines/challans are cleared prior to ownership transfer.")
    if not actions:
        actions.append("<b>1. General Inspection:</b> Vehicle history is clean. Conduct standard physical inspection and test drive before finalizing.")

    return actions


def build_report(vehicle_id: int) -> bytes:
    """Generates a complete, evidence-backed inspection PDF report."""
    with Session(engine) as session:
        vehicle = session.get(Vehicle, vehicle_id)
        loans = session.exec(select(Loan).where(Loan.vehicle_id == vehicle_id)).all()
        challans = session.exec(select(Challan).where(Challan.vehicle_id == vehicle_id)).all()

    df_raw = analyze(vehicle_id)
    df = normalize_df(df_raw)
    score, status, deductions = calculate_trust_score(vehicle_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1A252C'), fontName='Helvetica-Bold')
    section_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=11, leading=14, textColor=colors.HexColor('#2C3E50'), fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=4)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#2C3E50'))
    cell_bold = ParagraphStyle('CellBold', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#2C3E50'), fontName='Helvetica-Bold')
    cell_red = ParagraphStyle('CellRed', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor('#C0392B'), fontName='Helvetica-Bold')

    story = []

    verdict_map = {
        "Red": ("NOT RECOMMENDED FOR PURCHASE", "#C0392B"),
        "Yellow": ("PROCEED WITH CAUTION — VERIFY DOCUMENTS", "#D68910"),
        "Green": ("NO HIGH-RISK FLAGS DETECTED", "#27AE60")
    }
    verdict_text, verdict_color = verdict_map.get(status, ("AUDIT COMPLETE", "#2C3E50"))

    story.append(Paragraph("GaddiCheck — Vehicle History Audit Report", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>VERDICT: <font color='{verdict_color}'>{verdict_text}</font></b>", styles['Normal']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor(verdict_color), spaceAfter=10, spaceBefore=4))


    report_id = f"GC-{datetime.date.today().strftime('%Y%m%d')}-{vehicle.id:04d}"
    overview_data = [
        [Paragraph(f"<b>Vehicle:</b> {vehicle.company} {vehicle.model}", cell_style), Paragraph(f"<b>Year:</b> {vehicle.year}", cell_style)],
        [Paragraph(f"<b>Fuel Type:</b> {vehicle.fuel_type.capitalize()}", cell_style), Paragraph(f"<b>Registration Plate:</b> {vehicle.plate_number}", cell_style)],
        [Paragraph(f"<b>Trust Score:</b> <font color='{verdict_color}'><b>{score}/100 ({status})</b></font>", cell_style), Paragraph(f"<b>Report ID:</b> {report_id}", cell_style)]
    ]
    t_overview = Table(overview_data, colWidths=[260, 260])
    t_overview.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECF0F1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_overview)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Odometer Reading Progression Chart", section_style))
    chart_buf = generate_odometer_chart(df)
    story.append(Image(chart_buf, width=520, height=175))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Detailed Odometer Log & Mileage Delta", section_style))
    df_sorted = df.sort_values("reading_date").reset_index(drop=True)
    readings_table_data = [[
        Paragraph("<b>Date</b>", cell_bold), 
        Paragraph("<b>Odometer (km)</b>", cell_bold), 
        Paragraph("<b>Source</b>", cell_bold), 
        Paragraph("<b>Km Delta</b>", cell_bold), 
        Paragraph("<b>Status</b>", cell_bold)
    ]]

    flagged_row_indices = []
    for i in range(len(df_sorted)):
        row = df_sorted.iloc[i]
        is_flagged = row.get("is_rollback", False) or row.get("is_flatline", False) or row.get("is_jump", False)
        
        if i == 0:
            delta_str = "-"
        else:
            diff = row["distance_km"] - df_sorted.iloc[i - 1]["distance_km"]
            delta_str = f"+{diff:,} km" if diff >= 0 else f"{diff:,} km"

        flag_str = "<b>FLAGGED</b>" if is_flagged else "Clean"
        style_to_use = cell_red if is_flagged else cell_style

        readings_table_data.append([
            Paragraph(str(row["reading_date"]), style_to_use),
            Paragraph(f"{row['distance_km']:,} km", style_to_use),
            Paragraph(str(row["source"]).capitalize(), style_to_use),
            Paragraph(delta_str, style_to_use),
            Paragraph(flag_str, style_to_use)
        ])

        if is_flagged:
            flagged_row_indices.append(i + 1)

    t_readings = Table(readings_table_data, colWidths=[90, 100, 90, 110, 130])
    table_styles = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECF0F1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]
    for idx in flagged_row_indices:
        table_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#FADBD8')))
    
    t_readings.setStyle(TableStyle(table_styles))
    story.append(t_readings)
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Specific Evidence & Risk Analysis", section_style))
    evidence_list = build_evidence_strings(df)
    if not evidence_list:
        story.append(Paragraph("• No physical odometer tampering or mileage anomaly evidence detected.", cell_style))
    else:
        for item in evidence_list:
            story.append(Paragraph(f"• {item}", cell_style))
            story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Legal & Financial Debt Liabilities", section_style))
    debt_data = [[
        Paragraph("<b>Category</b>", cell_bold), 
        Paragraph("<b>Entity / Violation</b>", cell_bold), 
        Paragraph("<b>Amount</b>", cell_bold), 
        Paragraph("<b>Status</b>", cell_bold)
    ]]

    has_active_loan = False
    has_unpaid_challan = False

    for loan in loans:
        if loan.is_active:
            has_active_loan = True
        debt_data.append([
            Paragraph("Bank Hypothecation", cell_style),
            Paragraph(loan.bank_name, cell_style),
            Paragraph(f"₹{loan.loan_amount:,}" if getattr(loan, 'loan_amount', None) else "Active Loan", cell_style),
            Paragraph("<font color='#C0392B'><b>ACTIVE</b></font>" if loan.is_active else "CLOSED", cell_style)
        ])

    for ch in challans:
        if not ch.is_paid:
            has_unpaid_challan = True
        debt_data.append([
            Paragraph("Traffic Challan", cell_style),
            Paragraph(f"{ch.reason_of_challan} ({ch.challan_date})", cell_style),
            Paragraph(f"₹{ch.amount_of_fine:,}", cell_style),
            Paragraph("<font color='#C0392B'><b>UNPAID</b></font>" if not ch.is_paid else "PAID", cell_style)
        ])

    if len(debt_data) == 1:
        debt_data.append([Paragraph("Dues & Liabilities", cell_style), Paragraph("No active loans or unpaid fines recorded", cell_style), Paragraph("₹0", cell_style), Paragraph("CLEARED", cell_style)])

    t_debt = Table(debt_data, colWidths=[110, 190, 110, 110])
    t_debt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495E')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#BDC3C7')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#ECF0F1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_debt)
    story.append(Spacer(1, 8))

    story.append(Paragraph("5. Recommended Buyer Actions", section_style))
    recommended_actions = get_recommended_actions(status, deductions, has_active_loan, has_unpaid_challan)
    for act in recommended_actions:
        story.append(Paragraph(act, cell_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 10))

    footer_text = f"Report Date: {datetime.date.today().strftime('%d %b %Y')} | Report ID: {report_id} | Note: Data simulated for demonstration purposes by GaddiCheck Engine."
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#BDC3C7'), spaceAfter=4, spaceBefore=4))
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Italic'], fontSize=7, leading=9, textColor=colors.HexColor('#7F8C8D'), alignment=1)))

    doc.build(story)
    return buffer.getvalue()

