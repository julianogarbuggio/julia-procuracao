# -*- coding: utf-8 -*-
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path
from datetime import datetime
from tempfile import TemporaryDirectory
import traceback, shutil, subprocess, re, unicodedata

from docxtpl import DocxTemplate
from docx import Document
# >>> correção dos imports do python-docx:
from docx.oxml import OxmlElement
from docx.oxml.shared import qn

try:
    from docx2pdf import convert as docx2pdf_convert
    DOCX2PDF_OK = True
except Exception:
    DOCX2PDF_OK = False

BASE_DIR  = Path(__file__).resolve().parent
DOCS_DIR  = BASE_DIR / "documentos"
SAIDA_DIR = BASE_DIR / "saida"
TPL_DIR   = BASE_DIR / "templates"
STATIC_DIR= BASE_DIR / "static"

for p in (DOCS_DIR, SAIDA_DIR, STATIC_DIR, TPL_DIR):
    p.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Jul.IA – Automação PDF & DOCX")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TPL_DIR))

# ----------------------------- Utils -----------------------------
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s.lower().strip()

def parse_bloco(texto: str) -> dict:
    ctx = {
        "NOME": "", "NACIONALIDADE": "", "NASCIMENTO": "", "ESTADO_CIVIL": "", "PROFISSAO": "",
        "RG": "", "CPF": "", "LOGRADOURO": "", "NUMERO": "", "COMPLEMENTO": "", "BAIRRO": "",
        "CEP": "", "CIDADE": "", "ESTADO": "", "WHATSAPP": "", "EMAIL": "",
        "DATA_HOJE": datetime.now().strftime("%d/%m/%Y"),
    }

    for raw in (texto or "").splitlines():
        if ":" not in raw:
            continue
        label, val = raw.split(":", 1)
        lab   = _norm(label)
        value = val.strip()

        if "nome" in lab:               ctx["NOME"] = value; continue
        if "nacionalidade" in lab:      ctx["NACIONALIDADE"] = value; continue
        if "nascimento" in lab:         ctx["NASCIMENTO"] = value; continue
        if "estado civil" in lab:       ctx["ESTADO_CIVIL"] = value; continue
        if "profiss" in lab:            ctx["PROFISSAO"] = value; continue

        # RG "... - ESTADO: PR" -> "... - PR"
        if lab.startswith("rg"):
            num = value
            m = re.search(r"(?:estado\s*:\s*)?([A-Za-z]{2})\s*$", value, flags=re.IGNORECASE)
            if m:
                uf = m.group(1).upper()
                num = re.sub(r"-?\s*estado\s*:\s*[A-Za-z]{2}\s*$", "", value, flags=re.IGNORECASE).strip()
                num = re.sub(r"\s*-\s*$", "", num)
                ctx["RG"] = f"{num} - {uf}"
            else:
                ctx["RG"] = value
            continue

        if "cpf" in lab:                ctx["CPF"] = value; continue

        # ENDEREÇO COMPLETO -> LOGRADOURO/NUMERO/COMPLEMENTO
        if "endereco" in lab or "endereço" in lab:
            mlog  = re.search(r"^\s*(.*?)(?:,|$)", value)
            ctx["LOGRADOURO"] = (mlog.group(1).strip() if mlog else value)

            # só pega "nº / n. / no:" após início ou vírgula (evita "MariNO")
            mnum  = re.search(r"(?:^|[,;])\s*n[ºo\.]?\s*:?\s*([\d\w\-\/]+)", value, flags=re.IGNORECASE)
            ctx["NUMERO"]      = (mnum.group(1).strip() if mnum else "")

            mcomp = re.search(r"complemento\s*:\s*([^,]+)", value, flags=re.IGNORECASE)
            ctx["COMPLEMENTO"] = (mcomp.group(1).strip() if mcomp else "")
            continue

        if "bairro" in lab:             ctx["BAIRRO"] = value; continue
        if "cep" in lab:                ctx["CEP"] = value; continue

        # CIDADE "Maringá - ESTADO: PR" -> CIDADE=Maringá / ESTADO=PR
        if "cidade" in lab and "estado" in lab:
            m = re.search(
                r"^\s*([^,\-]+)[,\-]?\s*(?:estado\s*:\s*|uf\s*:\s*)?([A-Za-z]{2})\s*$",
                value,
                flags=re.IGNORECASE,
            )
            if m:
                ctx["CIDADE"] = m.group(1).strip()
                ctx["ESTADO"] = m.group(2).upper()
            else:
                ctx["CIDADE"] = value
            continue

        if "cidade" in lab:
            m = re.search(
                r"^\s*([^,\-]+)\s*[-,]\s*(?:estado\s*:\s*|uf\s*:\s*)?([A-Za-z]{2})\s*$",
                value,
                flags=re.IGNORECASE,
            )
            if m:
                ctx["CIDADE"] = m.group(1).strip()
                ctx["ESTADO"] = m.group(2).upper()
            else:
                ctx["CIDADE"] = value
            continue

        if lab == "estado" or lab == "uf":
            ctx["ESTADO"] = value.strip().upper(); continue

        if "whats" in lab:              ctx["WHATSAPP"] = value; continue
        if "e-mail" in lab or "email" in lab:
            ctx["EMAIL"] = value; continue

    return ctx

