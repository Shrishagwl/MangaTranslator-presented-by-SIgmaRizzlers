import tkinter as tk
import customtkinter as ctk
import datetime
import os
import threading
import io
import pdfplumber
import pytesseract
import cv2
import torch
import ocrmypdf
import tempfile
from pdfplumber import open as open_pdf
import numpy as np
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename, askopenfilenames
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from langdetect import detect
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pdf2image import convert_from_path
from PIL import Image
from pytesseract import Output
from batch_processor import BatchProcessor
from pdf_processor import extract_text, create_translated_pdf

current_dir = os.path.dirname(os.path.abspath(__file__))

tesseract_path = os.path.join(current_dir, "tempDependencies", "Tesseract-OCR", "tesseract.exe")
poppler_path = os.path.join(current_dir, "tempDependencies", "poppler-24.12.0", "Library", "bin")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

history = []
uploaded_file = None
repo_id = "cyy0/JaptoEnBetterMTL-2"
try:
    tokenizer = AutoTokenizer.from_pretrained(repo_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(repo_id)
    print("Model and tokenizer loaded successfully!")
except Exception as e:
    print(f"Error loading model and tokenizer: {e}")

def translate_text(japanese_text):
    try:
        if not japanese_text or not isinstance(japanese_text, str):
            return ""
            
        lang = detect(japanese_text)
        if lang == "en":
            return japanese_text
        elif lang == "ja":
            inputs = tokenizer(japanese_text, return_tensors="pt", max_length=512, truncation=True)
            outputs = model.generate(inputs.input_ids, max_length=512, num_beams=5, early_stopping=True)
            english_translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return english_translation
        else:
            return japanese_text
    except Exception as e:
        print(f"Translation error: {e}")
        return japanese_text  # Return original text if translation fails

class MangaTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Manga Translator App")
        self.geometry("1000x700")
        self.canvas = tk.Canvas(self, width=1000, height=700)
        self.canvas.pack(fill="both", expand=True)
        self.bg_image = tk.PhotoImage(file="bg.png")
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.pages = {}
        self.current_page = None

        self.init_nav_bar()
        self.init_upload_page()
        self.init_translation_page()
        self.init_history_page()
        self.init_settings_page()

        self.show_page("FileUploadPage")

    def init_nav_bar(self):
        self.nav_bar_buttons = []

        button_texts = [("Upload File", self.show_upload_page),
                        ("Translation Viewer", self.show_translation_page),
                        ("History", self.show_history_page),
                        ("Settings", self.show_settings_page)]

        x_position = 10
        for text, command in button_texts:
            button = ctk.CTkButton(self.canvas, text=text, font=("Helvetica", 16), command=command, bg_color='#161e25', fg_color='#161e25', hover_color="#212e38", corner_radius=10)
            button_window = self.canvas.create_window(x_position, 25, anchor="nw", window=button)
            self.nav_bar_buttons.append(button_window)
            x_position += 250

    def show_upload_page(self):
        self.show_page("FileUploadPage")
    def show_translation_page(self):
        self.show_page("TranslationViewerPage")
    def show_history_page(self):
        self.show_page("HistoryPage")
    def show_settings_page(self):
        self.show_page("SettingsPage")

    def init_upload_page(self):
        widgets = []
        rounded_background = self.canvas.create_oval(498, 693, 1000, 440, fill="#263642", outline="", tags="FileUploadPage")
        widgets.append(rounded_background)
        
        self.batch_upload_button = ctk.CTkButton(
            self.canvas, 
            text="Batch Upload", 
            font=("Helvetica", 16),
            corner_radius=30,
            bg_color="#263642",
            fg_color="#1c72b6",
            hover_color="#1b5a8a",
            text_color="white",
            border_width=0,
            command=self.batch_upload_files
        )
        batch_button_id = self.canvas.create_window(
            650, 486, anchor="nw", window=self.batch_upload_button, tags="FileUploadPage"
        )
        widgets.append(batch_button_id)
        
        self.upload_button = ctk.CTkButton(
            self.canvas, 
            text="Upload Single File", 
            font=("Helvetica", 16),
            corner_radius=30,
            bg_color="#263642",
            fg_color="#1c72b6",
            hover_color="#1b5a8a",
            text_color="white",
            border_width=0,
            command=self.upload_file
        )
        button_id = self.canvas.create_window(
            650, 546, anchor="nw", window=self.upload_button, tags="FileUploadPage"
        )
        widgets.append(button_id)
        
        # i added it, but the rogress bar is kinda broken...
        self.progress_bar = ctk.CTkProgressBar(
            self.canvas,
            width=300,
            height=20,
            corner_radius=10,
            bg_color="#263642"
        )
        progress_bar_id = self.canvas.create_window(
            650, 606, anchor="nw", window=self.progress_bar, tags="FileUploadPage"
        )
        self.progress_bar.set(0)
        widgets.append(progress_bar_id)
        
        self.pages["FileUploadPage"] = widgets

    def init_translation_page(self):
        widgets = []
        original_label = ctk.CTkLabel(self.canvas, text="Original Japanese Text", font=("Helvetica", 14))
        label_id = self.canvas.create_window(500, 150, anchor="center", window=original_label, tags="TranslationViewerPage")
        widgets.append(label_id)
        self.original_text = ctk.CTkTextbox(self.canvas, width=560, height=200, wrap="word")
        original_text_id = self.canvas.create_window(500, 300, anchor="center", window=self.original_text, tags="TranslationViewerPage")
        widgets.append(original_text_id)
        translated_label = ctk.CTkLabel(self.canvas, text="Translated English Text", font=("Helvetica", 14))
        translated_label_id = self.canvas.create_window(500, 400, anchor="center", window=translated_label, tags="TranslationViewerPage")
        widgets.append(translated_label_id)
        self.translated_text = ctk.CTkTextbox(self.canvas, width=560, height=200, wrap="word")
        translated_text_id = self.canvas.create_window(500, 550, anchor="center", window=self.translated_text, tags="TranslationViewerPage")
        widgets.append(translated_text_id)
        self.pages["TranslationViewerPage"] = widgets

    def init_history_page(self):
        widgets = []
        title_label = ctk.CTkLabel(self.canvas, text="Translation History", font=("Helvetica", 20))
        title_label_id = self.canvas.create_window(350, 150, anchor="center", window=title_label, tags="HistoryPage")
        widgets.append(title_label_id)
        self.history_textbox = ctk.CTkTextbox(self.canvas, wrap="word", state="normal", width=400, height=200)
        history_textbox_id = self.canvas.create_window(
            500, 350, anchor="center", window=self.history_textbox, tags="HistoryPage"
        )
        widgets.append(history_textbox_id)
        self.download_button = ctk.CTkButton(
            self.canvas, text="Download Selected", font=("Helvetica", 14),
            command=self.download_selected,
            state="disabled"
        )
        download_button_id = self.canvas.create_window(
            500, 600, anchor="center", window=self.download_button, tags="HistoryPage"
        )
        widgets.append(download_button_id)
        self.pages["HistoryPage"] = widgets

    def init_settings_page(self):
        widgets = []
        title_label = ctk.CTkLabel(self.canvas, text="Settings", font=("Helvetica", 20))
        title_label_id = self.canvas.create_window(500, 100, anchor="center", window=title_label, tags="SettingsPage")
        widgets.append(title_label_id)
        mode_label = ctk.CTkLabel(self.canvas, text="Appearance Mode:", font=("Helvetica", 14))
        mode_label_id = self.canvas.create_window(500, 200, anchor="center", window=mode_label, tags="SettingsPage")
        widgets.append(mode_label_id)
        mode_selector = ctk.CTkOptionMenu(self.canvas, values=["Light", "Dark"], command=ctk.set_appearance_mode)
        mode_selector_id = self.canvas.create_window(500, 250, anchor="center", window=mode_selector, tags="SettingsPage")
        widgets.append(mode_selector_id)
        self.pages["SettingsPage"] = widgets

    def show_page(self, page_name):
        for page in self.pages:
            self.canvas.itemconfigure(page, state='hidden')
            for widget_id in self.pages[page]:
                self.canvas.itemconfigure(widget_id, state='hidden')
        if page_name in self.pages:
            self.current_page = page_name
            self.canvas.itemconfigure(page_name, state='normal')
            for widget_id in self.pages[page_name]:
                self.canvas.itemconfigure(widget_id, state='normal')
        if page_name == "HistoryPage":
            self.update_history_content()

    def upload_file(self, event=None):
        global uploaded_file
        uploaded_file = askopenfilename(
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if uploaded_file:
            if not os.path.exists(uploaded_file):
                messagebox.showerror("Error", "Selected file does not exist.")
                return
            
            if not os.access(uploaded_file, os.R_OK):
                messagebox.showerror("Error", "Cannot read selected file. Check permissions.")
                return
            
            print(f"Uploaded file path: {uploaded_file}")
            self.upload_button.configure(text="Processing... Please wait", state="disabled")
            threading.Thread(target=self.process_file).start()

    def process_file(self):
        global uploaded_file, history
        try:
            text_data = extract_text(uploaded_file, dpi=200)
            if not text_data:
                raise ValueError("No text was extracted from the PDF.")

            for item in text_data:
                item["translated_text"] = translate_text(item["text"])

            output_pdf = os.path.splitext(uploaded_file)[0] + "_translated.pdf"
            create_translated_pdf(uploaded_file, output_pdf, text_data)

            history.append({"file": uploaded_file, "output": output_pdf, "date": datetime.datetime.now()})

            self.upload_button.configure(
                text="Download Translated PDF",
                state="normal",
                command=lambda: self.download_translated_pdf(output_pdf),
            )

            messagebox.showinfo("Success", "File translated successfully!")
            self.show_translation_page()
            self.display_translation(text_data)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {e}")
            self.upload_button.configure(text="Upload File", state="normal")

    def download_translated_pdf(self, output_pdf):
        save_path = asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if save_path:
            with open(output_pdf, 'rb') as f_src:
                with open(save_path, 'wb') as f_dst:
                    f_dst.write(f_src.read())
            messagebox.showinfo("Download", "Download successful!")

    def display_translation(self, text_data):
        page_one_data = [item for item in text_data if item["page_number"] == 0]
        original_texts = [item["text"] for item in page_one_data]
        translated_texts = [item["translated_text"] for item in page_one_data]

        self.original_text.delete("1.0", "end")
        self.original_text.insert("1.0", "\n".join(original_texts))
        self.translated_text.delete("1.0", "end")
        self.translated_text.insert("1.0", "\n".join(translated_texts))

    def update_history_content(self):
        self.history_textbox.configure(state="normal")
        self.history_textbox.delete("1.0", "end")
        for idx, entry in enumerate(history):
            file_name = os.path.basename(entry["file"])
            date = entry["date"].strftime("%Y-%m-%d %H:%M:%S")
            self.history_textbox.insert("end", f"{idx+1}. File: {file_name}\nDate: {date}\n\n")
        self.history_textbox.configure(state="disabled")
        if history:
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")

    def download_selected(self):
        selected_text = self.history_textbox.get("sel.first", "sel.last")
        if selected_text:
            idx = int(selected_text.split(".")[0]) - 1
            output_pdf = history[idx]["output"]
            self.download_translated_pdf(output_pdf)
        else:
            messagebox.showwarning("No Selection", "Please select an entry from the history.")

    def batch_upload_files(self):
        """Handle batch file upload"""
        file_paths = askopenfilenames(
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_paths:
            self.batch_upload_button.configure(text="Processing Batch...", state="disabled")
            self.upload_button.configure(state="disabled")
            self.progress_bar.show()
            threading.Thread(target=self.process_batch, args=(file_paths,)).start()

    def process_batch(self, file_paths):
        """Process multiple files in batch"""
        try:
            batch_processor = BatchProcessor(max_workers=3, chunk_size=5)
            
            def update_progress(current, total):
                progress = current / total
                self.progress_bar.set(progress)
                self.update()
            
            results = batch_processor.process_pdf_batch(
                file_paths, 
                progress_callback=update_progress,
                translate_func=translate_text
            )
            
            for result in results:
                if result.get("success"):
                    history.append({
                        "file": result["input"],
                        "output": result["output"],
                        "date": datetime.datetime.now()
                    })
            
            messagebox.showinfo("Batch Processing Complete", 
                              f"Processed {len(results)} files\n"
                              f"Successful: {sum(1 for r in results if r['success'])}\n"
                              f"Failed: {sum(1 for r in results if not r['success'])}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Batch processing error: {e}")
        
        finally:
            self.batch_upload_button.configure(text="Batch Upload", state="normal")
            self.upload_button.configure(state="normal")
            self.progress_bar.set(0)
            self.progress_bar.configure(state="hidden")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = MangaTranslatorApp()
    app.mainloop()
