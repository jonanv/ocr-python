import pikepdf

with pikepdf.open('files/14AutoOrdenaSeguirAdelanteEjecucion.pdf') as pdf:
  num_pages = len(pdf.pages)
  del pdf.pages[-1]
  pdf.save('decrypted.pdf')