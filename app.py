import streamlit as st
import pandas as pd

st.title('Super Buscador de Productos')

# Ruta del archivo Excel en tu Google Drive o entorno local
excel_file_path = '/content/drive/MyDrive/Colab Notebooks/1083 productos al 24 de sep.xlsx'

# Cargar el archivo Excel
df = pd.read_excel(excel_file_path)

# Mostrar el contenido del Excel
st.write("Contenido del archivo Excel:")
st.dataframe(df)

# Agregar funcionalidad de búsqueda si es necesario
producto_buscado = st.text_input("Buscar producto por nombre:")

if producto_buscado:
    resultados = df[df['Nombre'].str.contains(producto_buscado, case=False, na=False)]
    st.write(f"Resultados para '{producto_buscado}':")
    st.dataframe(resultados)
