import dateparser
from dateparser.search import search_dates

date = dateparser.parse('Jueves 04 de Febrero del 2021', languages=['es'])
print(date)

date_search = search_dates('The first artificial Earth satellite was launched on 4 October 1957.', add_detected_language=True)
print(date_search)