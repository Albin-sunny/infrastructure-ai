from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def generate_report(
    filename,
    defect_count,
    crack_area_percent,
    severity,
    risk_level,
    recommendation
):

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "InfraGuard AI Inspection Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            f"Defect Count: {defect_count}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Crack Area Percentage: {crack_area_percent:.2f}%",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Severity: {severity}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Risk Level: {risk_level}",
            styles["BodyText"]
        )
    )

    content.append(
        Paragraph(
            f"Recommendation: {recommendation}",
            styles["BodyText"]
        )
    )

    pdf.build(content)

    return filename