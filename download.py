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
    
    file_path = Path('pdfs') / filename
    
    # Check if file already exists
    if file_path.exists():
        return file_path, "already_exists"
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(file_path, 'wb') as file, tqdm(desc=filename, total=total_size, unit='B', unit_scale=True) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            pbar.update(len(chunk))
    
    return file_path, "downloaded"

def check_files_exist():
    """Check if both PDF files exist"""
    file_2023 = Path('pdfs') / 'document_2023.pdf'
    file_2024 = Path('pdfs') / 'document_2024.pdf'
    
    return {
        'document_2023.pdf': file_2023.exists(),
        'document_2024.pdf': file_2024.exists(),
        'both_exist': file_2023.exists() and file_2024.exists()
    }

def download_all_pdfs():
    """Create pdfs/ dir and download both PDFs"""
    Path('pdfs').mkdir(exist_ok=True)
    
    results = {}
    
    try:
        # Download 2023 document
        _, status_2023 = download_pdf(os.getenv('LINK_2023'), 'document_2023.pdf')
        results['document_2023.pdf'] = status_2023
    except Exception as e:
        results['document_2023.pdf'] = f"error: {str(e)}"
    
    try:
        # Download 2024 document
        _, status_2024 = download_pdf(os.getenv('LINK_2024'), 'document_2024.pdf')
        results['document_2024.pdf'] = status_2024
    except Exception as e:
        results['document_2024.pdf'] = f"error: {str(e)}"
    
    return results

if __name__ == "__main__":
    results = download_all_pdfs()
    for filename, status in results.items():
        print(f"{filename}: {status}")
