
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

def clean_text(text):
    cleaned_lines = []
    for line in text.split('\n'):
        # Remove unwanted characters, keeping only letters and numbers
        cleaned_line = re.sub(r'[^0-9A-Za-z\u0621-\u064A\s]+', '', line)
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line)
    # return cleaned_lines
    return '\n'.join(cleaned_lines)
# Save the extracted text
with open('extracted_text.txt', 'w', encoding='utf-8') as file:
    # Apply the correction and autocorrect
    # final_output = process_text(extracted_text)
    final_output = clean_text(extracted_text)
    file.write(final_output)



#======================[enhancement after extraction]=======================
from ar_corrector.corrector import Corrector
corr = Corrector()


from language_detector import detect_language

import re
from textblob import TextBlob

after_correct=[]
file = open("extracted_text.txt", "r",encoding='utf-8')

def replace_page_number(line):
    page_pattern = re.compile(r'^Page\s*(\d+)', re.IGNORECASE)
    match = page_pattern.match(line)
    if match:
        page_number = match.group(1)
        return f'==================[page number: {page_number}]======='
    return line

while True:
	content=file.readline()
	if not content:
		break
	line=[]
	for word in content.split(" "):
		if(len(word)==1):
			continue
		if detect_language(word) == 'Arabic':
			if re.search(r'[a-zA-Z0-9]',word):
				word=re.sub(r'[^a-zA-Z0-9\s]', '', word)
			word=corr.contextual_correct(word)
			if word:
				line.append(word)
			# line.append(corr.spell(word))
		else:
			if (len(word)==2 and word[0]==word[1]):
				continue
			elif  word.isupper():
				line.append(word)
			else:
				word=TextBlob(word).correct()
				line.append(str(word))
	after_correct.append(' '.join(line))

file.close()
words=[]
for line in after_correct:
	words.append(replace_page_number(line))
with open('extracted_text2.txt', 'w', encoding='utf-8') as file:
	file.write(''.join(words))
