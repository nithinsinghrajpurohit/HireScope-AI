"""
Sample Resume PDF Generator for HireScope AI.
Converts .txt resume files to professionally formatted PDFs using fpdf2.
"""

from fpdf import FPDF
import os
import glob


def txt_to_pdf(txt_path: str, pdf_path: str) -> None:
    """Convert a text resume file to a formatted PDF.

    Args:
        txt_path: Path to the input .txt file
        pdf_path: Path to save the output .pdf file
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)

    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")

            # Handle headers (lines in ALL CAPS or starting with ===)
            if line.isupper() and len(line) > 3:
                pdf.set_font("Helvetica", "B", 14)
                pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", size=11)
            elif line.startswith("---"):
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(5)
            elif line.startswith("==="):
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(3)
            elif line.strip() == "":
                pdf.ln(4)
            else:
                # Encode to latin-1 safe string for FPDF
                safe_line = line.encode("latin-1", "replace").decode("latin-1")
                pdf.multi_cell(0, 6, safe_line, new_x="LMARGIN", new_y="NEXT")

    pdf.output(pdf_path)
    print(f"  Created: {pdf_path}")


def main():
    """Convert all .txt resume files in sample_resumes/ to PDFs."""
    txt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_resumes")
    pdf_dir = os.path.join(txt_dir, "pdf")
    os.makedirs(pdf_dir, exist_ok=True)

    txt_files = glob.glob(os.path.join(txt_dir, "*.txt"))

    if not txt_files:
        print(f"No .txt files found in {txt_dir}")
        return

    print(f"Converting {len(txt_files)} resume(s) to PDF...")
    print(f"Output directory: {pdf_dir}")
    print()

    for txt_file in sorted(txt_files):
        base = os.path.splitext(os.path.basename(txt_file))[0]
        pdf_path = os.path.join(pdf_dir, f"{base}.pdf")
        try:
            txt_to_pdf(txt_file, pdf_path)
        except Exception as e:
            print(f"  Error converting {txt_file}: {e}")

    print()
    print("Done! All PDFs generated successfully.")


if __name__ == "__main__":
    main()
