from fpdf import FPDF
from core.rust_bridge import get_risk_score
import psutil
from datetime import datetime

def export_log_to_pdf(username, role):
    cpu = int(psutil.cpu_percent(interval=1))
    ram = int(psutil.virtual_memory().percent)
    net = int(psutil.net_io_counters().bytes_sent / 1024 / 1024) % 100  # simulate network load
    risk = get_risk_score(cpu, ram, net)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Aegis Spectra - System Scan Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Generated by: {username} ({role})", ln=True)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="System Resource Usage:", ln=True)
    pdf.cell(200, 10, txt=f"- CPU Usage: {cpu}%", ln=True)
    pdf.cell(200, 10, txt=f"- RAM Usage: {ram}%", ln=True)
    pdf.cell(200, 10, txt=f"- Network Activity (mock): {net}MB", ln=True)
    pdf.cell(200, 10, txt=f"- RISK SCORE: {risk}", ln=True)
    pdf.ln(10)

    if risk > 85:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(200, 10, txt="⚠ HIGH RISK DETECTED!", ln=True)
        pdf.set_text_color(0, 0, 0)

    output_path = f"C:/Users/{username}/Downloads/aegis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    try:
        pdf.output(output_path)
        print(f"✅ Report saved to {output_path}")
    except Exception as e:
        print(f"[ERROR] Could not save PDF: {e}")