def escolher_modelo() -> Path | None:
    preferido = DOCS_DIR / "documentos_acao.docx"
    if preferido.exists():
        return preferido
    preferido2 = DOCS_DIR / "documentos acao.docx"
    if preferido2.exists():
        return preferido2
    for p in sorted(DOCS_DIR.glob("*.docx")):
        if "~$" in p.name:
            continue
        return p
    return None

# --------- helper de nome: 02_Procuracao_Consig_Nome_Autor.ext ----------
def gerar_nome_arquivo(nome: str, extensao: str) -> Path:
    """
    Gera caminho na pasta SAIDA com o formato:
    02_Procuracao_Consig_Nome_Autor.ext
    """
    if not nome:
        sufixo = "Autor"
    else:
        # troca espaços por "_" e remove duplos
        sufixo = re.sub(r"\s+", "_", nome.strip())
    filename = f"02_Procuracao_Consig_{sufixo}.{extensao}"
    return SAIDA_DIR / filename

# ---------------- negrito APENAS no nome, preservando fonte ----------------
def _apply_base_font(dst_run, base_run):
    """Copia fonte/tamanho/estilo do run base (ex.: Montserrat)."""
    if not base_run:
        return
    f_dst, f_base = dst_run.font, base_run.font
    # fonte
    if f_base.name:
        f_dst.name = f_base.name
        rPr = dst_run._element.get_or_add_rPr()
        rFonts = rPr.rFonts
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        for key in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rFonts.set(qn(key), f_base.name)
    # demais atributos úteis
    f_dst.size   = f_base.size
    f_dst.italic = f_base.italic
    if f_base.color and f_base.color.rgb:
        f_dst.color.rgb = f_base.color.rgb

def _bold_substring_in_paragraph(paragraph, target: str):
    if not target:
        return

    # guarda o 1º run como referência de formatação (Montserrat)
    base_run = paragraph.runs[0] if paragraph.runs else None

    full = "".join(r.text for r in paragraph.runs)
    if not full:
        return

    # localizar todas ocorrências (case-sensitive)
    idxs, start = [], 0
    while True:
        i = full.find(target, start)
        if i == -1:
            break
        idxs.append((i, i + len(target)))
        start = i + len(target)
    if not idxs:
        return

    # “limpa” textos anteriores mas preserva o parágrafo
    for r in paragraph.runs:
        r.text = ""

    # recria runs preservando fonte do base_run
    cursor = 0
    for a, b in idxs:
        if a > cursor:
            r1 = paragraph.add_run(full[cursor:a])
            _apply_base_font(r1, base_run)
        r2 = paragraph.add_run(full[a:b])
        _apply_base_font(r2, base_run)
        r2.bold = True  # apenas o nome
        cursor = b
    if cursor < len(full):
        r3 = paragraph.add_run(full[cursor:])
        _apply_base_font(r3, base_run)

