from __future__ import annotations
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import pandas as pd

def make_offer_pdf(df: pd.DataFrame, title: str = "Offerte") -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Totaalprijs: <b>EUR {df['total_cost'].sum():,.2f}</b>", styles["Normal"]))
    story.append(Spacer(1, 12))

    headers = ["Line","Material","Qty","Mat. cost","Proc. cost","Overhead","Total"]
    data = [headers]
    for _, r in df.iterrows():
        data.append([
            str(r.get("line_id","")),
            str(r.get("material_id","")),
            str(r.get("qty","")),
            f"{r.get('material_cost',0):,.2f}",
            f"{r.get('process_cost',0):,.2f}",
            f"{r.get('overhead',0):,.2f}",
            f"{r.get('total_cost',0):,.2f}",
        ])
    tbl = Table(data, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("GRID",(0,0),(-1,-1),0.3,colors.grey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("FONTSIZE",(0,0),(-1,-1),9),
        ("BOTTOMPADDING",(0,0),(-1,0),6),
        ("TOPPADDING",(0,0),(-1,0),6),
    ]))

    story.append(tbl)
    doc.build(story)
    return buf.getvalue()
