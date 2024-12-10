### **What is the purpose of this application?**
This is an AI-powered tool designed to translate Japanese text in PDFs (e.g., manga) into English while maintaining the original layout. It supports both text-based and image-based PDFs, making it useful for translating scanned documents or manga.

---
tags:
- translation
language:
- unk
- unk
datasets:
- cyy0/open-mantra-bettermtl
co2_eq_emissions:
  emissions: 0.015690732803499252
---
# About BetterMTL

- Trained using Helsinki-NLP/opus-mt-ja-en
- Fine-tuned with OpenMantra Dataset (Lightly modified)
- Japanese to English one-way translation 

# Info

- Problem Type - Translation
- Model ID: 3620696849
- Max Context Length: 512
- CO2 Emissions (in grams): 0.0157

## Validation Metrics

- Loss: 2.309
- SacreBLEU: 9.750
- Gen len: 10.522

---

### **What are the main features of this application?**
- **Language Detection:** Automatically detects the document's language to avoid translating English documents unnecessarily.
- **OCR Support:** Extracts text from image-based PDFs, such as scanned manga pages, using Tesseract OCR.
- **Preserves Layout:** Ensures that translated text appears in the same position as the original text.
- **Seamless Workflow:** Handles the full pipeline from text extraction to translation and PDF creation.

---

### **What do users need to install to use this application?**
- **Tesseract OCR**: For OCR support on image-based PDFs.
  - Windows, Linux, and macOS installation instructions are included.
- **Poppler**: For converting PDF pages into images.
  - Installation steps are provided for all major platforms.
- **Python Dependencies**: A `requirements.txt` file is provided to simplify dependency installation.

---

### **What is the expected folder structure for this project?**
The project follows this structure:
MangaTranslator/
├── README.md               # Instructions for the project
├── requirements.txt        # Python dependencies
├── main.py                 # Main script
├── models/                 # Pre-trained translation models

x 