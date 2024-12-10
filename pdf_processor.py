import gc
import io
import os
import tempfile
import ocrmypdf
from pdfplumber import open as open_pdf
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from langdetect import detect

def extract_text(pdf_path, dpi=200):
    """Extract text with memory-efficient processing"""
    import gc
    
    temp_dir = tempfile.TemporaryDirectory()
    ocr_output_path = os.path.join(temp_dir.name, "ocr_output.pdf")
    text_data = []

    try:
        ocrmypdf.ocr(
            input_file=pdf_path,
            output_file=ocr_output_path,
            use_threads=True,
            force_ocr=True,
            language="jpn",
            jobs=2
        )
        
        with open_pdf(ocr_output_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                try:
                    words = page.extract_words()
                    if not words:
                        print(f"No features in text on page {page_number}. Skipping...")
                        continue
                        
                    chunk_size = 100
                    for i in range(0, len(words), chunk_size):
                        word_chunk = words[i:i + chunk_size]
                        for word in word_chunk:
                            text_data.append({
                                "page_number": page_number,
                                "text": word['text'],
                                "x0": word['x0'],
                                "y0": word['top'],
                                "x1": word['x1'],
                                "y1": word['bottom'],
                                "page_width": page.width,
                                "page_height": page.height
                            })
                        
                        gc.collect()
                        
                except Exception as e:
                    print(f"Error processing page {page_number}: {e}")
                    continue
                
        return text_data

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        raise e

    finally:
        temp_dir.cleanup()
        gc.collect()

def create_translated_pdf(original_pdf, output_pdf, text_data):
    reader = PdfReader(original_pdf)
    writer = PdfWriter()

    pages_data = {}
    for item in text_data:
        pg = item["page_number"]
        if pg not in pages_data:
            pages_data[pg] = []
        pages_data[pg].append(item)

    for page_num, page in enumerate(reader.pages):
        page_data = pages_data.get(page_num, [])
        if not page_data:
            writer.add_page(page)
            continue

        page_width = page_data[0]["page_width"]
        page_height = page_data[0]["page_height"]

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))
        can.setFont("Helvetica", 10)

        for item in page_data:
            rect_width = item["x1"] - item["x0"]
            rect_height = item["y1"] - item["y0"]

            can.setFillColorRGB(1, 1, 1)
            can.rect(item["x0"], item["y0"], rect_width, rect_height, fill=1, stroke=0)
            can.setFillColorRGB(0, 0, 0)
            text_y = item["y0"] + (rect_height / 2) - 3
            can.drawString(item["x0"], text_y, item["translated_text"])

        can.save()
        packet.seek(0)

        overlay_pdf = PdfReader(packet)
        overlay_page = overlay_pdf.pages[0]
        page.merge_page(overlay_page)
        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f) 