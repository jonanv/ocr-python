# pip3.6 install ocrmypdf
# ==11.7.3
# pip3.6 install pdfplumber
# ==0.5.27
# pip3.6 install requests
# ==2.25.1

# macOS = brew install ocrmypdf

import os

# import requests
import pdfplumber

# def download_file(url):
#     local_filename = url.split('/')[-1]
    
#     with requests.get(url) as r:
#         assert r.status_code == 200, f'error, status code is {r.status_code}'
#         with open(local_filename, 'wb') as f:
#             f.write(r.content)
        
#     return local_filename

# Para descargar el archivo desde la web
# invoice = 'https://bit.ly/2UJgUpO'
# invoice_pdf = download_file(invoice)

# Cuando el archivo esta local
invoice = 'scanned.pdf'

# Lee el archivo
with pdfplumber.open(invoice) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    print(text)
    print(page)

# Convierte la imagen a texto con ocrmypdf
os.system(f'ocrmypdf {invoice} output.pdf')

with pdfplumber.open('output.pdf') as pdf:
    page = pdf.pages[0]
    text = page.extract_text(x_tolerance=2)
    print(text)