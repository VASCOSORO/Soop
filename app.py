import streamlit as st
import pandas as pd

st.title('Super Buscador de Productos')

# Cargar el archivo Excel desde GitHub
excel_file_url = 'https://raw.githubusercontent.com/VASCOSORO/Soop/main/1083%20productos%20al%2024%20de%20sep.xlsx'
df = pd.read_excel(excel_file_url)

# Mostrar el contenido del archivo Excel
st.write("Contenido del archivo Excel:")
st.dataframe(df)

# Agregar funcionalidad de búsqueda
producto_buscado = st.text_input("Buscar producto por nombre:")

if producto_buscado:
    resultados = df[df['Nombre'].str.contains(producto_buscado, case=False, na=False)]
    st.write(f"Resultados para '{producto_buscado}':")
    st.dataframe(resultados)
