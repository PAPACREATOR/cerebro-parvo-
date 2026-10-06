"""Real LibreOffice Writer structural/render round-trip.

This is deliberately separate from nexus.adapters.office: first prove the native
Writer/ODF mechanisms with the real application, then extend the production
adapter only where the proof is stable.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import zipfile
from xml.etree import ElementTree as ET

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("NEXUS_REAL_WRITER") != "1",
    reason="explicit real LibreOffice Writer gate",
)

OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
STYLE = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
FO = "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
MANIFEST = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"

for prefix, uri in {"office": OFFICE, "style": STYLE, "text": TEXT, "fo": FO}.items():
    ET.register_namespace(prefix, uri)


def _soffice() -> str:
    requested = os.environ.get("LIBREOFFICE_EXE")
    if requested:
        path = Path(requested)
        if path.is_file():
            return str(path)
        raise AssertionError(f"LIBREOFFICE_EXE missing: {path}")
    found = shutil.which("soffice") or shutil.which("soffice.com") or shutil.which("soffice.exe")
    if not found:
        raise AssertionError("LibreOffice soffice executable not found")
    return found


def _xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def make_book_odt(path: Path) -> None:
    styles = ET.Element(f"{{{OFFICE}}}document-styles", {f"{{{OFFICE}}}version": "1.3"})
    office_styles = ET.SubElement(styles, f"{{{OFFICE}}}styles")

    body_style = ET.SubElement(
        office_styles, f"{{{STYLE}}}style",
        {f"{{{STYLE}}}name": "Body", f"{{{STYLE}}}family": "paragraph"},
    )
    ET.SubElement(
        body_style, f"{{{STYLE}}}paragraph-properties",
        {
            f"{{{FO}}}orphans": "2",
            f"{{{FO}}}widows": "2",
            f"{{{FO}}}line-height": "120%",
            f"{{{FO}}}text-indent": "0.5cm",
            f"{{{FO}}}margin-bottom": "0.12cm",
        },
    )

    heading_style = ET.SubElement(
        office_styles, f"{{{STYLE}}}style",
        {f"{{{STYLE}}}name": "ChapterTitle", f"{{{STYLE}}}family": "paragraph"},
    )
    ET.SubElement(
        heading_style, f"{{{STYLE}}}paragraph-properties",
        {
            f"{{{FO}}}keep-with-next": "always",
            f"{{{FO}}}break-before": "page",
            f"{{{FO}}}margin-top": "0cm",
            f"{{{FO}}}margin-bottom": "0.8cm",
        },
    )
    ET.SubElement(
        heading_style, f"{{{STYLE}}}text-properties",
        {f"{{{FO}}}font-size": "16pt", f"{{{FO}}}font-weight": "bold"},
    )

    header_style = ET.SubElement(
        office_styles, f"{{{STYLE}}}style",
        {f"{{{STYLE}}}name": "Header", f"{{{STYLE}}}family": "paragraph"},
    )
    ET.SubElement(header_style, f"{{{STYLE}}}paragraph-properties", {f"{{{FO}}}text-align": "center"})

    auto = ET.SubElement(styles, f"{{{OFFICE}}}automatic-styles")
    page = ET.SubElement(
        auto, f"{{{STYLE}}}page-layout",
        {f"{{{STYLE}}}name": "BookPage", f"{{{STYLE}}}page-usage": "mirrored"},
    )
    ET.SubElement(
        page, f"{{{STYLE}}}page-layout-properties",
        {
            f"{{{FO}}}page-width": "14.8cm",
            f"{{{FO}}}page-height": "21cm",
            f"{{{STYLE}}}print-orientation": "portrait",
            f"{{{FO}}}margin-top": "1.8cm",
            f"{{{FO}}}margin-bottom": "1.8cm",
            # Mirrored usage makes these inner/outer in Writer.
            f"{{{FO}}}margin-left": "2.5cm",
            f"{{{FO}}}margin-right": "1.7cm",
        },
    )

    masters = ET.SubElement(styles, f"{{{OFFICE}}}master-styles")
    master = ET.SubElement(
        masters, f"{{{STYLE}}}master-page",
        {f"{{{STYLE}}}name": "Standard", f"{{{STYLE}}}page-layout-name": "BookPage"},
    )
    header = ET.SubElement(master, f"{{{STYLE}}}header")
    ET.SubElement(header, f"{{{TEXT}}}p", {f"{{{TEXT}}}style-name": "Header"}).text = "Nexus — Livro de ensaio"
    footer = ET.SubElement(master, f"{{{STYLE}}}footer")
    fp = ET.SubElement(footer, f"{{{TEXT}}}p", {f"{{{TEXT}}}style-name": "Header"})
    ET.SubElement(fp, f"{{{TEXT}}}page-number", {f"{{{TEXT}}}select-page": "current"}).text = "1"

    content = ET.Element(f"{{{OFFICE}}}document-content", {f"{{{OFFICE}}}version": "1.3"})
    body = ET.SubElement(content, f"{{{OFFICE}}}body")
    text = ET.SubElement(body, f"{{{OFFICE}}}text")
    for chapter in range(1, 4):
        heading = ET.SubElement(
            text, f"{{{TEXT}}}h",
            {f"{{{TEXT}}}style-name": "ChapterTitle", f"{{{TEXT}}}outline-level": "1"},
        )
        heading.text = f"Capítulo {chapter} — Ação e memória"
        for paragraph in range(32):
            p = ET.SubElement(text, f"{{{TEXT}}}p", {f"{{{TEXT}}}style-name": "Body"})
            p.text = (
                f"Parágrafo {chapter}.{paragraph + 1}. "
                "Ação, proveniência, memória e revisão humana permanecem explícitas. "
                "Este texto força paginação suficiente para testar o fluxo real do Writer. "
                "Nenhuma ferramenta recebe autoridade sobre Creative ou Canonical."
            )

    meta = ET.Element(
        f"{{{OFFICE}}}document-meta",
        {f"{{{OFFICE}}}version": "1.3"},
    )
    ET.SubElement(meta, f"{{{OFFICE}}}meta")

    manifest = ET.Element(
        f"{{{MANIFEST}}}manifest",
        {f"{{{MANIFEST}}}version": "1.3"},
    )
    for full_path, media in (
        ("/", "application/vnd.oasis.opendocument.text"),
        ("content.xml", "text/xml"),
        ("styles.xml", "text/xml"),
        ("meta.xml", "text/xml"),
    ):
        ET.SubElement(
            manifest, f"{{{MANIFEST}}}file-entry",
            {f"{{{MANIFEST}}}full-path": full_path, f"{{{MANIFEST}}}media-type": media},
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            zipfile.ZipInfo("mimetype"),
            b"application/vnd.oasis.opendocument.text",
            compress_type=zipfile.ZIP_STORED,
        )
        archive.writestr("content.xml", _xml_bytes(content), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("styles.xml", _xml_bytes(styles), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("meta.xml", _xml_bytes(meta), compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr("META-INF/manifest.xml", _xml_bytes(manifest), compress_type=zipfile.ZIP_DEFLATED)


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [_soffice(), "--headless", "--norestore", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    return result


def _odt_member(path: Path, name: str) -> bytes:
    with zipfile.ZipFile(path) as archive:
        return archive.read(name)


def test_writer_real_opens_preserves_structure_roundtrips_and_exports_pdf(tmp_path):
    source = tmp_path / "book.odt"
    make_book_odt(source)

    styles_before = ET.fromstring(_odt_member(source, "styles.xml"))
    page = styles_before.find(f".//{{{STYLE}}}page-layout")
    props = styles_before.find(f".//{{{STYLE}}}page-layout-properties")
    assert page is not None and page.attrib[f"{{{STYLE}}}page-usage"] == "mirrored"
    assert props is not None
    assert props.attrib[f"{{{FO}}}margin-left"] == "2.5cm"
    assert props.attrib[f"{{{FO}}}margin-right"] == "1.7cm"

    rendered = tmp_path / "rendered"
    rendered.mkdir()
    _run("--convert-to", "fodt", "--outdir", str(rendered), str(source), cwd=tmp_path)
    fodt = rendered / "book.fodt"
    assert fodt.is_file() and fodt.stat().st_size > 1000
    flat = fodt.read_text(encoding="utf-8")
    assert "Capítulo 1 — Ação e memória" in flat
    assert "fo:keep-with-next=\"always\"" in flat
    assert "fo:orphans=\"2\"" in flat
    assert "fo:widows=\"2\"" in flat
    assert "style:page-usage=\"mirrored\"" in flat

    roundtrip = tmp_path / "roundtrip"
    roundtrip.mkdir()
    _run("--convert-to", "odt", "--outdir", str(roundtrip), str(fodt), cwd=tmp_path)
    odt2 = roundtrip / "book.odt"
    assert odt2.is_file()
    content2 = _odt_member(odt2, "content.xml").decode("utf-8")
    styles2 = _odt_member(odt2, "styles.xml").decode("utf-8")
    assert "Capítulo 3 — Ação e memória" in content2
    assert "keep-with-next" in styles2
    assert "orphans" in styles2 and "widows" in styles2
    assert "page-usage=\"mirrored\"" in styles2

    pdfdir = tmp_path / "pdf"
    pdfdir.mkdir()
    _run("--convert-to", "pdf:writer_pdf_Export", "--outdir", str(pdfdir), str(odt2), cwd=tmp_path)
    pdf = pdfdir / "book.pdf"
    raw = pdf.read_bytes()
    assert len(raw) > 5_000
    assert raw.startswith(b"%PDF-")
    assert b"%%EOF" in raw[-2048:]


def test_writer_real_original_bytes_are_unchanged(tmp_path):
    source = tmp_path / "book.odt"
    make_book_odt(source)
    original = source.read_bytes()
    out = tmp_path / "out"
    out.mkdir()
    _run("--convert-to", "pdf:writer_pdf_Export", "--outdir", str(out), str(source), cwd=tmp_path)
    assert source.read_bytes() == original
