import os
from os import remove
import copy
import re
from datetime import datetime
import shutil
import unicodedata
from unicodedata import normalize
from time import time, ctime
import sys
import subprocess
import platform

# Dependences
from PyPDF2 import PdfFileReader
import numpy as np
import pandas as pd
import datefinder
import dateparser
from dateparser.search import search_dates
import pdfplumber
import pikepdf

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
    try:
        if (key in metadata):
            return metadata[key]
        else:
            return ''
    except:
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
    os.system(f'ocrmypdf --pages 1 {path} output.pdf') # --pages 1-2

    with pdfplumber.open('output.pdf') as pdf:
        page = pdf.pages[0]
        text = page.extract_text(x_tolerance=2)
    remove('output.pdf') # Elimina el archivo que es generado porque no es necesario
    print()
    return text

# Metodo que recupera la primera fecha de un texto en espaniol y discrimina las fechas basura
def get_recover_date(text):
    try:
        # matches = datefinder.find_dates(text, source=False)
        matches = search_dates(text, languages=['es'])
        new_matches = list()
        for match in matches:
            if((len(match[0]) > 8) and (not match[0].isdigit())): # Mayor que 8(25/01/19) para eliminar la fechas basura que trae en matches
                new_matches.append(match[1])
                print(match)
        # print(new_matches)
        date = get_creation_date_format(new_matches[0]) # D:20201113165700 formato de la fecha de los metadatos
        return date
    except:
        return 'D:00000000000000'
        
# Metodo que lee y recupera la informacion de los metadatos con ayuda del metodo (get content file)
def read_and_recover_information(metadata_normalized, path):
    # NO TIENE FECHA DE CREACION
    if(metadata_normalized['creationDate'] == ''):
        text = get_content_file(path) # Llama al metodo para que recupere la info
        text = str(text).replace('  ', ' ')
        # print(text)
        # TODO: Revisar archivo 06. notificación 19.04.2021 DEMANDADO.pdf que sale con contenido extranio

        # Recupera la informacion si es un pdf escrito y es diferente de None
        if(str(text) != 'None'):
            metadata_normalized['creationDate'] = get_recover_date(text)
        else:
            text = get_content_file_scanned(path) # Llama al metodo para que recupere la info pdf imagen
            text = str(text).replace('  ', ' ')
            print(text)
            metadata_normalized['creationDate'] = get_recover_date(text)
            # TODO: Revisar el archivo 003_ESCRITO_DEMANDA_FLS._1-73.pdf el cual no esta recuperando la fecha correcta (Los archivos que son demanda deben de llevar la fecha del acta de reparto)
    return metadata_normalized

# Metodo que obtiene la metadata completa (arreglo), recibe el path, nombre de archivo, toda la metadata y lista de metadata
def get_metadata_files_list(path, list_metadata, list_metadata_dates, file):
    (metadata_original, number_of_pages) = get_metadata(path)
    metadata_normalized = normalize_metadata(metadata_original, number_of_pages)
    metadata_normalized = read_and_recover_information(metadata_normalized, path)

    print()
    print(metadata_normalized)

    list_metadata += str(metadata_normalized) + '\n'

    creation_date_datetime = convert_string_to_datatime(metadata_normalized['creationDate'])

    # TODO: Se aplica logica provicional para archivos pdf sin fecha (no es la mejor opcion) Es posible que la fecha del sistema no sea la de creacion y el orden cronologico de los archivos del proceso se pierda
    # if (creation_date_datetime == ''):
    #     creation_date_datetime = dateparser.parse(str(format(ctime(os.path.getmtime(path)))))
    if (creation_date_datetime == ''):
        creation_date_datetime = convert_string_to_datatime(metadata_normalized['modificationDate'])

    list_metadata_dates.append([creation_date_datetime, metadata_normalized['pages'], file])

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
def is_exist_folder_created(folder_of_files_renames):
    is_exist_folder = os.path.isdir(get_folder() + folder_of_files_renames) # comprueba si el folder existe
    if (not is_exist_folder):
        os.mkdir(get_folder() + folder_of_files_renames) # Genera una nueva carpeta