def bold_nome_everywhere(docx_path: Path, nome: str):
    if not nome:
        return
    try:
        doc = Document(str(docx_path))
        for p in doc.paragraphs:
            _bold_substring_in_paragraph(p, nome)
        for t in doc.tables:
            for row in t.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        _bold_substring_in_paragraph(p, nome)
        doc.save(str(docx_path))
    except Exception:
        # se der erro, não derruba o fluxo; só não aplica o bold
        pass

def try_convert_with_soffice(src_docx: Path, dst_pdf: Path) -> bool:
    try:
        cmd = [
            "soffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(dst_pdf.parent),
            str(src_docx),
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return dst_pdf.exists()
    except Exception:
        return False

# ----------------------------- Rotas -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/docx", response_class=HTMLResponse)
async def docx_page(request: Request):
    return templates.TemplateResponse("docx.html", {"request": request})

@app.get("/pdf", response_class=HTMLResponse)
async def pdf_page(request: Request):
    return templates.TemplateResponse("pdf.html", {"request": request})

@app.post("/gerar-docx")
async def gerar_docx(dados: str = Form(...)):
    try:
        modelo = escolher_modelo()
        if not modelo:
            return PlainTextResponse(
                "Modelo .docx não encontrado em app/documentos.",
                status_code=500,
            )
        ctx = parse_bloco(dados)
        nome_autor = ctx.get("NOME", "").strip()

        with TemporaryDirectory() as tmpdir:
            tmpdir   = Path(tmpdir)
            out_docx = tmpdir / "saida.docx"
            tpl = DocxTemplate(str(modelo))
            tpl.render(ctx)
            tpl.save(str(out_docx))

            bold_nome_everywhere(out_docx, nome_autor)

            final_docx = gerar_nome_arquivo(nome_autor, "docx")
            final_docx.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(out_docx, final_docx)

            return FileResponse(final_docx, filename=final_docx.name)
    except Exception:
        (SAIDA_DIR / "stacktrace.txt").write_text(
            traceback.format_exc(), encoding="utf-8"
        )
        return PlainTextResponse(
            "Erro ao gerar DOCX. Veja app/saida/stacktrace.txt",
            status_code=500,
        )

@app.post("/gerar-pdf")
async def gerar_pdf(dados: str = Form(...)):
    try:
        modelo = escolher_modelo()
        if not modelo:
            return PlainTextResponse(
                "Modelo .docx não encontrado em app/documentos.",
                status_code=500,
            )
        ctx = parse_bloco(dados)
        nome_autor = ctx.get("NOME", "").strip()

        with TemporaryDirectory() as tmpdir:
            tmpdir   = Path(tmpdir)
            out_docx = tmpdir / "saida.docx"
            tpl = DocxTemplate(str(modelo))
            tpl.render(ctx)
            tpl.save(str(out_docx))

            bold_nome_everywhere(out_docx, nome_autor)

            out_pdf = tmpdir / "saida.pdf"
            ok = False

            if DOCX2PDF_OK:
                try:
                    docx2pdf_convert(str(out_docx), str(out_pdf))
                    ok = out_pdf.exists()
                except Exception:
                    ok = False

            if not ok:
                ok = try_convert_with_soffice(out_docx, out_pdf)

            if ok:
                final_pdf = gerar_nome_arquivo(nome_autor, "pdf")
                final_pdf.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(out_pdf, final_pdf)
                return FileResponse(final_pdf, filename=final_pdf.name)
            else:
                # fallback: devolve DOCX no padrão 02_Procuracao_Consig_...
                final_docx = gerar_nome_arquivo(nome_autor, "docx")
                final_docx.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(out_docx, final_docx)
                return FileResponse(final_docx, filename=final_docx.name)
    except Exception:
        (SAIDA_DIR / "stacktrace.txt").write_text(
            traceback.format_exc(), encoding="utf-8"
        )
        return PlainTextResponse(
            "Erro ao gerar PDF. Veja app/saida/stacktrace.txt",
            status_code=500,
        )
