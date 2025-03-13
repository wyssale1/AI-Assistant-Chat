# enhanced_pdf_extractor.py
import os
import pickle
import re
import io
import tempfile
from PIL import Image

# Import PDF processing libraries
try:
    import fitz  # PyMuPDF
except ImportError:
    print("Warning: PyMuPDF not found. Installing...")
    os.system("pip install pymupdf==1.22.5")
    import fitz

try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    print("Warning: OCR dependencies not found. Installing...")
    os.system("pip install pytesseract==0.3.10 pdf2image==1.16.3")
    import pytesseract
    from pdf2image import convert_from_path

# Check if Tesseract is installed
try:
    pytesseract.get_tesseract_version()
except Exception as e:
    print("Warning: Tesseract not found or not properly installed.")
    print("Please install Tesseract using: brew install tesseract")

# Configure image extraction parameters
IMAGE_MIN_SIZE = 100  # Minimum width/height to extract
EXTRACT_IMAGES = True  # Set to False if you only want text

def extract_text_with_layout(pdf_path):
    """Extract text with layout awareness and image processing from PDF."""
    documents = []
    filename = os.path.basename(pdf_path)
    
    try:
        # Open the PDF with PyMuPDF
        doc = fitz.open(pdf_path)
        
        for i, page in enumerate(doc):
            try:
                # Extract text with layout preservation
                text = page.get_text("text")
                html = page.get_text("html")  # Get HTML for structure preservation
                
                # If text extraction yields little or no text, try OCR
                if len(text.strip()) < 50:  # Arbitrary threshold for "too little text"
                    print(f"  Page {i+1} has limited text, trying OCR...")
                    text = ocr_page(pdf_path, i)
                
                # Extract images if enabled
                image_texts = []
                image_descriptions = []
                
                if EXTRACT_IMAGES:
                    # Get images from the page
                    img_list = extract_images_from_page(page)
                    
                    for img_index, img_info in enumerate(img_list):
                        img_data, bbox = img_info
                        
                        # Try to OCR text from the image
                        try:
                            img_pil = Image.open(io.BytesIO(img_data))
                            img_text = pytesseract.image_to_string(img_pil)
                            
                            if img_text.strip():
                                image_texts.append(img_text)
                                image_descriptions.append(f"[Image {i+1}.{img_index+1}: {img_text[:50]}...]")
                        except Exception as e:
                            print(f"  Image OCR error on page {i+1}, image {img_index+1}: {str(e)}")
                
                # Combine all content
                combined_text = text
                
                # Add image descriptions if we have any
                if image_descriptions:
                    combined_text += "\n\nIMAGES ON THIS PAGE:\n" + "\n".join(image_descriptions)
                
                # Detect headings based on font size and styling (from HTML)
                headings = extract_headings_from_html(html)
                heading = headings[0] if headings else ""
                
                # Create the document entry
                documents.append({
                    "content": combined_text,
                    "metadata": {
                        "source": filename,
                        "page": i + 1,
                        "heading": heading,
                        "has_images": len(image_descriptions) > 0,
                        "image_count": len(image_descriptions)
                    }
                })
                
                print(f"  Processed page {i+1}: {len(combined_text)} chars, {len(image_descriptions)} images")
                
            except Exception as e:
                print(f"  Error processing page {i+1}: {str(e)}")
                documents.append({
                    "content": f"[PDF PROCESSING ERROR: {str(e)}]",
                    "metadata": {
                        "source": filename,
                        "page": i + 1,
                        "heading": "ERROR_PAGE"
                    }
                })
        
    except Exception as e:
        print(f"  Failed to process PDF: {str(e)}")
        documents.append({
            "content": f"[FAILED TO PROCESS PDF: {str(e)}]",
            "metadata": {
                "source": filename,
                "page": 0,
                "heading": "ERROR_DOCUMENT"
            }
        })
    
    return documents

def extract_images_from_page(page):
    """Extract images from a PDF page."""
    image_list = []
    
    # Get image list from page
    img_dict = page.get_images(full=True)
    
    for img_index, img_info in enumerate(img_dict):
        xref = img_info[0]
        
        try:
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Get image position on page
            for img_rect in page.get_image_rects(xref):
                bbox = (img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1)
                
            # Store the image and its position
            image_list.append((image_bytes, bbox))
            
        except Exception as e:
            print(f"  Error extracting image: {str(e)}")
    
    return image_list

def extract_headings_from_html(html_content):
    """Extract headings from HTML content based on font size and styling."""
    headings = []
    
    # Look for potential headings - text with large font size or bold formatting
    font_size_pattern = r'font-size:(\d+)px[^>]*>([^<]+)<'
    bold_pattern = r'font-weight:bold[^>]*>([^<]+)<'
    
    # Find large text (likely headings)
    for match in re.finditer(font_size_pattern, html_content):
        size = int(match.group(1))
        text = match.group(2).strip()
        
        # If font size is above 14px (typical heading size), consider it a heading
        if size > 14 and text and len(text) < 100:  # Not too long
            headings.append(text)
    
    # Find bold text (also likely headings)
    for match in re.finditer(bold_pattern, html_content):
        text = match.group(1).strip()
        if text and len(text) < 100 and text not in headings:
            headings.append(text)
    
    # Also look for common heading keywords
    keyword_pattern = r'>([^<]*(Section|Chapter|Part|Installation|Maintenance|Troubleshooting|Configuration)[^<]*)<'
    for match in re.finditer(keyword_pattern, html_content, re.IGNORECASE):
        text = match.group(1).strip()
        if text and len(text) < 100 and text not in headings:
            headings.append(text)
    
    return headings

def ocr_page(pdf_path, page_num):
    """Perform OCR on a specific page of a PDF."""
    try:
        # Convert PDF page to image
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(
                pdf_path, 
                first_page=page_num+1, 
                last_page=page_num+1,
                dpi=300,
                output_folder=temp_dir
            )
            
            if not images:
                return "[OCR ERROR: Could not convert page to image]"
            
            # Perform OCR on the image
            return pytesseract.image_to_string(images[0])
    except Exception as e:
        return f"[OCR ERROR: {str(e)}]"

def process_directory(directory_path):
    """Process all PDFs in a directory."""
    all_documents = []
    processed_files = 0
    failed_files = 0
    
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return all_documents
    
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return all_documents
    
    print(f"Found {len(pdf_files)} PDF files to process.")
    
    for filename in pdf_files:
        file_path = os.path.join(directory_path, filename)
        print(f"Processing {filename}...")
        try:
            documents = extract_text_with_layout(file_path)
            if documents:
                all_documents.extend(documents)
                print(f"  Successfully extracted {len(documents)} document chunks")
                processed_files += 1
            else:
                print(f"  No content extracted from {filename}")
                failed_files += 1
        except Exception as e:
            print(f"  Failed to process {filename}: {str(e)}")
            failed_files += 1
    
    print(f"Processing complete: {processed_files} files processed successfully, {failed_files} files failed")
    
    # Save the extracted documents
    os.makedirs("processed_docs", exist_ok=True)
    with open("processed_docs/extracted_docs.pkl", "wb") as f:
        pickle.dump(all_documents, f)
    
    return all_documents

if __name__ == "__main__":
    docs_dir = "docs"
    all_docs = process_directory(docs_dir)
    print(f"Extracted {len(all_docs)} document chunks")
    print(f"Saved to processed_docs/extracted_docs.pkl")