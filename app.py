import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
import pytz
import os

# Definir la zona horaria de Argentina
tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')

# Función para obtener la fecha de la última modificación del archivo en GitHub
def obtener_fecha_modificacion_github(usuario, repo, archivo):
    url = f"https://api.github.com/repos/{usuario}/{repo}/commits?path={archivo}&per_page=1"
    response = requests.get(url)
    if response.status_code == 200:
        commit_data = response.json()[0]
        fecha_utc = commit_data['commit']['committer']['date']
        fecha_utc = datetime.strptime(fecha_utc, "%Y-%m-%dT%H:%M:%SZ")
        fecha_argentina = fecha_utc.astimezone(tz_argentina)
        return fecha_argentina.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return "No se pudo obtener la fecha de actualización"

# Detalles del repositorio
usuario = "VASCOSORO"
repo = "Soop"
archivo = '1804no.xlsx'

# Intentar obtener la fecha de modificación
fecha_ultima_modificacion = obtener_fecha_modificacion_github(usuario, repo, archivo)

# Función para cargar datos
@st.cache_data
def load_data(file_path):
    try:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"El archivo '{file_path}' no se encuentra en el directorio.")
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Renombrar la columna "Precio" a "Precio x Mayor"
        if "Precio" in df.columns:
            df = df.rename(columns={"Precio": "Precio x Mayor"})
        
        return df
    except FileNotFoundError as fnf_error:
        st.error(str(fnf_error))
        return None
    except Exception as e:
        st.error(f"Error al cargar el archivo '{file_path}': {e}")
        st.exception(e)
        return None

# Nombre del archivo
file_path = '1804no.xlsx'

# Intentar cargar el archivo
df = load_data(file_path)

# Verificación de columnas requeridas
if df is not None:
    columnas_requeridas = ["Precio Jugueterias face", "Precio x Mayor"]
    for columna in columnas_requeridas:
        if columna not in df.columns:
            st.error(f"La columna '{columna}' no se encuentra en el archivo cargado.")
            st.stop()

# Checkbox para mostrar/ocultar la sección de detalles de archivo y actualización
mostrar_seccion_superior = st.checkbox("Mostrar detalles de archivo y botón de actualización", value=False)

# Si el checkbox está activado, mostrar la sección superior
if mostrar_seccion_superior:
    st.success("Archivo '1804no.xlsx' cargado correctamente.")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <span style="font-size: 24px; margin-right: 10px;">🔒</span>
            <span style="font-size: 24px; font-weight: bold;'>Subir Nuevo Archivo Excel</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Crear una columna para alinear el campo de contraseña y el uploader
    col_pass, col_space, col_upload = st.columns([1, 0.1, 2])

    with col_pass:
        password = st.text_input("Ingrese la contraseña para subir el archivo:", type="password")

    with col_upload:
        if password == "pasteur100pre":  # Reemplaza con la contraseña correcta
            st.success("Contraseña correcta. Puedes subir el archivo.")
            uploaded_file = st.file_uploader("Selecciona un archivo Excel o CSV", type=["xlsx", "csv"])
            if uploaded_file is not None:
                try:
                    file_extension = os.path.splitext(uploaded_file.name)[1]
                    if file_extension == ".xlsx":
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    elif file_extension == ".csv":
                        try:
                            csv_data = pd.read_csv(uploaded_file, encoding="utf-8", error_bad_lines=False, sep=None, engine="python")
                        except UnicodeDecodeError:
                            csv_data = pd.read_csv(uploaded_file, encoding="ISO-8859-1", error_bad_lines=False, sep=None, engine="python")
                        csv_data.to_excel(file_path, index=False, engine='openpyxl')
                        st.success("Archivo CSV convertido a Excel y guardado correctamente.")
                    else:
                        st.error("Formato no admitido. Sube un archivo en formato .xlsx o .csv")
                    st.cache_data.clear()
                    df = load_data(file_path)
                except Exception as e:
                    st.error(f"Error al subir el archivo: {e}")
        else:
            st.error("Contraseña incorrecta.")

    # Botón para actualizar datos
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<p style='font-size: 12px;'>Última modificación del archivo {archivo}: {fecha_ultima_modificacion}</p>", unsafe_allow_html=True)
        st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")
    
    with col2:
        if st.button('Actualizar datos'):
            st.cache_data.clear()
            st.success("Datos actualizados correctamente.")

# Línea negra sobre el título y arriba de "Soop Buscador"
st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

# Título
st.markdown("<h1 style='text-align: center;'>🐻Sooper 3.o🐻 beta</h1>", unsafe_allow_html=True)

# Inicializar variables en session_state para el buscador
if 'selected_codigo' not in st.session_state:
    st.session_state.selected_codigo = ''
if 'selected_nombre' not in st.session_state:
    st.session_state.selected_nombre = ''

# Funciones de devolución de llamada para sincronizar código y nombre
def on_codigo_change():
    codigo = st.session_state.selected_codigo
    if codigo:
        producto_data = df[df['Codigo'] == codigo].iloc[0]
        st.session_state.selected_nombre = producto_data['Nombre']
    else:
        st.session_state.selected_nombre = ''

def on_nombre_change():
    nombre = st.session_state.selected_nombre
    if nombre:
        producto_data = df[df['Nombre'] == nombre].iloc[0]
        st.session_state.selected_codigo = producto_data['Codigo']
    else:
        st.session_state.selected_codigo = ''

# Crear 2 columnas para el buscador por código y el buscador por nombre
col_codigo, col_nombre = st.columns([1, 2])

with col_codigo:
    codigo_lista = [""] + df['Codigo'].astype(str).unique().tolist()
    st.selectbox("Buscar por Código", codigo_lista, key='selected_codigo', on_change=on_codigo_change)

with col_nombre:
    nombre_lista = [""] + df['Nombre'].unique().tolist()
    st.selectbox("Buscar por Nombre", nombre_lista, key='selected_nombre', on_change=on_nombre_change)

# Si se selecciona un código y un nombre, mostrar el producto
if st.session_state.selected_codigo and st.session_state.selected_nombre:
    producto_data = df[df['Codigo'] == st.session_state.selected_codigo].iloc[0]

    # Agregar el checkbox para mostrar precio por mayor y calculador de descuento
    col1, col2 = st.columns([1, 2])
    with col1:
        mostrar_mayorista = st.checkbox("Mostrar Precio por Mayor")
    with col2:
        mostrar_descuento = st.checkbox("Mostrar calculador de descuento")
    if mostrar_descuento:
        descuento = st.number_input("Calcular descuento (%)", min_value=0, max_value=100, step=1, value=0)
    else:
        descuento = 0

    # Mostrar el producto con las opciones de precio por mayor y descuento
    # función de mostrar_producto_completo para mostrar los datos del producto

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
