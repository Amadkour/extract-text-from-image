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


jumb = True
while True:
	content=file.readline()
	if not content:
		break
	line=[]
	lines=content.split()
	for i, word in enumerate(lines):
		if word=='Page' and lines[i+1]=='81':
			jumb=False
		if ( len(word) == 1) or(len(word) == 2 and word[0] == word[1] and  not word.isupper()) or jumb:
			continue
		elif word=='Page':
			line.append(f"==================# Page Number:" )
		elif detect_language(word) == 'Arabic':
			if re.search(r'[a-zA-Z0-9]',word):
				word=re.sub(r'[^a-zA-Z0-9\s]', '', word)
			word=corr.contextual_correct(word)
			if word:
				line.append(word)
		else:
			if  word.isupper():
				line.append(word)
			elif len(word)==1:
				continue
			elif len(word)==2 and word[0]==word[1] and not word.isupper():
				continue
			else:
				word=TextBlob(word).correct()
				line.append(str(word))
	if(len(line)>0):
		after_correct.append(' '.join(line))

file.close()
words=[]
for line in after_correct:
	words.append(replace_page_number(line))
with open('cleaned_extracted_15_page.txt', 'w', encoding='utf-8') as file:
	file.write('\n'.join(words))
