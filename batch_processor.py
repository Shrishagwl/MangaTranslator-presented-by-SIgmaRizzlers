import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from pdf_processor import extract_text, create_translated_pdf

class BatchProcessor:
    def __init__(self, max_workers=3, chunk_size=10):
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.processing_lock = Lock()
        self.current_progress = 0
        self.total_files = 0
        
    def process_pdf_batch(self, file_paths, translate_func=None):
        """Process multiple PDF files in batches"""
        self.total_files = len(file_paths)
        self.current_progress = 0
        
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for i in range(0, len(file_paths), self.chunk_size):
                chunk = file_paths[i:i + self.chunk_size]
                chunk_futures = [executor.submit(self._process_single_file, file_path, translate_func) 
                               for file_path in chunk]
                
                for future in chunk_futures:
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                    except Exception as e:
                        print(f"Error processing file: {e}")
                
        return results
    
    def _process_single_file(self, file_path, translate_func):
        """Process a single PDF file"""
        try:
            text_data = extract_text(file_path)
            
            if translate_func:
                for item in text_data:
                    item["translated_text"] = translate_func(item["text"])
            
            output_pdf = os.path.splitext(file_path)[0] + "_translated.pdf"
            create_translated_pdf(file_path, output_pdf, text_data)
            
            return {"input": file_path, "output": output_pdf, "success": True}
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return {"input": file_path, "error": str(e), "success": False} 
