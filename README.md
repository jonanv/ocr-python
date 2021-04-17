<p align="center">
    <img src="https://i.imgur.com/Co75En9.png" width="300">
</p>

[![Python][python-badge]][python-url]
[![Pip][pip-badge]][pip-url]
[![Ocrmypdf][ocrmypdf-badge]][ocrmypdf-url]
[![License][license-badge]][license-url]

# ocr-python

## Note:
- For Mac OS use: ```pip3```
- For Windows use ```pip```

# Create virtual environment (Mac OS)
## 1. Install virtualenv
```python
pip3 install virtualenv
```

## 2. Create virtual environment (Example: env, .env, environment)
```python
virtualenv name_project
```

## 3. Activate virtual environment
```python
source name_project/bin/activate
```

## 4. Desactivate virtual environment
```python
deactivate
```

---

# Create virtual environment (Windows)
## 1. Install virtualenv
```python
pip install virtualenv
```

## 2. Create virtual environment (Example: env, .env, environment)
```python
virtualenv name_project
```

## 3. Activate virtual environment
```python
source name_project/Scripts/activate
```

## 4. Desactivate virtual environment
```python
deactivate
```

## Install dependences
```python
pip3 install -r requirements.txt
```

# Dependences:

- PyPDF2==1.26.0
- numpy==1.14.4
- pandas==0.23.0
- datefinder==0.7.1
- dateparser==1.0.0
- pdfplumber==0.5.27
- pikepdf==2.11.0
- ocrmypdf==11.7.3 (Optional for Mac OS)
<!-- TODO: Comprobar el versionamiento de las dependencias aca y en requeriments.txt -->

# Optical Character Recognition: [ocrmypdf][ocrmypdf-url]

### Mac OS
```
brew install ocrmypdf
```

### Windows
Using the [Chocolatey][chocolatey-url] package manager, install the following when running in an Administrator command prompt:
```
1. choco install --pre tesseract
```

```
2. choco install ghostscript
```

```
3. choco install pngquant (Opcional)
```

```
4. pip install ocrmypdf
```

# Run
```python
python3 get_info.py
```

## Generete requirements.txt
```python
pip3 freeze > requeriments.txt
```

[python-badge]: https://img.shields.io/badge/python-v3.6.5-brightgreen
[python-url]: https://www.python.org/downloads/release/python-365/
[pip-badge]: https://img.shields.io/badge/pip-v21.0.1-brightgreen
[pip-url]: https://pip.pypa.io/en/stable/installing/
[ocrmypdf-badge]: https://img.shields.io/badge/ocrmypdf-v11.7.3-brightgreen
[ocrmypdf-url]: https://ocrmypdf.readthedocs.io/en/v11.7.3/
[license-badge]: https://img.shields.io/badge/license-MIT-green.svg
[license-url]: https://opensource.org/licenses/MIT
[ocrmypdf-url]: https://ocrmypdf.readthedocs.io/en/latest/installation.html
[chocolatey-url]: https://chocolatey.org/install