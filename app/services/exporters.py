from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from fpdf import FPDF

from app.config import BASE_DIR
from app.schemas import ComicLayout

EXPORTS_DIR = BASE_DIR / "app" / "static" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _local_image_path(image_path: str) -> Path:
    parsed = urlparse(image_path)
    relative = parsed.path.lstrip("/")
    path = BASE_DIR / "app" / relative.replace("static/", "static/", 1)
    return path


def save_pdf(layout: list[ComicLayout], title: str = "ComicCraft Comic") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comiccraft_{timestamp}.pdf"
    output_path = EXPORTS_DIR / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=14)

    for index, panel in enumerate(layout):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, f"Panel {panel.panel_number}: {panel.title}")
        pdf.ln(2)

        image_path = _local_image_path(panel.image_path)
        if image_path.exists():
            pdf.image(str(image_path), x=15, y=None, w=180)
            pdf.ln(4)

        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 6, panel.scene_description)
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, "Caption", new_x="LMARGIN")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, panel.caption or "")
        pdf.ln(1)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, "Narration", new_x="LMARGIN")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, panel.narration or "")

        if panel.dialogue:
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, "Dialogue", new_x="LMARGIN")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, panel.dialogue)

    pdf.output(str(output_path))
    return f"/static/exports/{filename}"
