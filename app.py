import streamlit as st
import pandas as pd
from datetime import datetime
import requests

# Función para obtener la fecha de la última modificación del archivo en GitHub
def obtener_fecha_modificacion_github(usuario, repo, archivo):
    url = f"https://api.github.com/repos/{usuario}/{repo}/commits?path={archivo}&per_page=1"
    response = requests.get(url)
    if response.status_code == 200:
        commit_data = response.json()[0]
        fecha_utc = commit_data['commit']['committer']['date']
        # Convertir la fecha a un formato legible y ajustado a la zona horaria de Argentina
        fecha_utc = datetime.strptime(fecha_utc, "%Y-%m-%dT%H:%M:%SZ")
        return fecha_utc.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return "No se pudo obtener la fecha de actualización"

# Definir los detalles del repositorio
usuario = "VASCOSORO"  # Tu usuario de GitHub
repo = "Soop"  # El nombre de tu repositorio
archivo = "1083.xlsx"  # El archivo del cual querés obtener la fecha

# Llamar a la función para obtener la fecha de modificación del archivo
fecha_ultima_modificacion = obtener_fecha_modificacion_github(usuario, repo, archivo)

# Mostrar la fecha de la última modificación en la interfaz
st.write(f"Última actualización en GitHub del archivo {archivo}: {fecha_ultima_modificacion}")

# Cargar el archivo Excel (desde GitHub o local)
@st.cache_data
def load_data():
    df = pd.read_excel('1083.xlsx', engine='openpyxl')  # Cargar el archivo Excel
    return df

# Cargar los datos
df = load_data()

# Mostrar el contenido cargado y la fecha de última modificación
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo Excel.")
