# get_doc_info.py

from PyPDF2 import PdfFileReader
from unicodedata import normalize
import os
import copy
import re
import unicodedata

# Función que permite obtener la informacion de metadatos del archivo
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

    # diccionario = {'/nombre' : 'Carlos', 'edad' : 22, 'cursos': ['Python','Django','JavaScript'] }
    # print(diccionario['/nombre'])
    
    # for key in diccionario:
    #     print (key, ":", diccionario[key])
        
    for key in info:
        print (key, ":", info[key])

    # info_normalize = {
    #     '/Creator': '',
    #     '/Producer': '',
    #     '/CreationDate': '',
    #     '/ModDate': '',
    #     '/Title': '',
    #     '/Author': '',
    #     '/Subject': '',
    #     '/Keywords': ''
    # }
    
    # print(info)
    normalize_metadata(info)
    return info


def normalize_metadata(metadata):

    info_normalize = {
        'creator': '',
        '/Producer': '',
        '/CreationDate': '',
        '/ModDate': '',
        '/Title': '',
        '/Author': '',
        '/Subject': '',
        '/Keywords': ''
    }

    print(info_normalize)

def exist_prop():
    return

# Metodo que determina si el archivo esta protegido
def is_locked(file):
    with open(file, 'rb') as f:
        pdf = PdfFileReader(f)

    if(pdf.isEncrypted):
        return True
    else:
        return False

def rename_file(file, file_rename):
    os.rename(file, file_rename)

# Función que retorna la variable con el nombre de la carpeta
def folder():
	carpeta = 'HERRAMIENTAS EXCEL/1220190007900 Prueba 1/CUADERNO PRINCIPAL/'
	# carpeta = 'HERRAMIENTAS EXCEL/1220190007900 Prueba 2/CUADERNO PRINCIPAL/'
	return carpeta

# Función que retorna una lista con los archivos del folder
def list_files(folder):
	list_files = os.listdir(folder)
	return list_files

# 
def show_metadata():
    print()
    files = list_files(folder())
    copyFiles = copy.deepcopy(files) # Copia del arreglo original
    all_metadata = ''
    list_metadata_dates = list()

    for x in range(len(files)):
        print(str(x+1) + ". " + files[x])

        file = remove_extension(files[x]) # Elimina la extension
        file = normalize_accents(file) # Elimina acentos
        print('Caracteres: ' + str(len(file))) # Cantidad de caracteres
        print('Capitalizacion: ' + str(file.title())) # Capitalizacion
        file = remove_special_characters(file.title()) # Elimina caracteres especiales
        print('Salida: ' + file)

        path = folder() + files[x]
        print('Encriptado: ' + str(is_locked(path)))

        metadata = get_metadata(path)
        all_metadata += str(metadata) + '\n'
        print(metadata)

        list_metadata_dates.append(metadata)
        print()
        print()

    generate_txt(all_metadata)
    print(list_metadata_dates)
 
    
def remove_special_characters(file_name):
    new_file_name = ''.join(filter(str.isalnum, file_name)) 
    return new_file_name

def remove_extension(file_name):
    new_file_name = file_name.split('.pdf')
    return new_file_name[0]

def normalize_accents(file_name):
    # s = "Pingüino: Málãgà ês uñ̺ã cíudãd fantástica y èn Logroño me pica el... moñǫ̝̘̦̞̟̩̐̏̋͌́ͬ̚͡õ̪͓͍̦̓ơ̤̺̬̯͂̌͐͐͟o͎͈̳̠̼̫͂̊"
    # -> NFD y eliminar diacríticos
    file_name = re.sub(
            r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", 
            normalize("NFD", file_name), 0, re.I
        )
    # -> NFC
    file_name = normalize('NFC', file_name)
    return file_name

def remove_numbers():
    return

def change_date():
    return

def generate_txt(metadata):
    file = open("metadata.txt", "w")
    file.write(str(metadata) + os.linesep)
    file.close()

if __name__ == '__main__':
    # Obtener metadatos de un solo pdf
    # path = 'files/14AutoOrdenaSeguirAdelanteEjecucion-smallpdf.pdf'
    # get_metadata(path)

    show_metadata()
    # rename_file('text.pdf', 'rename_text.pdf')
    
    



# TODO: Cargar archivos de pdf
# TODO: remplazar la ñ por n
# TODO: Obtener metadatos X
# TODO: Hacer copia de archivos para no romper los originales
# TODO: Archivos protegidos (unlocked - protected - unsecured)
# TODO: Archivos sin fecha de cracion y modifiacion en metadatos
# TODO: Generar .txt con las fechas