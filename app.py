import streamlit as st
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import spacy

# Initialize PaddleOCR with English recognition model
ocr = PaddleOCR()

# Load the custom-trained SpaCy NER model from the output directory
nlp = spacy.load("output_model55")

# Function to preprocess an image
def preprocess_image(image):
    image = image.convert('L')  # Convert to grayscale
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    image = image.filter(ImageFilter.SHARPEN)
    return image

# Function to sort OCR results based on the position of bounding boxes
def sort_ocr_results(ocr_results):
    boxes_and_text = [(line[0], line[1][0]) for result in ocr_results for line in result]
    boxes_and_text.sort(key=lambda x: x[0][0][1])
    return boxes_and_text

# Function to group text elements by lines based on y-coordinate
def group_text_by_lines(sorted_results, y_threshold=10):
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

# Function to combine SpaCy NER results
def combine_spacy_entities(doc):
    combined_entities = []
    for ent in doc.ents:
        combined_entities.append({"entity_group": ent.label_, "word": ent.text})
    return combined_entities

# Function to perform OCR and NER on a PDF
def process_pdf(pdf_path):
    pages = convert_from_path(pdf_path, dpi=500)  # Convert PDF pages to images
    results = []

    for i, page in enumerate(pages):
        processed_image = preprocess_image(page)  # Preprocess the image
        
        ocr_results = ocr.ocr(np.array(processed_image))  # Perform OCR with PaddleOCR
        
        sorted_results = sort_ocr_results(ocr_results)  # Sort results by bounding box positions
        
        lines = group_text_by_lines(sorted_results)  # Group text elements by lines
        
        page_text = "\n".join([" ".join(line) for line in lines])  # Collect text lines for NER
        
        doc = nlp(page_text)  # Perform NER using SpaCy
        
        combined_entities = combine_spacy_entities(doc)  # Process and combine NER results

        results.append((page_text, combined_entities))

    return results

# Streamlit app
st.title("PDF OCR and NER")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("Processing PDF...")
    ocr_ner_results = process_pdf("temp.pdf")

    for i, (ocr_output, ner_results) in enumerate(ocr_ner_results):
        st.subheader(f"Page {i+1}")
        st.text_area("OCR Output", ocr_output, height=300)

        st.subheader("NER Results")
        for entity in ner_results:
            st.write(f"Entity: **{entity['word']}**, Group: **{entity['entity_group']}**")

        st.markdown("---")

# Run the Streamlit app with `streamlit run app.py`
