# import cv2
# import pytesseract
# import numpy as np
#
# pytesseract.pytesseract.tesseract_cmd = r"D:\ahmed\PhD\tesseract.exe"
#
# # Load image, grayscale, Otsu's threshold
# image = cv2.imread('img.png')
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
#
# # Morph open to remove noise
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
# opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
#
# # Find contours and remove small noise
# cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# cnts = cnts[0] if len(cnts) == 2 else cnts[1]
# for c in cnts:
#     area = cv2.contourArea(c)
#     if area < 50:
#         cv2.drawContours(opening, [c], -1, 0, -1)
#
# # Invert and apply slight Gaussian blur
# result = 255 - opening
# result = cv2.GaussianBlur(result, (3,3), 0)
#
# # Perform OCR
# data = pytesseract.image_to_string(result, lang='eng', config='--psm 6')
# print(data)
#
# cv2.imshow('thresh', thresh)
# cv2.imshow('opening', opening)
# cv2.imshow('result', result)
# cv2.waitKey()

from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re
from difflib import get_close_matches

pytesseract.pytesseract.tesseract_cmd = r"D:\ahmed\PhD\tesseract.exe"

# Function to enhance image quality
def enhance_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpened = cv2.filter2D(thresh, -1, kernel)
    return sharpened

# Function to extract text with both Arabic and English support
def extract_text_from_image(image, lang='ara+eng'):
    custom_config = r'--oem 3 --psm 6 -l ' + lang
    text = pytesseract.image_to_string(image, config=custom_config)
    return text

# Main processing function
def process_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    extracted_text = ""

    for i, image in enumerate(images):
        enhanced_image = enhance_image(image)
        text = extract_text_from_image(Image.fromarray(enhanced_image))
        extracted_text += f"Page {i+1}:\n{text}\n\n"

    return extracted_text

# Path to your PDF
pdf_path = 'files.pdf'

# Process the PDF and extract text
extracted_text = process_pdf(pdf_path)


# Dictionary for known words (simplified for demonstration)
known_words_en = {
    "Digital": "Digital", "Discover": "Discover", "number": "number", "VAT": "VAT",
    "Invoice": "Invoice", "Total": "Total", "Amount": "Amount"
}
known_words_ar = {
    "الرقم": "الرقم", "الضريبي": "الضريبي", "فاتورة": "فاتورة", "الاجمالي": "الإجمالي",
    "قيمة": "قيمة", "الخصم": "الخصم", "المبلغ": "المبلغ"
}
from spellchecker import SpellChecker
from camel_tools.spelling import SpellingReplacer
# Initialize spell checkers
spell_en = SpellChecker(language='en')
replacer = SpellingReplacer()

def clean_text(text):
    cleaned_lines = []
    for line in text.split('\n'):
        # Remove unwanted characters, keeping only letters and numbers
        cleaned_line = re.sub(r'[^0-9A-Za-z\u0621-\u064A\s]+', '', line)
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line)
    # return cleaned_lines
    return '\n'.join(cleaned_lines)

def correct_arabic(text):
    # Use Camel Tools for Arabic spelling correction
    corrected_text = replacer.replace(text)
    return corrected_text

def correct_english(text):
    words = text.split()
    corrected_words = [spell_en.candidates(word).pop() if spell_en.unknown([word]) else word for word in words]
    return ' '.join(corrected_words)

def process_text(text):
    cleaned_lines = clean_text(text)
    corrected_lines = []
    for line in cleaned_lines:
        if any(char.isalpha() for char in line):
            if re.search(r'[\u0621-\u064A]', line):  # Check for Arabic characters
                corrected_lines.append(correct_arabic(line))
            else:
                corrected_lines.append(correct_english(line))
    return '\n'.join(corrected_lines)
# Save the extracted text
with open('extracted_text.txt', 'w', encoding='utf-8') as file:
    # Apply the correction and autocorrect
    # final_output = process_text(extracted_text)
    final_output = clean_text(extracted_text)
    # corrected_text = correct_extracted_text(extracted_text)
    autocorrected_text = autocorrect(final_output, known_words_en, known_words_ar)
    file.write(autocorrected_text)

print("Text extraction completed.")