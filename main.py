import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def download_pdf(url, filename):
    """Download PDF to pdfs/ directory"""
    if not url:
        raise ValueError(f"URL not found for {filename}")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    file_path = Path('pdfs') / filename
    total_size = int(response.headers.get('content-length', 0))
    
    with open(file_path, 'wb') as file, tqdm(desc=filename, total=total_size, unit='B', unit_scale=True) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            pbar.update(len(chunk))
    
    return file_path

def download_all_pdfs():
    """Create pdfs/ dir and download both PDFs"""
    Path('pdfs').mkdir(exist_ok=True)
    
    download_pdf(os.getenv('LINK_2023'), 'document_2023.pdf')
    download_pdf(os.getenv('LINK_2024'), 'document_2024.pdf')

if __name__ == "__main__":
    download_all_pdfs()
