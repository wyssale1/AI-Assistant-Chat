# document_processor.py
"""
Document processor using LLaVA to extract text and analyze images from SMC documentation PDFs.
"""
import os
import fitz  # PyMuPDF
import base64
import requests
import io
from PIL import Image
import pickle
from tqdm import tqdm
import logging
import time

# Import configuration
from config import (
    DOCS_DIR, PROCESSED_DIR, CHUNK_SIZE, CHUNK_OVERLAP,
    EXTRACT_IMAGES, IMAGE_MIN_SIZE, OCR_ENABLED,
    LLAVA_URL, LLAVA_MODEL, LLAVA_TEMPERATURE, LLAVA_CONTEXT_SIZE
)

# Import chunking from langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("document_processor.log"), logging.StreamHandler()]
)
logger = logging.getLogger("document_processor")

def encode_image_to_base64(image_bytes):
    """Convert image bytes to base64 string for API."""
    return base64.b64encode(image_bytes).decode('utf-8')

def process_with_llava(image_bytes, surrounding_text="", page_num=0, source=""):
    """Process an image using LLaVA with surrounding text for context."""
    try:
        # Convert image bytes to base64
        base64_image = encode_image_to_base64(image_bytes)
        
        # Create prompt with contextual information
        prompt = f"""Analyze this technical image from an SMC device manual.
Document: {source}
Page: {page_num}
Surrounding text: {surrounding_text[:LLAVA_CONTEXT_SIZE]}...

Provide a detailed and technical description of what this image shows.
Identify components, connections, and operational principles visible in the diagram.
Be specific about part numbers, labels, and functional descriptions.
"""
        
        # Prepare request for Ollama API with LLaVA model
        request_data = {
            "model": LLAVA_MODEL,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False,
            "options": {
                "temperature": LLAVA_TEMPERATURE
            }
        }
        
        # Call LLaVA API
        response = requests.post(
            LLAVA_URL,
            json=request_data,
            timeout=60  # Longer timeout for image processing
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Error: No response content")
        else:
            return f"Error: API returned status code {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return f"Error processing image: {str(e)}"

def extract_text_around_image(page, bbox, context_size=LLAVA_CONTEXT_SIZE):
    """Extract text surrounding an image for context."""
    # Get all text blocks on the page
    blocks = page.get_text("blocks")
    
    # Filter blocks that are close to the image
    nearby_blocks = []
    for block in blocks:
        block_bbox = block[:4]  # x0, y0, x1, y1
        # Simple proximity check - expand image bbox slightly
        expanded_bbox = (
            bbox[0] - 20, bbox[1] - 20,
            bbox[2] + 20, bbox[3] + 20
        )
        
        # Check if block overlaps with expanded bbox
        if (block_bbox[0] < expanded_bbox[2] and block_bbox[2] > expanded_bbox[0] and
            block_bbox[1] < expanded_bbox[3] and block_bbox[3] > expanded_bbox[1]):
            nearby_blocks.append(block[4])  # The text content is at index 4
    
    # Combine nearby text
    context_text = " ".join(nearby_blocks)
    
    # Trim to context size
    if len(context_text) > context_size:
        context_text = context_text[:context_size] + "..."
        
    return context_text

def extract_headings_from_html(html_content):
    """Extract headings from HTML content based on font size and styling."""
    import re
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
    if not OCR_ENABLED:
        return "[OCR is disabled]"
        
    try:
        # Import required libraries
        import pytesseract
        from pdf2image import convert_from_path
        import tempfile
        
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

def extract_text_with_llava(pdf_path, verbose=True):
    """Extract text and analyze images with LLaVA."""
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
                if OCR_ENABLED and len(text.strip()) < 50:  # Arbitrary threshold for "too little text"
                    if verbose:
                        logger.info(f"  Page {i+1} has limited text, trying OCR...")
                    text = ocr_page(pdf_path, i)
                
                # Extract and analyze images if enabled
                image_descriptions = []
                
                if EXTRACT_IMAGES:
                    # Get images from the page
                    img_list = page.get_images(full=True)
                    
                    for img_index, img_info in enumerate(img_list):
                        try:
                            xref = img_info[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            
                            # Find image position
                            image_bbox = None
                            for img_rect in page.get_image_rects(xref):
                                image_bbox = (img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1)
                            
                            # Get surrounding text for context
                            surrounding_text = ""
                            if image_bbox:
                                surrounding_text = extract_text_around_image(page, image_bbox)
                            
                            # Process with LLaVA
                            if verbose:
                                logger.info(f"  Processing image {img_index+1} on page {i+1} with LLaVA...")
                            
                            image_description = process_with_llava(
                                image_bytes,
                                surrounding_text=surrounding_text,
                                page_num=i+1,
                                source=filename
                            )
                            
                            image_descriptions.append(f"[Image {i+1}.{img_index+1}]: {image_description}")
                            
                        except Exception as e:
                            if verbose:
                                logger.error(f"  Error processing image {img_index+1} on page {i+1}: {str(e)}")
                
                # Combine all content
                combined_text = text
                
                # Add image descriptions if we have any
                if image_descriptions:
                    combined_text += "\n\nIMAGE DESCRIPTIONS:\n" + "\n\n".join(image_descriptions)
                
                # Extract headings from HTML
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
                
                if verbose:
                    logger.info(f"  Processed page {i+1}: {len(combined_text)} chars, {len(image_descriptions)} images")
                
            except Exception as e:
                if verbose:
                    logger.error(f"  Error processing page {i+1}: {str(e)}")
                documents.append({
                    "content": f"[PDF PROCESSING ERROR: {str(e)}]",
                    "metadata": {
                        "source": filename,
                        "page": i + 1,
                        "heading": "ERROR_PAGE"
                    }
                })
        
    except Exception as e:
        if verbose:
            logger.error(f"  Failed to process PDF: {str(e)}")
        documents.append({
            "content": f"[FAILED TO PROCESS PDF: {str(e)}]",
            "metadata": {
                "source": filename,
                "page": 0,
                "heading": "ERROR_DOCUMENT"
            }
        })
    
    return documents

def chunk_documents(documents):
    """Split documents into smaller chunks for better retrieval."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunked_documents = []
    
    for doc in documents:
        chunks = text_splitter.split_text(doc["content"])
        for chunk in chunks:
            chunked_documents.append({
                "content": chunk,
                "metadata": doc["metadata"].copy()
            })
    
    return chunked_documents

def process_directory(directory_path=DOCS_DIR, verbose=True):
    """Process all PDFs in a directory using LLaVA for image analysis."""
    all_documents = []
    processed_files = 0
    failed_files = 0
    
    if not os.path.exists(directory_path):
        logger.error(f"Directory {directory_path} does not exist.")
        return all_documents
    
    pdf_files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory_path}")
        return all_documents
    
    logger.info(f"Found {len(pdf_files)} PDF files to process.")
    
    for filename in pdf_files:
        file_path = os.path.join(directory_path, filename)
        logger.info(f"Processing {filename}...")
        
        try:
            # Extract text and analyze images with LLaVA
            start_time = time.time()
            documents = extract_text_with_llava(file_path, verbose=verbose)
            
            if documents:
                all_documents.extend(documents)
                processing_time = time.time() - start_time
                logger.info(f"  Successfully extracted {len(documents)} document chunks in {processing_time:.2f} seconds")
                processed_files += 1
            else:
                logger.warning(f"  No content extracted from {filename}")
                failed_files += 1
                
        except Exception as e:
            logger.error(f"  Failed to process {filename}: {str(e)}")
            failed_files += 1
    
    logger.info(f"Processing complete: {processed_files} files processed successfully, {failed_files} files failed")
    
    # Save the extracted documents
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    with open(os.path.join(PROCESSED_DIR, "extracted_docs.pkl"), "wb") as f:
        pickle.dump(all_documents, f)
    
    # Create chunks
    chunked_docs = chunk_documents(all_documents)
    
    with open(os.path.join(PROCESSED_DIR, "chunked_docs.pkl"), "wb") as f:
        pickle.dump(chunked_docs, f)
    
    logger.info(f"Created {len(chunked_docs)} chunks from {len(all_documents)} documents")
    
    return chunked_docs

if __name__ == "__main__":
    chunked_docs = process_directory()
    logger.info(f"Processed {len(chunked_docs)} total chunks")