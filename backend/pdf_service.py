from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

RECEIPT_DIR = Path(__file__).resolve().parent / "receipts"
RECEIPT_DIR.mkdir(exist_ok=True)

def generate_receipt_pdf(order: dict) -> str:
    """
    order = {
      order_id, order_type, total,
      items: [{name, price, qty, line_total}]
    }
    Returns absolute file path (string).
    """
    order_id = order["order_id"]
    filename = f"receipt_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = RECEIPT_DIR / filename

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4

    y = height - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "KIOSK RECEIPT")
    y -= 25

    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Order #: {order_id}")
    y -= 16
    c.drawString(50, y, f"Type: {order.get('order_type', '')}")
    y -= 16
    c.drawString(50, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 20

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Item")
    c.drawString(280, y, "Qty")
    c.drawString(340, y, "Price")
    c.drawString(430, y, "Total")
    y -= 12
    c.line(50, y, width - 50, y)
    y -= 16

    c.setFont("Helvetica", 11)
    for it in order.get("items", []):
        if y < 80:  # new page
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)

        c.drawString(50, y, str(it["name"])[:28])
        c.drawRightString(320, y, str(it["qty"]))
        c.drawRightString(400, y, f"{float(it['price']):.2f}")
        c.drawRightString(width - 50, y, f"{float(it['line_total']):.2f}")
        y -= 16

    y -= 10
    c.line(50, y, width - 50, y)
    y -= 22

    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(width - 50, y, f"TOTAL: ${float(order['total']):.2f}")

    c.save()
    return str(pdf_path)
