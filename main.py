import pdfplumber
import pytesseract
from PIL import Image
import io
from typing import Dict, List
import json

def extract_pdf_info(pdf_path: str) -> Dict:
    """
    Extracts text and metadata from a PDF file using pdfplumber and OCR for image-only PDFs.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing:
        - text: List of text from each page (using OCR if needed)
        - num_pages: Total number of pages
        - has_images: Boolean indicating if the PDF contains images
    """
    try:
        # Open the PDF file with pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text from each page
            text = []
            has_images = False
            
            for page_num, page in enumerate(pdf.pages, 1):
                # First try to extract text normally
                page_text = page.extract_text()
                
                # If no text is found but there are images, use OCR
                if not page_text and page.images:
                    has_images = True
                    # Convert page to image and use OCR with Japanese language
                    image = page.to_image().original
                    page_text = pytesseract.image_to_string(image, lang='jpn')
                    
                print(f"\nDebug - Page {page_num} text length: {len(page_text or '')}")
                print(f"Debug - First 100 chars of page {page_num} text: {page_text[:100] if page_text else 'No text'}")
                text.append(page_text or '')
                
                # Debug information
                print(f"Page {page_num} char count: {len(page.chars)}")
                print(f"Page {page_num} image count: {len(page.images)}")
                break
            
            return {
                "text": text,
                "num_pages": len(pdf.pages),
                "has_images": has_images
            }
            
    except Exception as e:
        raise Exception(f"Error extracting PDF info: {str(e)}")

def print_pdf_info(pdf_info: Dict):
    """Helper function to print PDF information."""
    print(f"Number of pages: {pdf_info['num_pages']}")
    if pdf_info.get('has_images'):
        print("\nNote: This PDF contains images and OCR was used to extract text")
    print("\nText content:")
    
    # Print text from each page
    for page_num, page_text in enumerate(pdf_info['text'], 1):
        if page_text.strip():  # Only print if there's actual text
            print(f"\nPage {page_num}:")
            # Split text into chunks of 1000 characters for better readability
            chunks = [page_text[i:i+1000] for i in range(0, len(page_text), 1000)]
            for chunk in chunks:
                print(chunk)
                print("-" * 80)  # Add a separator between chunks
            print("=" * 80)  # Add a separator between pages

def main():
    """Main function that handles command-line arguments."""
    import sys
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract text from PDF files.')
    parser.add_argument('pdf_file', nargs='?', help='Path to the PDF file')
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # If no filename is provided as argument, read from stdin
        if args.pdf_file is None:
            args.pdf_file = input("Enter PDF file path: ")
            
        # Extract and print PDF info
        pdf_info = extract_pdf_info(args.pdf_file)
        print_pdf_info(pdf_info)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
