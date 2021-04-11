# get_doc_info.py

from PyPDF2 import PdfFileReader
from unicodedata import normalize
import os
import copy
import re
import unicodedata
import numpy as np
import pandas as pd
from datetime import datetime
import datefinder
import dateparser
from dateparser.search import search_dates
import pdfplumber

# Metodo que permite obtener la informacion de metadatos del archivo
def get_metadata(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
    
    author = info.author
    creator = info.creator
    producer = info.producer
    subject = info.subject
    title = info.title
        
    # for key in info:
    #     print (key, ":", info[key])

    # print(info)
    return info

# Metodo que normaliza los medatatos de los pdfs para que todos los archivos tengan las mismas propiedades
def normalize_metadata(metadata):
    info_normalize = {
        'creator': exist_prop(metadata, '/Creator'),
        'producer': exist_prop(metadata, '/Producer'),
        'creationDate': exist_prop(metadata, '/CreationDate'),
        'modificationDate': exist_prop(metadata, '/ModDate'),
        'title': exist_prop(metadata, '/Title'),
        'author': exist_prop(metadata, '/Author'),
        'subject': exist_prop(metadata, '/Subject'),
        'keywords': exist_prop(metadata, '/Keywords')
    }
    return info_normalize

# Metodo que determina si la llave existe en el diccionario, retorna vacio en caso de no existir
def exist_prop(metadata, key):
    if(metadata.get(key)):
        return metadata[key]
    else:
        return ''

# Metodo que obtiene el contenido de la primera pagina del archivo
def get_content_file(path):
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    return text

# Metodo que lee y recupera la informacion de los metadatos con ayuda del metodo (get content file)
def read_and_recover_information(metadata_normalized, path):
    # TODO: Archivos sin fecha de cracion y modifiacion en metadatos
    if(metadata_normalized['creationDate'] == ''):
        print('NO TIENE FECHA DE CREACION DEBE DE LLAMAR A OTRO METODO QUE LEA EL PDF Y RECUPERE LA INFO')
        print()
        text = get_content_file(path)
        print(text)

        if(str(text) != 'None'):
            # matches = datefinder.find_dates(text, source=False)
            matches = search_dates(text, languages=['es'])
            new_matches = list()
            for match in matches:
                new_matches.append(match[1])
                print(match)
            print(new_matches)
            # TODO: Implementar algoritmo que determine la menor fecha (OJO revisar bien (08. AUTO NOMBRA CURADOR.pdf))
            date = get_creation_date_format(new_matches[0]) # D:20201113165700 formato de la fecha de los metadatos
            metadata_normalized['creationDate'] = date
        else:
            # TODO: Metodo que analiza la informacion de la imagen y recupera la fecha
            print('DEBE DE LLAMAR A OTRO METETODO QUE ANALIZARA LA IMAGEN DEL PDF')
    return metadata_normalized

# Metodo que determina si el archivo esta protegido
def is_locked(file):
    with open(file, 'rb') as f:
        pdf = PdfFileReader(f)

    if(pdf.isEncrypted):
        return True
    else:
        return False

# Metodo que renombra los nombres de los archivos
def rename_file(file, file_rename):
    os.rename(file, file_rename)

# Metodo que retorna la variable con el nombre de la carpeta
def folder():
	# carpeta = 'HERRAMIENTAS EXCEL/1220190007900 Prueba 1/CUADERNO PRINCIPAL/'
	carpeta = 'HERRAMIENTAS EXCEL/1220190007900 Prueba 2/CUADERNO PRINCIPAL/'
	return carpeta

# Metodo que retorna una lista con los archivos del folder
def list_files(folder):
	list_files = os.listdir(folder)
	return list_files

# Metodo que lista los archivos en el folder y recorre cada archivo
def show_metadata():
    files = list_files(folder())
    copyFiles = copy.deepcopy(files) # Copia del arreglo original
    all_metadata = ''
    list_metadata_dates = list()

    for x in range(len(files)):
        print(str(x+1) + ". " + files[x])

        # NOMBRE DEL ARCHIVO
        # TODO: Crear metodo que haga todo el proceso de modificar el nombre con los metodos que se utilizan aca
        file = remove_extension(files[x]) # Elimina la extension
        file = normalize_accents(file) # Elimina acentos
        count_character_file = count_character(file) # Cantidad de caracteres
        print('Valido: ' + str(count_character_file) + ', Caracteres: ' + str(len(file)))
        file = str(file.title()) # Capitalizacion
        print('Capitalizacion: ' + file)

        date = get_date(file) # Retorna la fecha del archivo formateada si tiene
        # TODO: Regla de los numeros al principio antecedidos por cero
        # TODO: Regla de las preposiciones en el nombre (Diccionario)

        file = remove_special_characters(file.title()) # Elimina caracteres especiales
        file = remove_numbers(file) # Elimina numeros de la cadena
        file = file + date

        print('SALIDA: ' + file)

        # CONTENIDO DEL ARCHIVO
        path = folder() + files[x]
        print('Encriptado: ' + str(is_locked(path)))

        print()

        if(is_locked(path)):
            # TODO: Archivos protegidos (unlocked - protected - unsecured)
            print('EL ARCHIVO ESTA ENCRIPTADO NO SE PUDE ACCEDER A LOS METADATOS')
        else:
            metadata_original = get_metadata(path)
            metadata_normalized = normalize_metadata(metadata_original)
            metadata_normalized = read_and_recover_information(metadata_normalized, path)

            print()
            print(metadata_normalized)

            all_metadata += str(metadata_normalized) + '\n'

            list_metadata_dates.append([metadata_normalized['creationDate'], files[x]])
        print()
        print('--------------------------------------------')
        print()

    # generate_txt(all_metadata)
    # generate_csv(list_metadata_dates)

# Metodo que elimina los caracteres especiales de la cadena
def remove_special_characters(file_name):
    new_file_name = ''.join(filter(str.isalnum, file_name)) 
    return new_file_name

# Metodo que retorna el nombre del archivo sin la extension
def remove_extension(file_name):
    new_file_name = file_name.split('.pdf')
    return new_file_name[0]

# Metodo que elimina los acentos y remplaza las letras sin acentos
def normalize_accents(file_name):
    # s = "Pingüino: Málãgà ês uñ̺ã cíudãd fantástica y èn Logroño me pica el... moñǫ̝̘̦̞̟̩̐̏̋͌́ͬ̚͡õ̪͓͍̦̓ơ̤̺̬̯͂̌͐͐͟o͎͈̳̠̼̫͂̊"
    # -> NFD y eliminar diacríticos sin la ñ
    # s = re.sub(
    #         r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
    #         normalize( "NFD", s), 0, re.I
    #     )
    # -> NFD y eliminar diacríticos
    file_name = re.sub(
            r"([^\u0300-\u036f]|(?![\u0300-\u036f]))[\u0300-\u036f]+", r"\1", 
            normalize("NFD", file_name), 0, re.I
        )
    # -> NFC
    file_name = normalize('NFC', file_name)
    return file_name

# Metodo que elimina los numeros del nombre del archivo
def remove_numbers(file_name):
    new_file_name = ''.join(i for i in file_name if not i.isdigit())
    return new_file_name

# Metodo que genera archivo txt
def generate_txt(metadata):
    file = open("metadata.txt", "w")
    file.write(str(metadata) + os.linesep)
    file.close()

# Metodo que genera archivo csv
def generate_csv(list_metadata_dates):
    NCD = pd.DataFrame(np.array(list_metadata_dates)) # Matriz de nuevo conjunto de datos con pandas
    print(NCD)
    NCD.to_csv(str('metadata') + '.csv', header=True, sep=',', index=False)

# Metodo que busca una fecha (en cualquier formato) en una cadena o texto
def find_date(text):
    matches = datefinder.find_dates(text)
    for match in matches:
        # print(match)
        return match # 2021-10-22 18:30:00

# Metodo que establece formato para una fecha en formato string
def set_format_date(text):
    match = re.search(r'\d{4}-\d{2}-\d{2}', str(text))
    # print(match.group()) # 2021-03-21
    date = datetime.strptime(match.group(), '%Y-%m-%d').strftime('%Y%m%d')
    # date = datetime.strptime('Mon Feb 15 2010', '%a %b %d %Y').strftime('%d/%m/%Y')
    # print(date)
    return date

# Metodo que recibe el nombre del archivo y determina si tiene fecha en la cadena y si la tiene la retorna con el formato correcto despues de llamar al metodo (set format date)
def get_date(file):
    date = ''
    date_formated = str(find_date(file))
    if(date_formated != 'None'):
        print('Formato: ' + date_formated)
        date = set_format_date(date_formated)
        # print(date)
    return date

# Metodo que cuenta la cantidad de caracteres del nombre del archivo y determina si es valido
def count_character(file):
    characters = len(file)
    # FIXME: Que pasa con los archivos que son superior a 40 caracteres?
    if(characters <= 40):
        return True
    else:
        return False

# Metodo que formatea la fecha de creacion de los metadatos del pdf, se apolla en el metodo de (set format date)
def get_creation_date_format(date):
    date_format = 'D:' + set_format_date(date) + '000000'
    return date_format

if __name__ == '__main__':
    # Obtener metadatos de un solo pdf
    # path = 'files/14AutoOrdenaSeguirAdelanteEjecucion-smallpdf.pdf'
    # print(get_metadata(path))
    # "D:20210219152236-05'00'"
    # 'D:2021 02 19 15 22 36'

    # show_metadata()
    # rename_file('text.pdf', 'rename_text.pdf')


    print()

    file = 'files/08. AUTO NOMBRA CURADOR.pdf'
    with pdfplumber.open(file) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    print(text)
    print()

    # matches = datefinder.find_dates(matches)
    matches = search_dates(text, languages=['es'])
    new_text = ''
    new_matches = list()
    for match in matches:
        new_text += match[0] + ', '
        new_matches.append(match)
        print(match)
    print(new_text)

    matches = datefinder.find_dates(str(new_text))
    for match in matches:
        print(match)

    # print(get_creation_date_format(new_matches[0]))
    
    # print()
    # print(pdf.metadata)

    # date = dateparser.parse('Jueves 04 de Febrero del 2021', languages=['es'])
    # print(date)
    # date_search = search_dates('The first artificial Earth satellite was launched on 4 October 1957.', add_detected_language=True)
    # print(date_search)

# TODO: Revisar archivo 06. notificación 19.04.2021 DEMANDADO.pdf que sale con contenido extranio
# TODO: Obtener metadatos X
# TODO: Cargar archivos de pdf en web
# TODO: Hacer copia de archivos para no romper los originales
# TODO: Generar .txt con las fechas