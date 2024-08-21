import paddleocr
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

class POCR:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.ocr = PaddleOCR()

    def preprocess_image(self, image):
        # Convert PIL Image to NumPy array
        image = np.array(image)
        
        # Convert to grayscale
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Denoise image
        image = cv2.fastNlMeansDenoising(image, None, 30, 7, 21)
        
        # Enhance contrast
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Contrast(pil_image)
        pil_image = enhancer.enhance(2)
        image = np.array(pil_image)
        
        # Sharpen image
        pil_image = Image.fromarray(image)
        pil_image = pil_image.filter(ImageFilter.SHARPEN)
        image = np.array(pil_image)
        
        # Apply the Projection Profile method to detect and correct skew
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    def sort_ocr_results(self, ocr_results):
        boxes_and_text = [(line[0], line[1][0]) for result in ocr_results for line in result]
        boxes_and_text.sort(key=lambda x: x[0][0][1])
        return boxes_and_text

    def group_text_by_lines(self, sorted_results, y_threshold=50):
        lines = []
        current_line = []
        last_y = -float('inf')

        for bbox, text in sorted_results:
            current_y = bbox[0][1]
            if abs(current_y - last_y) > y_threshold:
                if current_line:
                    lines.append(current_line)
                current_line = [text]
            else:
                current_line.append(text)
            last_y = current_y

        if current_line:
            lines.append(current_line)
        

        return lines

    def perform_ocr(self):
        pages = convert_from_path(self.pdf_path, dpi=500)  # Convert PDF pages to images

        for i, page in enumerate(pages):
            print(f"Processing page {i+1}")
            processed_image = self.preprocess_image(page)  # Preprocess the image
            
            ocr_results = self.ocr.ocr(np.array(processed_image))  # Perform OCR with PaddleOCR
            
            sorted_results = self.sort_ocr_results(ocr_results)  # Sort results by bounding box positions
            
            lines = self.group_text_by_lines(sorted_results)  # Group text elements by lines
            
            page_text = "\n".join([" ".join(line) for line in lines])  # Collect text lines for output
            
            # print(f"OCR Output for page {i+1}:\n{page_text}\n")  # Print OCR text
            return page_text

# Example usage:
# pdf_path = '/home/praadnyah/p8/annotations/C2.pdf'
# pdf_processor = POCR(pdf_path)
# pdf_processor.perform_ocr()
