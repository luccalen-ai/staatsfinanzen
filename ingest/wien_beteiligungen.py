"""Vienna's shareholdings report (Beteiligungsbericht der Stadt Wien), chapters as PDF from the
Wienbibliothek digital archive.

Two chapters matter for the public enterprise ledger:
- the overview table of direct holdings: annual result, revenue, investment and subsidies from
  the city (Zuschüsse der Stadt Wien), in EUR thousand;
- the portfolio of all holdings down to the third level, with shares.

The PDFs are kept unmodified in data/raw. Their text is extracted page by page into
data/extracts/ for review; table parsing follows once the layout has been read.

Run:  python -m ingest.wien_beteiligungen
"""

from __future__ import annotations

import pdfplumber

from ingest.common import REPO_ROOT, download

SOURCE_ID = "wien_beteiligungsbericht"
BASE = "https://digital.wienbibliothek.at/download/pdf/"
# Report 2024 (business year 2023): overview table and portfolio chapters.
CHAPTERS = {"2024_uebersicht": "5162233", "2024_portfolio": "5162270",
            "2024_struktur": "5162230", "2023_uebersicht": "5162143"}


def main() -> None:
    out_dir = REPO_ROOT / "data" / "extracts" / "wien_beteiligungsbericht"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, doc_id in CHAPTERS.items():
        try:
            path = download(SOURCE_ID, f"{BASE}{doc_id}.pdf", f"{name}_{doc_id}.pdf")
        except Exception as e:  # noqa: BLE001 - one missing chapter should not stop the rest
            print(f"{name}: download failed: {e}")
            continue
        pages = []
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                pages.append(f"===== page {i} =====\n{page.extract_text() or ''}")
                for j, table in enumerate(page.extract_tables(), 1):
                    rows = ["\t".join("" if c is None else str(c).replace("\n", " ") for c in r) for r in table]
                    pages.append(f"----- table {i}.{j} -----\n" + "\n".join(rows))
        (out_dir / f"{name}.txt").write_text("\n".join(pages), encoding="utf-8")
        print(f"{name}: {len(pages)} blocks")


if __name__ == "__main__":
    main()
