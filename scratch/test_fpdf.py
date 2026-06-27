from fpdf import FPDF
import sys

try:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    
    # Let's see current x, y
    print(f"Initial: x={pdf.get_x()}, y={pdf.get_y()}")
    
    # Test cell
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "ALICE SMITH", new_x="LMARGIN", new_y="NEXT")
    print(f"After cell: x={pdf.get_x()}, y={pdf.get_y()}")
    
    # Test multi_cell
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 6, "Email: alice.smith@email.com")
    print(f"After multi_cell: x={pdf.get_x()}, y={pdf.get_y()}")
    
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
