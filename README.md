# MangaTranslator-presented-by-SigmaRizzlers

# Manga Translator

A desktop application that translates Japanese manga/PDF files to English using AI-powered translation.

## Features

- Single PDF file translation
- Batch processing of multiple PDFs
- OCR (Optical Character Recognition) for Japanese text
- AI-powered Japanese to English translation
- Progress tracking for batch operations
- Translation history management
- Dark/Light mode support

## Prerequisites

- Python 3.8 or higher
- Tesseract OCR
- Poppler
- GPU recommended for faster processing

### Required Software

1. **Tesseract OCR**:
   - **Windows**: [Download and Install](https://github.com/UB-Mannheim/tesseract/wiki). Add the installation path to your system's `PATH` environment variable.
   - **Linux**: Install via package manager:
     ```bash
     sudo apt install tesseract-ocr
     ```
   - **macOS**: Install via Homebrew:
     ```bash
     brew install tesseract
     ```
2. **Poppler** (for PDF to image conversion):
   - **Windows**: [Download and Extract](https://github.com/oschwartz10612/poppler-windows/releases). Add the `bin` folder to your `PATH`.
   - **Linux**: Install via package manager:
     ```bash
     sudo apt install poppler-utils
     ```
   - **macOS**: Install via Homebrew:
     ```bash
     brew install poppler

### Required Dependencies

The application requires the following external tools:
- Tesseract-OCR (for text recognition)
- Poppler (for PDF processing)

These should be placed in the `tempDependencies` folder: 
tempDependencies/
├── Tesseract-OCR/
│ └── tesseract.exe
└── poppler-24.12.0/
└── Library/
└── bin/

## Installation

1. Clone the repository:
bash
git clone [repository-url]
cd manga-translator

2. Install required Python packages:
bash
pip install -r requirements.txt

## Usage

### Run from Source
bash
python main.py

### Features Guide

1. **Single File Translation**
   - Click "Upload Single File"
   - Select a PDF file
   - Wait for processing
   - Download the translated PDF

2. **Batch Processing**
   - Click "Batch Upload"
   - Select multiple PDF files
   - Monitor progress bar
   - Access translated files through history

3. **Translation History**
   - View all translated files
   - Download previous translations
   - Track translation dates

4. **Settings**
   - Toggle between Light/Dark modes
   - Additional settings can be configured here

## Project Structure
manga-translator/
├── main.py 
├── batch_processor.py
├── pdf_processor.py 
├── requirements.txt
├── bg.png
└── tempDependencies

## Technical Details

### Components

1. **PDF Processing**
   - Uses OCRmyPDF for text extraction
   - Implements memory-efficient processing
   - Handles large PDF files

2. **Translation**
   - Uses the JaptoEnBetterMTL-2 model
   - Supports batch translation
   - Maintains original PDF layout

3. **UI**
   - Built with CustomTkinter
   - Responsive design
   - Progress tracking

### Performance Considerations

- Memory management for large PDFs
- Batch processing with controlled resource usage
- Progress tracking for long operations

## Troubleshooting

Common issues and solutions:

1. **OCR Issues**
   - Ensure Tesseract is properly installed
   - Check language pack installation

2. **PDF Processing Errors**
   - Verify Poppler installation
   - Check PDF file permissions

3. **Memory Issues**
   - Reduce batch size
   - Close other applications
   - Consider GPU usage

## Acknowledgments

