from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.models.checklist import Checklist

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "pdf"

_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
_CSS_CONTENT = (TEMPLATE_DIR / "checklist.css").read_text(encoding="utf-8")

VISTA_LABELS = {
    "topo": "Topo",
    "lateral_esquerda": "Lateral Esquerda",
    "lateral_direita": "Lateral Direita",
    "frontal_traseira": "Frontal / Traseira",
}


def generate_checklist_pdf(checklist: Checklist) -> bytes:
    template = _env.get_template("checklist.html")

    html_content = template.render(
        checklist=checklist,
        css=_CSS_CONTENT,
        itens=checklist.itens or [],
        itens_devolucao=checklist.itens_devolucao or [],
        avarias=checklist.avarias or [],
        is_devolvido=checklist.status.value == "devolvido",
        vista_labels=VISTA_LABELS,
        generated_at=datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC"),
    )
    return HTML(string=html_content).write_pdf()
