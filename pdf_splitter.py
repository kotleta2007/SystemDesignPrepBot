import re
import os
from pathlib import Path
import string

def clean_filename(title):
    """Clean title to make it a valid filename"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in title if c in valid_chars)
    filename = filename.replace(' ', '_').replace('?', '').replace(':', '').replace('(', '').replace(')', '')
    return filename[:60]

def find_article_starts(pdf_path):
    """Find article start pages by looking for large/colorful text at page tops"""
    try:
        import pdfplumber
    except ImportError:
        print("Installing pdfplumber...")
        os.system("uv add pdfplumber")
        import pdfplumber
    
    article_starts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Scanning {len(pdf.pages)} pages for large/colorful headers...")
        
        for page_num, page in enumerate(pdf.pages):
            # Skip first few pages (cover, TOC, etc.)
            if page_num < 7:
                continue
                
            try:
                # Get characters with formatting info
                chars = page.chars
                
                if not chars:
                    continue
                
                # Look at the top portion of the page (first 15% vertically)
                page_height = page.height
                top_chars = [c for c in chars if c['top'] < page_height * 0.15]
                
                if not top_chars:
                    continue
                
                # Check for large font sizes (typically used for headers)
                large_chars = [c for c in top_chars if c.get('size', 0) > 14]
                
                # Check for colored text (non-black)
                colored_chars = [c for c in top_chars if c.get('non_stroking_color') != (0, 0, 0)]
                
                # If we have BOTH large AND colored text at the top, it's likely a header
                if large_chars and colored_chars:
                    # Extract the text from these formatted characters
                    top_text = page.extract_text()
                    if top_text:
                        lines = top_text.strip().split('\n')
                        first_line = lines[0].strip() if lines else ""
                        
                        if len(first_line) > 5:  # Basic length check only
                            article_starts.append((page_num + 1, first_line))  # +1 for 1-based page numbers
                            print(f"Page {page_num + 1}: {first_line}")
                            print(f"  - Large chars: {len(large_chars)}, Colored chars: {len(colored_chars)}")
                
            except Exception as e:
                print(f"Error processing page {page_num + 1}: {e}")
                continue
    
    return article_starts

def split_pdf_by_headers(pdf_path, output_dir):
    """Split PDF based on article header detection"""
    from pypdf import PdfReader, PdfWriter
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    article_starts = find_article_starts(pdf_path)
    print(f"\nFound {len(article_starts)} article starts")
    
    if len(article_starts) < 5:
        print("Too few articles found, something might be wrong!")
        return
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    for i, (start_page, title) in enumerate(article_starts):
        # Determine end page
        if i + 1 < len(article_starts):
            end_page = article_starts[i + 1][0] - 1
        else:
            end_page = total_pages
        
        writer = PdfWriter()
        
        # Add pages (convert to 0-based indexing)
        pages_added = 0
        for page_num in range(start_page - 1, min(end_page, total_pages)):
            if 0 <= page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
                pages_added += 1
        
        if pages_added > 0:
            filename = f"{start_page:03d}_{clean_filename(title)}.pdf"
            output_path = Path(output_dir) / filename
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"Created: {filename} ({pages_added} pages: {start_page}-{end_page})")

def process_2023_document():
    """Process the 2023 document and split it into articles"""
    pdf_path = "pdfs/document_2023.pdf"
    output_dir = "pdfs/articles_2023"
    
    if not Path(pdf_path).exists():
        print(f"PDF not found: {pdf_path}")
        return
    
    print(f"Processing {pdf_path}...")
    split_pdf_by_headers(pdf_path, output_dir)
    print(f"\nDone! Articles saved to {output_dir}/")

if __name__ == "__main__":
    process_2023_document()
