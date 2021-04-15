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
from os import remove
import pikepdf
import shutil

# Metodo que permite obtener la informacion de metadatos del archivo
def get_metadata(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
    
    if (info != None):
        author = info.author
        creator = info.creator
        producer = info.producer
        subject = info.subject
        title = info.title
    else:
        # print('Metadata: None')
        info = {}
        info.setdefault('/Author', '')
        
    # for key in info:
    #     print (key, ":", info[key])

    # print(info)
    return (info, number_of_pages)

# Metodo que normaliza los medatatos de los pdfs para que todos los archivos tengan las mismas propiedades
def normalize_metadata(metadata, number_of_pages):
    info_normalize = {
        'creator': exist_prop(metadata, '/Creator'),
        'producer': exist_prop(metadata, '/Producer'),
        'creationDate': exist_prop(metadata, '/CreationDate'),
        'modificationDate': exist_prop(metadata, '/ModDate'),
        'title': exist_prop(metadata, '/Title'),
        'author': exist_prop(metadata, '/Author'),
        'subject': exist_prop(metadata, '/Subject'),
        'keywords': exist_prop(metadata, '/Keywords'),
        'pages': number_of_pages
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

# Metodo que obtiene la informacion de la primera pagina del pdf escaneado, recibe el path
def get_content_file_scanned(path):
    # Convierte la imagen a texto con ocrmypdf
    os.system(f'ocrmypdf --pages 1-2 {path} output.pdf')

    with pdfplumber.open('output.pdf') as pdf:
        page = pdf.pages[0]
        text = page.extract_text(x_tolerance=2)
        remove('output.pdf') # Elimina el archivo que es generado porque no es necesario
        print()
    return text

# Metodo que recupera la primera fecha de un texto en espaniol y discrimina las fechas basura
def get_recover_date(text):
    # matches = datefinder.find_dates(text, source=False)
    matches = search_dates(text, languages=['es'])
    new_matches = list()
    for match in matches:
        if(len(match[0]) > 7): # Mayor que 7(25/1/19) para eliminar la fechas basura que trae en matches
            new_matches.append(match[1])
            print(match)
    # print(new_matches)
    date = get_creation_date_format(new_matches[0]) # D:20201113165700 formato de la fecha de los metadatos
    return date
        
# Metodo que lee y recupera la informacion de los metadatos con ayuda del metodo (get content file)
def read_and_recover_information(metadata_normalized, path):
    # NO TIENE FECHA DE CREACION
    if(metadata_normalized['creationDate'] == ''):
        text = get_content_file(path) # Llama al metodo para que recupere la info
        # print(text)

        # Recupera la informacion si es un pdf escrito y es diferente de None
        if(str(text) != 'None'):
            metadata_normalized['creationDate'] = get_recover_date(text)
        else:
            # TODO: Debe de cambiar el nombre y asignarselo antes de scanned el pdf para que permita su observacion porque no permite espacios en su nombre
            text = get_content_file_scanned(path) # Llama al metodo para que recupere la info pdf imagen
            print(text)
            metadata_normalized['creationDate'] = get_recover_date(text)
    return metadata_normalized

# Metodo que obtiene la metadata completa (arreglo), recibe el path, nombre de archivo, toda la metadata y lista de metadata
def get_metadata_files_list(path, list_metadata, list_metadata_dates, file):
    (metadata_original, number_of_pages) = get_metadata(path)
    metadata_normalized = normalize_metadata(metadata_original, number_of_pages)
    metadata_normalized = read_and_recover_information(metadata_normalized, path)

    print()
    print(metadata_normalized)

    list_metadata += str(metadata_normalized) + '\n'

    list_metadata_dates.append([convert_string_to_datatime(metadata_normalized['creationDate']), metadata_normalized['pages'], file])

    return (list_metadata, list_metadata_dates)

# Metodo que desencripta archivos protegidos (unlocked - protected - unsecured) y retorna la ruta del archivo desencriptado
def decrypted_file(file, path):
    path_file_decrypted = file + '_decrypted.pdf'
    with pikepdf.open(path) as pdf:
        num_pages = len(pdf.pages)
        # del pdf.pages[-1] # Elimina la ultima pagina
        pdf.save(path_file_decrypted)
    return path_file_decrypted

# Metodo que determina si el archivo esta protegido
def is_locked(file):
    with open(file, 'rb') as f:
        pdf = PdfFileReader(f)

    if(pdf.isEncrypted):
        return True
    else:
        return False

# Metodo que comprueba si el archivo basura existe, si exite lo elimina
def is_exist_file_trash():
    is_exist_file_trash = os.path.isfile(get_folder() + '.DS_Store') # Comprueba si el archivo existe
    if (is_exist_file_trash):
        remove(get_folder() + '.DS_Store') # Elimina el archivo basura

# Metodo que comprueba si la carpeta existe, si no exite la crea, si exite no la crea
def is_exist_folder(folder_of_files_renames):
    is_exist_folder = os.path.isdir(get_folder() + folder_of_files_renames) # comprueba si el folder existe
    if (not is_exist_folder):
        os.mkdir(get_folder() + folder_of_files_renames) # Genera una nueva carpeta

# Metodo que renombra los nombres de los archivos y los ubica en el nuevo folder
def temporality_rename_file_and_place_folder(path, file, folder_of_files_renames):
    file_rename = file.replace(' ', '_')
    print(file_rename)

    # TODO: Aplicar esta logica de abajo para el renombramiento final del archivo
    is_exist_file_trash()
    is_exist_folder(folder_of_files_renames)
    
    shutil.copy(path, (get_folder() + str(folder_of_files_renames) + file)) # Copia el archivo a la nueva carpeta
    os.rename((get_folder() + str(folder_of_files_renames) + file), (get_folder() + str(folder_of_files_renames) + file_rename)) # Renombrar el archivo ubicado en la nueva carpeta

# Metodo que recorre el folder actual y renombra todos los archivos en el
def temporality_rename_all_files(folder_of_files_renames):
    files = files_list(get_folder())
    count = 0

    for x in range(len(files)):
        if ((files[x] != 'numero_proceso') and (files[x] != '.DS_Store')):
            print(str(count+1) + ". " + files[x])

            path_original = get_folder() + files[x]
            temporality_rename_file_and_place_folder(path_original, files[x], folder_of_files_renames)
            print()
        count += 1

# Metodo que retorna la variable con el nombre de la carpeta
def get_folder():
	# carpeta = 'HERRAMIENTAS_EXCEL/1220190007900_Prueba_1/CUADERNO_PRINCIPAL/'
	carpeta = 'HERRAMIENTAS_EXCEL/1220190007900_Prueba_2/CUADERNO_PRINCIPAL/'
	# carpeta = 'HERRAMIENTAS_EXCEL/CUADERNO_PRINCIPAL_JUAN/'
	# carpeta = 'HERRAMIENTAS_EXCEL/CUADERNO_PRINCIPAL_SEBAS/'
	return carpeta

# Metodo que retorna una lista con los archivos del folder
def files_list(folder):
	files_list = os.listdir(folder)
	return files_list

# Metodo que lista los archivos en el folder y recorre cada archivo
def show_metadata():
    print('RENONBRAMIENTO DE ARCHIVO Y COPIA A LA NUEVA UBICACION')
    print('----------------------------------------------------------')
    folder_of_files_renames = 'numero_proceso/'
    temporality_rename_all_files(folder_of_files_renames)
    
    print()
    print('LECTURA DEL ARCHIVO PARA OBTENER METADATOS DESDE LA NUEVA UBICACION')
    print('----------------------------------------------------------')
    files_news = files_list(get_folder() + folder_of_files_renames)
    list_metadata = ''
    list_metadata_dates = list()

    for x in range(len(files_news)):
        print(str(x+1) + ". " + files_news[x])

        # ------------------------------------------------------------
        # CONTENIDO DEL ARCHIVO
        path = get_folder() + folder_of_files_renames + files_news[x]
        print('Encriptado: ' + str(is_locked(path)))

        print()

        if(is_locked(path)):
            # Archivos que son pdf y tiene proteccion con texto o con imagen
            path_file_decrypted = decrypted_file(files_news[x], path) # Desencripta y retorna la ruta del archivo desencriptado

            # TODO: Aca se debe de leer el archivo primero, para cambiar el nombre original al provisional, despues de obtener toda la metadata asignar nombre de acuerdo al orden de fechas(Mirar si se puede asignar nombre temporal de entrada)
            # TODO: Agregar el nombre correcto que debe de llevar sin el numero al principio (01, 02, ...) a la list_metadata_dates (tambien se pude recorrer el arreglo (list_metadata_dates) y extraer el nombre del archivo y que despues pase por un metodo para su transformacion y asignacion, debe ser al final del bucle for, despues llamar al metodo de renombrar)

            (list_metadata, list_metadata_dates) = get_metadata_files_list(path_file_decrypted, list_metadata, list_metadata_dates, files_news[x])
            remove(path_file_decrypted) # Elimina el archivo que es generado porque no es necesario
            # TODO: Eliminar .DS_Store dentro de la carpeta del proceso cuando es agregado algun archivo, para este caso el folder
        else:
            # Archivos que son pdf sin proteccion con texto o con imagen
            (list_metadata, list_metadata_dates) = get_metadata_files_list(path, list_metadata, list_metadata_dates, files_news[x])
        print()
        print('--------------------------------------------')
        print()

    print()
    print('ORDENAMIENTO DE LOS DATOS DE ACUERDO A LA FECHA Y ESCRITURA DE NOMBRE FINAL')
    print('----------------------------------------------------------')
    # list_metadata_dates = sort_list_metadata_dates(list_metadata_dates)
    print(list_metadata_dates)
    for x in range(len(list_metadata_dates)):
        print('NOMBRE: ' + list_metadata_dates[x][2])
        print()

    #     # NOMBRE DEL ARCHIVO
    #     # TODO: Crear metodo que haga todo el proceso de modificar el nombre con los metodos que se utilizan aca
    #     file = remove_extension(files_news[x]) # Elimina la extension
    #     file = normalize_accents(file) # Elimina acentos
    #     count_character_file = count_character(file) # Cantidad de caracteres
    #     print('Valido: ' + str(count_character_file) + ', Caracteres: ' + str(len(file)))
    #     file = str(file.title()) # Capitalizacion
    #     print('Capitalizacion: ' + file)

    #     date = get_date(file) # Retorna la fecha del archivo formateada si tiene
    #     # TODO: Regla de los numeros al principio antecedidos por cero
    #     # TODO: Regla de las preposiciones en el nombre (Diccionario)

    #     file = remove_special_characters(file.title()) # Elimina caracteres especiales
    #     file = remove_numbers(file) # Elimina numeros de la cadena
    #     file = file + date

    #     print('SALIDA: ' + file)

    # generate_txt(list_metadata)
    # generate_csv(list_metadata_dates)
    # generate_xlsx(list_metadata_dates)

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

# Metodo que ordena la lista de metadatos de fechas
def sort_list_metadata_dates(list_metadata_dates):
    data_set = pd.DataFrame(np.array(list_metadata_dates)) # Matriz de nuevo conjunto de datos con pandas
    data_set = data_set.sort_values(by=0) # Ordena la columna 0 que contiene las fechas
    return data_set

# Metodo que genera archivo txt
def generate_txt(metadata):
    # TODO: Crear metodo para la carpeta list_metadata_dates, aplicar validacion si existe o crearla
    file = open("generated_files/metadata.txt", "w")
    file.write(str(metadata) + os.linesep)
    file.close()

# Metodo que genera archivo csv
def generate_csv(list_metadata_dates):
    data_set = sort_list_metadata_dates(list_metadata_dates)
    print(data_set)
    data_set.to_csv(str('generated_files/metadata') + '.csv', header=True, sep=',', index=False)

# Metodo que genera archivo csv
def generate_xlsx(list_metadata_dates):
    data_set = sort_list_metadata_dates(list_metadata_dates)
    writer = pd.ExcelWriter(str('generated_files/0_0ReadData') + '.xlsx', engine='xlsxwriter')
    data_set.to_excel(writer, header=False, index=False)
    writer.save()

def convert_string_to_datatime(text_date):
    # D:20200821205457Z00'00' --> D:2020 08 21 20 54 57 Z00'00'
    # D:20201111143014-05'00' --> D:2020 11 11 14 30 14 -05'00'
    # D:20201216122209+00'00' --> D:2020 12 16 12 22 09 +00'00'
    # D:20201113165700 --> D:2020 11 13 16 57 00
    text_list = text_date.split(':') # 'Z', '-', '+'

    date_with_z = text_list[1].find('Z')
    date_with_underscore = text_list[1].find('-')
    date_with_plus = text_list[1].find('+')

    if(date_with_z != -1):
        text_list = text_list[1].split('Z')
        string_date = text_list[0]
    elif(date_with_underscore != -1):
        text_list = text_list[1].split('-')
        string_date = text_list[0]
    elif(date_with_plus != -1):
        text_list = text_list[1].split('+')
        string_date = text_list[0]
    else:
        string_date = text_list[1]

    date = datetime.strptime(str(string_date), '%Y%m%d%H%M%S')
    return date

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
    # path = 'files/002 ACTA DE REPARTO_prop_author.pdf'
    # (metadata, number_of_pages) = get_metadata(path)
    # print(metadata)
    # print(number_of_pages)

    show_metadata()
    
    # path = 'files/10. AcEpTa dEsIgNaCióN_name_file_with_spaces.pdf'
    # file = '10. AcEpTa dEsIgNaCióN_name_file_with_spaces.pdf'
    # folder_of_files_renames = 'numero_proceso/'

    # file_rename = file.replace(' ', '_')
    # print(file)

    # is_exit_folder = os.path.isdir(folder_of_files_renames) # comprueba si el archivo existe
    # print(is_exit_folder)
    # if (not is_exit_folder):
    #     os.mkdir(folder_of_files_renames) # Genera una nueva carpeta
    # shutil.copy(path, str(folder_of_files_renames) + file) # Copia el archivo a la nueva carpeta
    # rename_file(str(folder_of_files_renames) + file, str(folder_of_files_renames) + file_rename) # Renombrar el archivo ubicado en la nueva carpeta



    

# TODO: Revisar archivo 06. notificación 19.04.2021 DEMANDADO.pdf que sale con contenido extranio
# TODO: Revisar el archivo 003_ESCRITO_DEMANDA_FLS._1-73.pdf el cual no esta recuperando la fecha correcta (intentar aplicarle los dos metodos de busqueda de fechas, en ingles y espaniol y obtener las que son iguales)
# TODO: Cargar archivos de pdf en web (Django and Drag and Drop)
# TODO: Hacer copia de archivos para no romper los originales
# TODO: Identificar si un proceso ya esta bien renombrado y no aplicar programa a menos de que tenga un archivo nuevo