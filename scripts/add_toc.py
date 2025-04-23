import nbformat as nbf
import os

# Ruta al notebook
notebook_path = '../notebooks/clear_summary.ipynb'
output_path = '../notebooks/clear_summary_with_toc.ipynb'

# Leer el contenido de la tabla de contenidos
with open('../notebooks/toc_clear_summary.md', 'r', encoding='utf-8') as toc_file:
    toc_content = toc_file.read()

# Cargar el notebook
notebook = nbf.read(notebook_path, as_version=4)

# Crear una nueva celda de markdown con la tabla de contenidos
toc_cell = nbf.v4.new_markdown_cell(toc_content)

# Insertar la celda de tabla de contenidos al inicio
notebook.cells.insert(0, toc_cell)

# Escribir el notebook modificado
nbf.write(notebook, output_path)

print(f"Tabla de contenidos agregada. Notebook guardado como {output_path}") 