# Metodo que comprueba si la carpeta existe, si no exite la elimina con su contenido
def is_exist_folder_files_renames_remove(folder_of_files_renames):
    is_exist_folder = os.path.isdir(get_folder() + folder_of_files_renames) # comprueba si el folder existe
    if (is_exist_folder):
        shutil.rmtree(get_folder() + folder_of_files_renames) # Elimina el folder con su contenido

# Metodo que renombra los nombres de los archivos y los ubica en el nuevo folder
def temporality_rename_file_and_place_folder(path, file, folder_of_files_renames):
    file_rename = file.replace(' ', '_')
    print(file_rename)

    is_exist_file_trash()
    is_exist_folder_created(folder_of_files_renames)
    
    shutil.copy2(path, (get_folder() + str(folder_of_files_renames) + file)) # Copia el archivo a la nueva carpeta
    os.rename((get_folder() + str(folder_of_files_renames) + file), (get_folder() + str(folder_of_files_renames) + file_rename)) # Renombrar el archivo ubicado en la nueva carpeta

# Metodo que recorre el folder actual y renombra todos los archivos en el
def temporality_rename_all_files(folder_of_files_renames):
    files = files_list(get_folder())
    count = 0

    folder_generate_files = get_folder_generate_files().split('/')[0]
    for x in range(len(files)):
        if (not os.path.isdir(get_folder() + files[x]) and
            (files[x] != folder_of_files_renames) and 
            (files[x] != '.DS_Store') and 
            (files[x] != folder_generate_files) and
            (files[x] != '00IndiceElectronico.xlsx')):
            print(str(count+1) + ". " + files[x])

            path_original = get_folder() + files[x]
            temporality_rename_file_and_place_folder(path_original, files[x], folder_of_files_renames)
            print()
            count += 1

# Metodo que retorna la variable con el nombre de la carpeta
def get_folder():
    carpeta = sys.argv[1]
    # carpeta = 'HERRAMIENTAS_EXCEL/1220190007900_Prueba_1_correcto/CUADERNO_PRINCIPAL/'
    # carpeta = 'HERRAMIENTAS_EXCEL/1220190007900_Prueba_2_incorrecto/CUADERNO_PRINCIPAL/'
    # carpeta = 'HERRAMIENTAS_EXCEL/CUADERNO_PRINCIPAL_JUAN/'
    # carpeta = 'HERRAMIENTAS_EXCEL/CUADERNO_PRINCIPAL_SEBAS/'
    # carpeta = 'HERRAMIENTAS_EXCEL/PROCESO_MULTIMEDIA/'
    # carpeta = 'HERRAMIENTAS_EXCEL/C01Principal/'
    # carpeta = 'HERRAMIENTAS_EXCEL/Procesos_con_Imagenes/17001400300320190031400/' # Archivo NaT
    # carpeta = 'HERRAMIENTAS_EXCEL/Procesos_con_Imagenes/17001400300920200031500/CUADERNO_PRINCIPAL/'
    # carpeta = 'HERRAMIENTAS_EXCEL/Procesos_con_Imagenes/17001400301020180075700/C01Principal/' # Archivo NaT
    # carpeta = 'HERRAMIENTAS_EXCEL/SEXTO/17001400300620190033500/C01Principal/'
    return carpeta

# Metodo que obtiene el nombre de la carpera de los nuevos archivos renombrados
def get_folder_of_files_renames():
    folders = get_folder().split('/')
    count_folders = len(folders)
    folder_of_files_renames = folders[count_folders - 2]
    return folder_of_files_renames + '/'

# Metodo que retorna la capera de los archivos que se van a generar
def get_folder_generate_files():
    folder_generate_files = 'generated_files/'
    return folder_generate_files

# Metodo que retorna una lista con los archivos del folder
def files_list(folder):
    files_list = os.listdir(folder)
    return files_list

