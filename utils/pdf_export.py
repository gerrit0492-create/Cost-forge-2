from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def make_offer_pdf(df, title: str = "Offerte") -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    total = float(df["total_cost"].sum())
    story.append(Paragraph(f"Totaalprijs: <b>EUR {total:,.2f}</b>", styles["Normal"]))
    headers = ["Line", "Material", "Qty", "Mat. cost", "Proc. cost", "Overhead", "Total"]
    rows = [
        [
            str(r.get("line_id", "")),
            str(r.get("material_id", "")),
            str(r.get("qty", "")),
            f"{r.get('material_cost', 0):,.2f}",
            f"{r.get('process_cost', 0):,.2f}",
            f"{r.get('overhead', 0):,.2f}",
            f"{r.get('total_cost', 0):,.2f}",
        ]
        for _, r in df.iterrows()
    ]
    t = Table([headers] + rows)
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(t)
    doc.build(story)
    return buf.getvalue()
