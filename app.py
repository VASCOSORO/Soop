import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
import pytz  # Para manejar zonas horarias
import os

# ====== Version 2.0.1 ==== Funcionando 
# Definir la zona horaria de Argentina
tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')

# Función para obtener la fecha de la última modificación del archivo en GitHub
def obtener_fecha_modificacion_github(usuario, repo, archivo):
    url = f"https://api.github.com/repos/{usuario}/{repo}/commits?path={archivo}&per_page=1"
    response = requests.get(url)
    if response.status_code == 200:
        commit_data = response.json()[0]
        fecha_utc = commit_data['commit']['committer']['date']
        # Convertir la fecha a datetime y luego ajustarla a la zona horaria de Argentina
        fecha_utc = datetime.strptime(fecha_utc, "%Y-%m-%dT%H:%M:%SZ")
        fecha_argentina = fecha_utc.astimezone(tz_argentina)
        return fecha_argentina.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return "No se pudo obtener la fecha de actualización"

# Definir los detalles del repositorio
usuario = "VASCOSORO"  # Tu usuario de GitHub
repo = "Soop"  # El nombre de tu repositorio
archivo = "1804.xlsx"  # El archivo del cual querés obtener la fecha

# Obtener la fecha de la última modificación del archivo en GitHub
fecha_ultima_modificacion = obtener_fecha_modificacion_github(usuario, repo, archivo)

# Cargar el archivo Excel
@st.cache_data
def load_data():
    file_path = '1804.xlsx'  # Ruta del archivo Excel

    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        st.error(f"El archivo '{file_path}' no se encuentra. Por favor, subí el archivo usando la opción de subida.")
        return None

    # Cargar el archivo Excel
    df = pd.read_excel(file_path, engine='openpyxl')
    return df

# Función para cargar la imagen desde una URL con caché
@st.cache_data
def cargar_imagen(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# Cargar datos
df = load_data()

# Si df es None, mostrar la sección de subida de archivo
if df is None:
    st.error("No se pudo cargar el archivo Excel porque no se encuentra en el directorio.")
    st.markdown("### Subí el archivo 1804.xlsx")
    uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xlsx"], key='uploaded_file')
    if uploaded_file is not None:
        try:
            # Guardar el archivo subido como '1804.xlsx'
            with open("1804.xlsx", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("Archivo Excel subido y guardado correctamente.")
            st.cache_data.clear()  # Limpiar la caché para cargar los nuevos datos
            # Recargar los datos
            df = load_data()
        except Exception as e:
            st.error(f"Error al subir el archivo: {e}")

if df is not None:
    # Mostrar detalles si el archivo se cargó correctamente
    st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")
    # Aquí continuarías con el resto de tu código para mostrar productos, categorías, etc.
