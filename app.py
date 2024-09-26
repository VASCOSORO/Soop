import streamlit as st
import pandas as pd
import os

excel_file_url = 'https://raw.githubusercontent.com/VASCOSORO/Soop/main/1083%20productos%20al%2024%20de%20sep.xlsx'

df = pd.read_excel(excel_file_url)

st.title('Super Buscador de Productos')

st.write("Contenido del archivo Excel:")
st.dataframe(df)

producto_buscado = st.text_input("Buscar producto por nombre:")

if producto_buscado:
    resultados = df[df['Nombre'].str.contains(producto_buscado, case=False, na=False)]
    st.write(f"Resultados para '{producto_buscado}':")
    st.dataframe(resultados)

# Luego lo subimos a GitHub:
!git add app.py
!git commit -m "Subir el archivo app.py"
