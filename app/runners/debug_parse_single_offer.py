from pathlib import Path
import pdfplumber


# =========================================================
# CONFIG
# =========================================================

PDF_PATH = Path(
    r"C:\Users\PV\OneDrive\Sicherheitssysteme Vöcklabruck GmbH\Angebote\Verarbeitet\An-VB-162_2025.pdf"
)

OUTPUT_DEBUG_FILE = Path(
    r"C:\Users\PV\OneDrive\backend\debug_pdf_output_2.txt"
)


# =========================================================
# FUNCTIONS
# =========================================================

def extract_text(pdf_path: Path) -> str:
    text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


# =========================================================
# MAIN
# =========================================================

def main():

    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}")
        return

    print(f"\nReading PDF: {PDF_PATH}\n")

    raw_text = extract_text(PDF_PATH)

    # ------------------------------
    # RAW TEXT
    # ------------------------------

    print("=" * 80)
    print("RAW TEXT")
    print("=" * 80)

    print(raw_text[:3000])

    # ------------------------------
    # CLEAN LINES
    # ------------------------------

    lines = clean_lines(raw_text)

    print("\n" + "=" * 80)
    print("CLEAN LINES")
    print("=" * 80)

    for i, line in enumerate(lines):
        print(f"{i:03d}: {line}")

    # ------------------------------
    # WRITE DEBUG FILE
    # ------------------------------

    debug_parts = []

    debug_parts.append("=" * 80)
    debug_parts.append("RAW TEXT")
    debug_parts.append("=" * 80)
    debug_parts.append(raw_text)
    debug_parts.append("")

    debug_parts.append("=" * 80)
    debug_parts.append("CLEAN LINES")
    debug_parts.append("=" * 80)

    for i, line in enumerate(lines):
        debug_parts.append(f"{i:03d}: {line}")

    OUTPUT_DEBUG_FILE.write_text("\n".join(debug_parts), encoding="utf-8")

    print(f"\nDebug output written to:\n{OUTPUT_DEBUG_FILE}")


# =========================================================

if __name__ == "__main__":
    main()