import dateparser
from dateparser.search import search_dates

date = dateparser.parse('Jueves 04 de Febrero del 2021', languages=['es'])
print(date)

date_search = search_dates('The first artificial Earth satellite was launched on 4 October 1957.', add_detected_language=True)
print(date_search)


# Ejemplo de lectura de archivo pdf y obtencion de fechas

# file = 'files/08. AUTO NOMBRA CURADOR.pdf'
# with pdfplumber.open(file) as pdf:
#     page = pdf.pages[0]
#     text = page.extract_text()
# print(text)
# print()

# # matches = datefinder.find_dates(matches)
# matches = search_dates(text, languages=['es'])
# new_matches = list()
# for match in matches:
#     if(len(match[0]) > 5):
#         new_matches.append(match[1])
#         print(match)
# print(new_matches)

# print(get_creation_date_format(new_matches[0]))