# Metodo que obtiene la metadata de un archivo multimedia
def get_metadata_media_file(path):
    extension = get_file_extension(path)

    date = format(ctime(os.path.getmtime(path)))

    input_file = path
    if (extension == '.doc' or extension == '.docx'):
        if (platform.system() == 'Darwin'):
            exe = 'exiftool' # Mac OS
        elif (platform.system() == 'Windows'):
            exe = 'exiftool(-k).exe' # Windows
    else:
        exe = 'hachoir-metadata'
    process = subprocess.Popen([exe, input_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    metadata_dict = dict()

    for output in process.stdout:
        line = output.strip().split(':', 1)
        if (line[0] != 'Metadata' and line[0] != 'Common'):
            if (line[0] == '-- press ENTER --'):
                print(line[0])
            else:
                key = line[0].strip()

                if (extension != '.doc' and extension != '.docx'):
                    key = key.split('-')[1].strip()

                value = line[1].strip()
                if (key == 'Creation date'): # Atributo de hachoir
                    metadata_dict.setdefault('/CreationDate', value)
                elif (key == 'Create Date'): # Atributo de exiftool
                        value = str(value).replace(':', '-', 2)
                        match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', str(value))
                        date = datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')
                        metadata_dict.setdefault('/CreationDate', date)
                else:
                    metadata_dict.setdefault(key, value)

    if (not '/CreationDate' in metadata_dict):
        metadata_dict.setdefault('/CreationDate', date)
    
    if (extension == '.doc' or extension == '.docx'):
        return (metadata_dict, int(metadata_dict['Pages'])) # Se envia numero de paginas para documentos .doc y docx
    else:
        return (metadata_dict, 1) # Se envia 1 para indicar que tiene un folio para los archivos multimedia

# Metodo que obtiene la metadata completa de archivos multimedia (arreglo), recibe el path, nombre de archivo, toda la metadata y lista de metadata
def get_metadata_media_files_list(path, list_metadata, list_metadata_dates, file):
    (metadata_original, number_of_pages) = get_metadata_media_file(path)
    metadata_normalized = normalize_metadata(metadata_original, number_of_pages)

    list_metadata += str(metadata_normalized) + '\n'
    
    date_datetime = dateparser.parse(str(metadata_normalized['creationDate'])) # datetime.datetime(2020, 4, 28, 18, 22, 32)
    list_metadata_dates.append([date_datetime, metadata_normalized['pages'], file])

    return (list_metadata, list_metadata_dates)

# Metodo que obtiene los metadatos de la lista nueva de archivos
def get_metadata_files_list_news(folder_of_files_renames):
    files_news = files_list(get_folder() + folder_of_files_renames)
    list_metadata = ''
    list_metadata_dates = list()

    extension_media_list = ['.mpg', '.mp1', '.mp2', '.mp3', '.m1v', '.m1a', '.m2a', '.mpa', '.mpv', '.mp4', '.mpeg', '.m4v', '.mp3', '.wav', '.jpeg', '.jpg', '.jpe', '.jpg2', '.tiff', '.doc', '.docx']

    for x in range(len(files_news)):
        print(str(x+1) + ". " + files_news[x])

        # ------------------------------------------------------------
        # CONTENIDO DEL ARCHIVO
        path = get_folder() + folder_of_files_renames + files_news[x]
        extension = get_file_extension(path)

        if (extension == '.pdf'):
            # Es un archivo de texto
            print('Encriptado: ' + str(is_locked(path)))
            print()

            if(is_locked(path)):
                # Archivos que son pdf y tiene proteccion con texto o con imagen
                path_file_decrypted = decrypted_file(files_news[x], path) # Desencripta y retorna la ruta del archivo desencriptado
                (list_metadata, list_metadata_dates) = get_metadata_files_list(path_file_decrypted, list_metadata, list_metadata_dates, files_news[x])
                remove(path_file_decrypted) # Elimina el archivo que es generado porque no es necesario
            else:
                # Archivos que son pdf sin proteccion con texto o con imagen
                (list_metadata, list_metadata_dates) = get_metadata_files_list(path, list_metadata, list_metadata_dates, files_news[x])
            print()
        elif (extension in extension_media_list):
            # Es un archivo multimedia (video, audio, imagen)
            (list_metadata, list_metadata_dates) = get_metadata_media_files_list(path, list_metadata, list_metadata_dates, files_news[x])
            print()
        else:
            print('NO SE HA IDENTIFICADO EL ARCHIVO')
            print()
    return (list_metadata, list_metadata_dates)

# Metodo que hace el renombramiento final a la lista de datos ordenada por fecha
def final_name_renaming(list_metadata_dates, folder_of_files_renames):
    extension_media_video_list = ['.mpg', '.mp1', '.mp2', '.mp3', '.m1v', '.m1a', '.m2a', '.mpa', '.mpv', '.mp4', '.mpeg', '.m4v']

    for x in range(len(list_metadata_dates)):
        file_name = list_metadata_dates[x][2]
        print()

        # TODO: nombre de carpetas C01CuadernoPrincipal, C02CuadernoMedidas
        # TODO: nombre del indice electronico 00IndiceElectronicoC01 00IndiceElectronicoC02

        # ------------------------------------------------------------
        # NOMBRE DEL ARCHIVO
        print('Nombre real: ', file_name)
        (file, extension) = split_file_extension(file_name) # Separa el nombre y la extension

        date = get_date(file.lower()) # Retorna la fecha del archivo formateada si tiene
        file = normalize_accents(file) # Elimina acentos

        if (file.find('_') != -1):
            file = str(file.title()) # Capitalizacion
        print('Capitalizacion: ' + file)

        file = indetify_file_name(file) # Identificador de capital case para los archivos que viene bien
        if (identify_date_file_name(file) != ''): # Identificador de fecha para los archivos que viene bien
            date = identify_date_file_name(file)
        
        count_character_file = count_character(file) # Cantidad de caracteres
        print('Valido: ' + str(count_character_file) + ', Caracteres: ' + str(len(file)))

        # TODO: Regla de las preposiciones en el nombre (Diccionario)

        file = remove_special_characters(file.title()) # Elimina caracteres especiales
        file = remove_numbers(file) # Elimina numeros de la cadena
        if ((file == '') and (extension == '.pdf')):
            file = 'REVISAR_NOMBRE'
        if (list_metadata_dates[x][0] is pd.NaT):
            file = file + '_REVISAR_FECHA'
        if ((file == '') and (extension in extension_media_video_list)):
            file = 'Audiencia'
        file = file + date

        file_out = assign_index(x, file, extension)
        print('SALIDA: ' + file_out)

        list_metadata_dates[x][2] = file_out
        os.rename((get_folder() + str(folder_of_files_renames) + file_name), (get_folder() + str(folder_of_files_renames) + file_out)) # Renombrar el archivo ubicado en la nueva carpeta

# Metodo que retorna el index inicial de cada archivo
def assign_index(x, file, extension):
    index = x + 1
    if (index < 10):
        file_out = '0' + str(index) + file + extension
    else:
        file_out = str(index) + file + extension
    return file_out

# Metodo que elimina los caracteres especiales de la cadena
def remove_special_characters(file_name):
    new_file_name = ''.join(filter(str.isalnum, file_name)) 
    return new_file_name

# Metodo que retorna el nombre del archivo y la extension por separado
def split_file_extension(file_name):
    new_file_name = os.path.splitext(file_name)
    name = new_file_name[0]
    extension = new_file_name[1].lower()
    return (name, extension)

# Metodo que retorna la extension del archivo
def get_file_extension(file_name):
    new_file_name = os.path.splitext(file_name)
    extension = new_file_name[1].lower()
    return extension

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

# Metodo que retorna la lista en formato DataFrame de pandas
def get_dataframe_of_list_metadata_dates(list_metadata_dates):
    data_set = pd.DataFrame(np.array(list_metadata_dates)) # Matriz de nuevo conjunto de datos con pandas
    data_set = data_set.sort_values(by=0) # Ordena la columna 0 que contiene las fechas
    return data_set

# Metodo que ordena la lista de metadatos de fechas
def sort_list_metadata_dates(list_metadata_dates):
    data_set = get_dataframe_of_list_metadata_dates(list_metadata_dates)
    return data_set.values.tolist() # Devuelve la lista ordenada en formato list() de python

# Metodo que comprueba si la carpeta existe, si no exite la crea, si exite no la crea
def is_exist_folder_generate_files(folder_of_generate_files):
    is_exist_folder = os.path.isdir(get_folder() + folder_of_generate_files) # comprueba si el folder existe
    if (not is_exist_folder):
        os.mkdir(get_folder() + folder_of_generate_files) # Genera una nueva carpeta

# Metodo que se encarga de llamar a los metodo de generacion de archivos
def generate_files(list_metadata, list_metadata_dates):
    generate_txt(list_metadata)
    generate_csv(list_metadata_dates)
    generate_xlsx(list_metadata_dates)

# Metodo que genera archivo txt
def generate_txt(list_metadata):
    folder_generate_files = get_folder_generate_files()
    is_exist_folder_generate_files(folder_generate_files)
    file = open(get_folder() + folder_generate_files + 'metadata.txt', 'w', encoding='utf-8')
    file.write(str(list_metadata) + os.linesep)
    file.close()

# Metodo que genera archivo csv
def generate_csv(list_metadata_dates):
    folder_generate_files = get_folder_generate_files()
    is_exist_folder_generate_files(folder_generate_files)
    data_set = get_dataframe_of_list_metadata_dates(list_metadata_dates)
    print(data_set)
    data_set.to_csv(str(get_folder() + folder_generate_files + 'metadata') + '.csv', header=True, sep=',', index=False)

# Metodo que genera archivo csv
def generate_xlsx(list_metadata_dates):
    folder_generate_files = get_folder_generate_files()
    is_exist_folder_generate_files(folder_generate_files)
    data_set = get_dataframe_of_list_metadata_dates(list_metadata_dates)
    writer = pd.ExcelWriter(str(get_folder() + folder_generate_files + '0_0ReadData') + '.xlsx', engine='xlsxwriter')
    data_set.to_excel(writer, header=False, index=False)
    writer.save()

def convert_string_to_datatime(text_date):
    try:
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
    except:
        return ''

# Metodo que busca una fecha (en cualquier formato) en una cadena o texto
def find_date(text):
    matches = datefinder.find_dates(text, strict=False, source=True)
    try:
        for match in matches:
            if((len(match[1]) > 8) and (not match[1].isdigit())): # Mayor que 8(25/01/19) para eliminar la fechas basura que trae en matches
                # print(match)
                return match[0] # 2021-10-22 18:30:00
    except:
        return 'None'

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
    # FIXME: Que pasa con los archivos que son superior a 40 caracteres?, entrar a revisar manual
    if(characters <= 40):
        return True
    else:
        return False

# Metodo que formatea la fecha de creacion de los metadatos del pdf, se apolla en el metodo de (set format date)
def get_creation_date_format(date):
    date_format = 'D:' + set_format_date(date) + '000000'
    return date_format

# Metodo que se encarga de hacer todo el prosamiento de archivos llamando a otros metodos para tareas especificas
def process_files_all():
    # Elimina de entrada los archivos renombrados si existen
    folder_of_files_renames = get_folder_of_files_renames()
    is_exist_folder_files_renames_remove(folder_of_files_renames)
    
    print('RENONBRAMIENTO TEMPORAL DEL ARCHIVO Y COPIA A LA NUEVA UBICACION')
    print('---------------------------------------------------------------------------')
    temporality_rename_all_files(folder_of_files_renames)
    
    print()
    print('LECTURA DEL ARCHIVO PARA OBTENER METADATOS DESDE LA NUEVA UBICACION')
    print('---------------------------------------------------------------------------')
    (list_metadata, list_metadata_dates) = get_metadata_files_list_news(folder_of_files_renames)

    print()
    print('ORDENAMIENTO DE LOS DATOS DE ACUERDO A LA FECHA Y ESCRITURA DE NOMBRE FINAL')
    print('---------------------------------------------------------------------------')
    list_metadata_dates = sort_list_metadata_dates(list_metadata_dates)
    final_name_renaming(list_metadata_dates, folder_of_files_renames)
    
    print()
    print('GENERADOR DE ARCHIVOS TXT, CSV Y XLSX')
    print('---------------------------------------------------------------------------')
    generate_files(list_metadata, list_metadata_dates)

# Metodo que calcula el tiempo de ejecucion
def calculate_time(start_time):
    elapsed_time = time() - start_time # Calculo de tiempo final
    if (elapsed_time < 60):
        print("Tiempo transcurrido: %0.10f segundos." % elapsed_time)
    else:
        elapsed_time /= 60
        print("Tiempo transcurrido: %0.10f minutos." % elapsed_time)

def camel_case_split(file_name):
    words = [[file_name[0]]]

    for x in file_name[1:]:
        if (words[-1][-1].islower() and x.isupper()):
            words.append(list(x))
        else:
            words[-1].append(x)
  
    return [''.join(word) for word in words]

# Metodo que divide la cadena entre letras y numeros
def split_between_words_numbers(file_name):
    file_name_list = re.findall('(\d+|[A-Za-z]+)', file_name) # Divide la cadena entre letras y numeros
    return file_name_list

# Recorre la lista que se genero e identifica camel case title
def identify_camel_case_title_in_list(file_name_list):
    for x in range(len(file_name_list)):
        list_temporality = camel_case_split(str(file_name_list[x]))
        if (len(list_temporality) > 1):
            file_name_list[x] = list_temporality
    return file_name_list

# Unifica la lista con sus sublista en una sola lista
def unify_list_with_sublist(file_name_list):
    file_name_list_final = list()
    for x in range(len(file_name_list)):
        # print(file_name_list[x])
        if (isinstance(file_name_list[x], list)):
            for text in (file_name_list[x]):
                file_name_list_final.append(text)
        else:
            file_name_list_final.append(file_name_list[x])
    return file_name_list_final

# Metodo que se encarga de unir las palabras de la lista con guion bajo (_)
def camel_case_join(file_name_list_final):
    # text = ''.join(x for x in text_list)
    # return text

    file_name = ''
    count = 0
    for word in file_name_list_final:
        if (count < (len(file_name_list_final) - 1)):
            file_name += word + '_'
        else:
            file_name += word
        count += 1
    return file_name

# Metodo que identifica si la cadena vine de forma correcta y devuelve el nombre separado por guin bajo (_)
def indetify_file_name(file_name):
    file_name_list = split_between_words_numbers(file_name)
    file_name_list = identify_camel_case_title_in_list(file_name_list)
    file_name_list_final = unify_list_with_sublist(file_name_list)
    file_name = camel_case_join(file_name_list_final)
    return file_name

# Metodo que identifica la fecha y la guarda
def identify_date_file_name(file_name):
    file_list = split_between_words_numbers(file_name)

    date = ''
    for word in file_list:
        if (len(word) == 8 and word.isdigit()):
            date = word

    if (date in file_list):
        file_list.remove(date)
        file_list.append(date)
    # print(file_list)
    return date

# Metodo principal
if __name__ == '__main__':
    start_time = time() # Timpo inicial

    process_files_all()

    calculate_time(start_time)
    

# TODO: Cargar archivos de pdf en web (Django and Drag and Drop)
# TODO: Capturar la fecha de modificacion del folder del proceso para ser procesada (Si la fecha de modificacion coincide con la fecha actual debe ser procesada)