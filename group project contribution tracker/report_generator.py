from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

from reportlab.platypus.flowables import HRFlowable

from datetime import datetime


def generate_pdf(
    project_title,
    guide,
    members,
    contributions,
    percentages,
    total,
    pdf_output="AI_Contribution_Report.pdf",
    college_name="",
    department=""
):

    # =====================================================
    # PDF FILE
    # =====================================================

    doc = SimpleDocTemplate(
        pdf_output,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    elements = []

    # =====================================================
    # COLLEGE NAME
    # =====================================================

    college_name_para = Paragraph(
        f"<font size=18><b>{college_name}</b></font>",
        styles['Title']
    )

    elements.append(college_name_para)

    # =====================================================
    # DEPARTMENT
    # =====================================================

    department_para = Paragraph(
        f"<font size=14><b>{department}</b></font>",
        styles['Heading2']
    )

    elements.append(department_para)

    elements.append(Spacer(1, 15))

    # =====================================================
    # PROJECT TITLE
    # =====================================================

    project_heading = Paragraph(
        f"<font size=20><b>{project_title}</b></font>",
        styles['Title']
    )

    elements.append(project_heading)

    elements.append(Spacer(1, 10))

    line = HRFlowable(
        width="100%",
        thickness=1,
        color=colors.black
    )

    elements.append(line)

    elements.append(Spacer(1, 20))

    # =====================================================
    # GUIDE DETAILS
    # =====================================================

    guide_heading = Paragraph(
        "<font size=14><b>GUIDE DETAILS</b></font>",
        styles['Heading2']
    )

    elements.append(guide_heading)

    elements.append(Spacer(1, 10))

    guide_data = [
        ["Guide Name", guide],
        ["Department", department],
        ["Academic Year", "2025-2026"]
    ]

    guide_table = Table(
        guide_data,
        colWidths=[220, 280]
    )

    guide_table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),

        ('FONTSIZE', (0, 0), (-1, -1), 11),

        ('BOTTOMPADDING', (0, 0), (-1, -1), 8)

    ]))

    elements.append(guide_table)

    elements.append(Spacer(1, 20))

    # =====================================================
    # CONTRIBUTION TABLE
    # =====================================================

    heading = Paragraph(
        "<font size=14><b>CONTRIBUTION TABLE</b></font>",
        styles['Heading2']
    )

    elements.append(heading)

    elements.append(Spacer(1, 10))

    table_data = [[
        "Member Name",
        "PRN",
        "Role",
        "Contribution %",
        "Score"
    ]]

    # =====================================================
    # ADD MEMBERS
    # =====================================================

    for member in members:

        name = member["name"]

        prn = member["prn"]

        role = member["role"]

        score = contributions.get(name, 0)

        percent = percentages.get(name, 0)

        table_data.append([
            name,
            prn,
            role,
            str(percent) + "%",
            str(score)
        ])

    # =====================================================
    # CREATE TABLE
    # =====================================================

    contribution_table = Table(
        table_data,
        colWidths=[130, 130, 100, 80, 80]
    )

    contribution_table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),

        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

        ('FONTSIZE', (0, 0), (-1, -1), 10),

        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER')

    ]))

    elements.append(contribution_table)

    elements.append(Spacer(1, 20))

    # =====================================================
    # AI ANALYSIS
    # =====================================================

    analysis_heading = Paragraph(
        "<font size=14><b>AI ANALYSIS</b></font>",
        styles['Heading2']
    )

    elements.append(analysis_heading)

    elements.append(Spacer(1, 10))

    analysis_text = """
    This report is generated using an AI-powered contribution
    tracking system. Contribution percentages are calculated
    using uploaded files, source code, reports,
    documents, and project activities.
    """

    analysis_para = Paragraph(
        analysis_text,
        styles['BodyText']
    )

    elements.append(analysis_para)

    elements.append(Spacer(1, 20))

    # =====================================================
    # PIE CHART
    # =====================================================

    graph_heading = Paragraph(
        "<font size=14><b>CONTRIBUTION GRAPH</b></font>",
        styles['Heading2']
    )

    elements.append(graph_heading)

    elements.append(Spacer(1, 10))

    drawing = Drawing(400, 200)

    pie = Pie()

    pie.x = 150
    pie.y = 15

    pie.width = 150
    pie.height = 150

    pie.data = [
        percentages.get(member["name"], 0)
        for member in members
    ]

    pie.labels = [
        member["name"]
        for member in members
    ]

    drawing.add(pie)

    elements.append(drawing)

    elements.append(Spacer(1, 20))

    # =====================================================
    # TOTAL SCORE
    # =====================================================

    total_para = Paragraph(
        f"<font size=12><b>Total Project Contribution Score : {total}</b></font>",
        styles['BodyText']
    )

    elements.append(total_para)

    elements.append(Spacer(1, 20))

    # =====================================================
    # DATE
    # =====================================================

    generated_date = Paragraph(
        f"<font size=10><b>Generated On : {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</b></font>",
        styles['BodyText']
    )

    elements.append(generated_date)

    elements.append(Spacer(1, 20))

    # =====================================================
    # FOOTER
    # =====================================================

    footer = Paragraph(
        "<font size=10><b>Generated Using AI Contribution Tracking System</b></font>",
        styles['BodyText']
    )

    elements.append(footer)

    elements.append(Spacer(1, 20))

    end_report = Paragraph(
        "<font size=14><b>*** END OF REPORT ***</b></font>",
        styles['Title']
    )

    elements.append(end_report)

    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(elements)

    print("PDF Report Generated Successfully!")