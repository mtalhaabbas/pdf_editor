import fitz
from typing import Dict, List
import json
import io
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR libraries not available. Install pytesseract and opencv-python for image text detection.")

class PDFEditor:
    def __init__(self, pdf_path: str):
        self.doc = fitz.open(pdf_path)
        self.path = pdf_path
    
    def get_page_count(self) -> int:
        return len(self.doc)
    
    def get_page_text_elements(self, page_num: int, include_ocr: bool = True) -> List[Dict]:
        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        elements = []
        
        print(f"\n=== Analyzing page {page_num} ===")
        print(f"Total blocks found: {len(blocks)}")
        
        for idx, block in enumerate(blocks):
            block_type = block.get("type")
            print(f"Block {idx}: type={block_type}", end="")
            
            # Process text blocks
            if block_type == 0 and "lines" in block:
                print(f" (TEXT BLOCK with {len(block['lines'])} lines)")
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span.get("text", "").strip()
                        if (text and 
                            span.get("font") and 
                            span.get("size", 0) > 0 and
                            span.get("size", 0) < 200):
                            
                            print(f"  - Text: '{text[:30]}...' Font: {span['font']} Size: {span['size']}")
                            
                            elements.append({
                                "text": span["text"],
                                "bbox": span["bbox"],
                                "x": span["bbox"][0],
                                "y": span["bbox"][1],
                                "width": span["bbox"][2] - span["bbox"][0],
                                "height": span["bbox"][3] - span["bbox"][1],
                                "font": span["font"],
                                "size": span["size"],
                                "color": span["color"],
                                "flags": span["flags"],
                                "origin": span["origin"],
                                "type": "text"
                            })
            
            # Process image blocks with OCR
            elif block_type == 1 and include_ocr and OCR_AVAILABLE:
                print(f" (IMAGE BLOCK - attempting OCR)")
                try:
                    ocr_elements = self._extract_text_from_image_block(page, block, page_num)
                    elements.extend(ocr_elements)
                    print(f"  - Extracted {len(ocr_elements)} text regions from image")
                except Exception as e:
                    print(f"  - OCR failed: {e}")
            
            elif block_type == 1:
                print(f" (IMAGE BLOCK - OCR not available)")
            else:
                print(f" (UNKNOWN TYPE - skipped)")
        
        print(f"Total text elements extracted: {len(elements)}\n")
        return elements
    
    def render_page_image(self, page_num: int, zoom: float = 2.0) -> bytes:
        page = self.doc[page_num]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        return pix.tobytes("png")
    
    def replace_text_at_bbox(self, page_num: int, bbox: List[float], old_text: str, new_text: str, 
                            font: str, size: float, color: int, flags: int, origin: tuple, element_type: str = "text"):
        page = self.doc[page_num]
        rect = fitz.Rect(bbox)
        
        # Convert color from integer to RGB tuple
        if isinstance(color, int):
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            color_tuple = (r/255, g/255, b/255)
        else:
            color_tuple = (0, 0, 0)  # Default black
        
        # Map font flags to determine style
        is_bold = flags & 2**4  # Bold flag
        is_italic = flags & 2**1  # Italic flag
        
        # Get the best matching font
        fontname = self._get_font_name(font, is_bold, is_italic)
        
        if element_type == "ocr":
            # For OCR text (from images), draw a white rectangle to cover the image area
            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), width=0)
        else:
            # For regular text, use redaction
            page.add_redact_annot(rect, fill=(1, 1, 1))
            page.apply_redactions()
        
        # Insert new text with preserved formatting
        try:
            rc = page.insert_text(
                origin,
                new_text,
                fontname=fontname,
                fontsize=size,
                color=color_tuple
            )
            if rc < 0:
                # If insert_text fails, try with default font
                page.insert_text(
                    origin,
                    new_text,
                    fontname='Helvetica',
                    fontsize=size,
                    color=color_tuple
                )
        except Exception as e:
            print(f"Error inserting text: {e}")
            # Fallback to default Helvetica if font fails
            page.insert_text(
                origin,
                new_text,
                fontname='Helvetica',
                fontsize=size,
                color=color_tuple
            )
        
        return True
    
    def _extract_text_from_image_block(self, page, block, page_num: int) -> List[Dict]:
        """Extract text from image blocks using OCR"""
        if not OCR_AVAILABLE:
            return []
        
        elements = []
        bbox = block["bbox"]
        rect = fitz.Rect(bbox)
        
        # Extract image from the block
        pix = page.get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
        img_data = pix.tobytes("png")
        
        # Convert to PIL Image
        img = Image.open(io.BytesIO(img_data))
        
        # Convert to numpy array for OpenCV
        img_np = np.array(img)
        
        # Preprocess image for better OCR
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        # Apply thresholding to get better text detection
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Use pytesseract to get detailed text data
        ocr_data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        
        # Process each detected text element
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = int(ocr_data['conf'][i])
            
            # Only include text with reasonable confidence (>30)
            if text and conf > 30:
                # Calculate actual position in PDF coordinates
                x = bbox[0] + (ocr_data['left'][i] / 2)  # Divide by 2 because we used 2x zoom
                y = bbox[1] + (ocr_data['top'][i] / 2)
                w = ocr_data['width'][i] / 2
                h = ocr_data['height'][i] / 2
                
                # Estimate font size from height
                font_size = h * 0.8  # Approximate
                
                elements.append({
                    "text": text,
                    "bbox": [x, y, x + w, y + h],
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h,
                    "font": "Helvetica",  # Default font for OCR text
                    "size": font_size,
                    "color": 0,  # Black
                    "flags": 0,
                    "origin": (x, y + h),  # Bottom-left corner
                    "type": "ocr",
                    "confidence": conf
                })
        
        return elements
    
    def _get_font_name(self, original_font: str, is_bold: bool, is_italic: bool) -> str:
        """Map original font to available PyMuPDF font"""
        font_lower = original_font.lower()
        
        # Check for common font families and their variants
        if 'times' in font_lower:
            if is_bold and is_italic:
                return 'Times-BoldItalic'
            elif is_bold:
                return 'Times-Bold'
            elif is_italic:
                return 'Times-Italic'
            return 'Times-Roman'
        
        elif 'helvetica' in font_lower or 'arial' in font_lower or 'sans' in font_lower:
            if is_bold and is_italic:
                return 'Helvetica-BoldOblique'
            elif is_bold:
                return 'Helvetica-Bold'
            elif is_italic:
                return 'Helvetica-Oblique'
            return 'Helvetica'
        
        elif 'courier' in font_lower or 'mono' in font_lower:
            if is_bold and is_italic:
                return 'Courier-BoldOblique'
            elif is_bold:
                return 'Courier-Bold'
            elif is_italic:
                return 'Courier-Oblique'
            return 'Courier'
        
        elif 'symbol' in font_lower:
            return 'Symbol'
        
        elif 'zapf' in font_lower:
            return 'ZapfDingbats'
        
        # Try to detect style from font name itself
        if 'bold' in font_lower and 'italic' in font_lower:
            if 'times' in font_lower:
                return 'Times-BoldItalic'
            elif 'courier' in font_lower:
                return 'Courier-BoldOblique'
            return 'Helvetica-BoldOblique'
        elif 'bold' in font_lower:
            if 'times' in font_lower:
                return 'Times-Bold'
            elif 'courier' in font_lower:
                return 'Courier-Bold'
            return 'Helvetica-Bold'
        elif 'italic' in font_lower or 'oblique' in font_lower:
            if 'times' in font_lower:
                return 'Times-Italic'
            elif 'courier' in font_lower:
                return 'Courier-Oblique'
            return 'Helvetica-Oblique'
        
        # Default to Helvetica (most common sans-serif)
        return 'Helvetica'
    
    def save(self, output_path: str):
        # Use garbage collection and deflate for clean save
        self.doc.save(output_path, garbage=4, deflate=True, clean=True)
    
    def close(self):
        self.doc.close()
