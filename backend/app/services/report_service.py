from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemas.report import FraudReportRequest


class ReportService:
    def generate_fraud_report(
        self,
        report: FraudReportRequest,
    ) -> bytes:
        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.65 * inch,
            leftMargin=0.65 * inch,
            topMargin=0.55 * inch,
            bottomMargin=0.55 * inch,
            title="Healthcare Fraud Detection Report",
            author="Enterprise AI Assistant",
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            leading=25,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=8,
        )

        subtitle_style = ParagraphStyle(
            name="Subtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#667085"),
        )

        section_style = ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=10,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            name="Body",
            parent=styles["BodyText"],
            fontSize=10,
            leading=16,
            textColor=colors.HexColor("#344054"),
        )

        small_style = ParagraphStyle(
            name="Small",
            parent=styles["Normal"],
            fontSize=8,
            leading=12,
            textColor=colors.HexColor("#667085"),
        )

        story = [
            Paragraph(
                "HEALTHCARE FRAUD DETECTION REPORT",
                title_style,
            ),
            Paragraph(
                "Enterprise AI Assistant",
                subtitle_style,
            ),
            Spacer(1, 16),
        ]

        summary_data = [
            [
                Paragraph("<b>Prediction</b>", body_style),
                Paragraph(
                    self._safe(report.prediction),
                    body_style,
                ),
            ],
            [
                Paragraph(
                    "<b>Fraud Probability</b>",
                    body_style,
                ),
                Paragraph(
                    f"{report.fraud_probability:.2f}%",
                    body_style,
                ),
            ],
            [
                Paragraph("<b>Risk Level</b>", body_style),
                Paragraph(
                    self._safe(report.risk_level),
                    body_style,
                ),
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[2.1 * inch, 4.6 * inch],
        )

        summary_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor("#EAF2F8"),
                    ),
                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, -1),
                        colors.HexColor("#F8FAFC"),
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        colors.HexColor("#CBD5E1"),
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor("#CBD5E1"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                ]
            )
        )

        story.append(summary_table)

        story.extend(
            [
                Paragraph(
                    "Top Contributing Features",
                    section_style,
                )
            ]
        )

        if report.top_features:
            for feature in report.top_features:
                story.append(
                    Paragraph(
                        f"- {self._safe(feature)}",
                        body_style,
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No contributing features were provided.",
                    body_style,
                )
            )

        story.extend(
            [
                Paragraph("AI Explanation", section_style),
                Paragraph(
                    self._safe(report.ai_explanation),
                    body_style,
                ),
                Paragraph("Recommendation", section_style),
                Paragraph(
                    self._safe(report.recommendation),
                    body_style,
                ),
                Spacer(1, 20),
                Paragraph(
                    (
                        "Generated on: "
                        f"{datetime.now():%B %d, %Y at %I:%M %p}"
                    ),
                    small_style,
                ),
                Paragraph(
                    (
                        "Generated by Enterprise AI Assistant "
                        "- FastAPI, Gemini and ReportLab"
                    ),
                    small_style,
                ),
            ]
        )

        document.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    @staticmethod
    def _safe(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )


report_service = ReportService()