# Import libraries
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os

'''
# Path of the pdf
PDF_file = 'd.pdf'


# Part #1 : Converting PDF to images


# Store all the pages of the PDF in a variable
pages = convert_from_path(PDF_file, 500)

# Counter to store images of each page of PDF to image
image_counter = 1

# Iterate through all the pages stored above
for page in pages:

	# Declaring filename for each page of PDF as JPG
	# For each page, filename will be:
	# PDF page 1 -> page_1.jpg
	# PDF page 2 -> page_2.jpg
	# PDF page 3 -> page_3.jpg
	# ....
	# PDF page n -> page_n.jpg
	filename = "page_"+str(image_counter)+".jpg"
	
	# Save the image of the page in system
	page.save(filename, 'JPEG')

	# Increment the counter to update filename
	image_counter = image_counter + 1


# Part #2 - Recognizing text from the images using OCR


# 3 Variable to get count of total number of pages
filelimit = image_counter-1

# Creating a text file to write the output
outfile = "out_text.txt"

# Open the file in append mode so that
# All contents of all images are added to the same file
f = open(outfile, "a")

# Iterate from 1 to total number of pages
for i in range(1, filelimit + 1):

	# Set filename to recognize text from
	# Again, these files will be:
	# page_1.jpg
	# page_2.jpg
	# ....
	# page_n.jpg
	filename = "page_"+str(i)+".jpg"
		
	# Recognize the text as string in image using pytesserct
	text = str(((pytesseract.image_to_string(Image.open(filename)))))

	# The recognized text is stored in variable text
	# Any string processing may be applied on text
	# Here, basic formatting has been done:
	# In many PDFs, at line ending, if a word can't
	# be written fully, a 'hyphen' is added.
	# The rest of the word is written in the next line
	# Eg: This is a sample text this word here GeeksF-
	# orGeeks is half on first line, remaining on next.
	# To remove this, we replace every '-\n' to ''.
	text = text.replace('-\n', '')	

	# Finally, write the processed text to the file.
	f.write(text)

# Close the file after writing all the text.
f.close()
'''

# Extraer texto de imagen
filename = 'routing.png'
outfile = 'extractionImagen.txt'

f = open(outfile, 'a')
text = str(((pytesseract.image_to_string(Image.open(filename)))))
text = text.replace('-\n', '')
f.write(text)
f.close()
print('Terminado')


# Extrar texto de pdf, se convierte a imagen y luego extrae el texto
# brew install tesseract
# https://tesseract-ocr.github.io/tessdoc/Installation.html
# https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/

# pdf_file = 'text.pdf'
# pages = convert_from_path(pdf_file, 500)
# image_counter = 1

# for page in pages:
# 	filename = 'pages' + str(image_counter) + 'jpg'
# 	page.save(filename, 'JPEG')
# 	image_counter += 1

# filelimit = image_counter - 1
# outfile = 'extrancionPdf.txt'
# f = open(outfile, 'a')

# for i in range(1, filelimit + 1):
# 	filename = 'page_' + str(i) + '.jpg'
# 	text = str(((pytesseract.image_to_string(Image.open(filename)))))
# 	text = text.replace('-\n', '')
# 	f.write(text)

# f.close()
print('Terminado')