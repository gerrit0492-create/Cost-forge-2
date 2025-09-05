from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
def make_offer_pdf(df, title="Offerte")->bytes:
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4)
    styles=getSampleStyleSheet(); story=[]
    story.append(Paragraph(f"<b>{title}</b>",styles["Title"])); story.append(Spacer(1,12))
    story.append(Paragraph(f"Totaalprijs: <b>EUR {df['total_cost'].sum():,.2f}</b>",styles["Normal"]))
    headers=["Line","Material","Qty","Mat. cost","Proc. cost","Overhead","Total"]
    rows=[[str(r.get(c,"")) for c in ["line_id","material_id","qty","material_cost","process_cost","overhead","total_cost"]] for _,r in df.iterrows()]
    data=[headers]+rows
    t=Table(data); t.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT")
    ]))
    story.append(t); doc.build(story); return buf.getvalue()
