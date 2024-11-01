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

# Obtener la fecha de la última modificación
fecha_ultima_modificacion = obtener_fecha_modificacion_github(usuario, repo, archivo)

# Función para cargar datos y asegurar la validación de columnas
@st.cache_data
def load_data(file_path):
    try:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"El archivo '{file_path}' no se encuentra en el directorio.")
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Validar columnas necesarias
        columnas_requeridas = ["Codigo", "Nombre", "Precio", "Precio x Mayor", "Stock", "Descripcion", "Categorias", "imagen", "Pasillo", "Estante", "Proveedor"]
        if not all(col in df.columns for col in columnas_requeridas):
            raise ValueError("El archivo no tiene las columnas necesarias.")
        
        st.success(f"Archivo '{file_path}' cargado correctamente.")
        return df
    except FileNotFoundError as fnf_error:
        st.error(str(fnf_error))
        return None
    except Exception as e:
        st.error(f"Error al cargar el archivo '{file_path}': {e}")
        return None

# Especificar el nombre del archivo
file_path = '1804no.xlsx'

# Intentar cargar el archivo
df = load_data(file_path)

# Si el archivo no se encuentra, opción para subir un archivo
if df is None:
    st.warning("Por favor, subí el archivo Excel o CSV si no está presente en el sistema.")
    uploaded_file = st.file_uploader("Selecciona un archivo Excel o CSV", type=["xlsx", "csv"])

    if uploaded_file is not None:
        file_extension = os.path.splitext(uploaded_file.name)[1]
        
        # Convertir CSV a Excel si es necesario
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
        
        st.cache_data.clear()  # Limpiar caché para cargar nuevos datos
        df = load_data(file_path)

# Si los datos se cargan correctamente, mostrar éxito
if df is not None:
    st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")
else:
    st.stop()

# Función para cambiar el color del stock
def obtener_color_stock(stock):
    if stock > 5:
        return 'green'
    elif stock < 0:
        return 'red'
    elif stock <= 1:
        return 'orange'
    else:
        return 'black'

# Función para cargar imágenes desde URL
@st.cache_data
def cargar_imagen(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# Mostrar producto completo con precio normal o por mayor
def mostrar_producto_completo(producto, mostrar_mayorista, mostrar_descuento, descuento):
    st.markdown(f"<h3 style='font-size: 36px;'>{producto['Nombre']}</h3>", unsafe_allow_html=True)

    # Usar precio normal por defecto, precio por mayor solo si el checkbox está marcado
    precio_mostrar = producto['Precio'] if not mostrar_mayorista else producto['Precio x Mayor']
    tipo_precio = "Precio" if not mostrar_mayorista else "Precio x Mayor"

    precio_formateado = f"{precio_mostrar:,.0f}".replace(",", ".")
    stock_color = obtener_color_stock(producto['Stock'])
    st.markdown(f"<span style='font-size: 28px; font-weight: bold;'>Código: {producto['Codigo']} | {tipo_precio}: ${precio_formateado} | <span style='color: {stock_color};'>Stock: {producto['Stock']}</span></span>", unsafe_allow_html=True)

    if mostrar_descuento and descuento > 0:
        precio_descuento = precio_mostrar * (1 - descuento / 100)
        st.markdown(f"<span style='font-size: 24px; color:blue;'>Precio con {descuento}% de descuento: ${precio_descuento:,.0f}</span>", unsafe_allow_html=True)

    st.markdown(f"<p style='font-size: 26px;'>Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size: 24px;'>Categorías: {producto['Categorias']}</p>", unsafe_allow_html=True)

    col_img, col_btns = st.columns([5, 1])
    with col_img:
        imagen_url = producto.get('imagen', '')
        if imagen_url:
            imagen = cargar_imagen(imagen_url)
            if imagen:
                img_size = st.session_state.get('img_size', 300)
                st.image(imagen, width=img_size)
            else:
                st.write("Imagen no disponible.")
    with col_btns:
        st.markdown("**Vista**")
        if st.button("➕"):
            st.session_state.img_size = min(st.session_state.get('img_size', 300) + 50, 600)
        if st.button("➖"):
            st.session_state.img_size = max(st.session_state.get('img_size', 300) - 50, 100)

    if st.checkbox('Mostrar Ubicación'):
        st.write(f"Pasillo: {producto.get('Pasillo', 'Sin datos')}")
        st.write(f"Estante: {producto.get('Estante', 'Sin datos')}")
        st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")

# Título de la app
st.markdown("<h1 style='text-align: center;'>🐻Sooper 3.o🐻 beta  </h1>", unsafe_allow_html=True)

# Inicializar buscadores en session_state
if 'selected_codigo' not in st.session_state:
    st.session_state.selected_codigo = ''
if 'selected_nombre' not in st.session_state:
    st.session_state.selected_nombre = ''

# Sincronizar código y nombre
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

# Buscadores de código y nombre
col_codigo, col_nombre = st.columns([1, 2])

with col_codigo:
    codigo_lista = [""] + df['Codigo'].astype(str).unique().tolist()
    st.selectbox("Buscar por Código", codigo_lista, key='selected_codigo', on_change=on_codigo_change)

with col_nombre:
    nombre_lista = [""] + df['Nombre'].unique().tolist()
    st.selectbox("Buscar por Nombre", nombre_lista, key='selected_nombre', on_change=on_nombre_change)

# Mostrar producto seleccionado
if st.session_state.selected_codigo and st.session_state.selected_nombre:
    producto_data = df[df['Codigo'] == st.session_state.selected_codigo].iloc[0]

    # Checkbox para precio mayorista y calculador de descuento
    col1, col2 = st.columns([1, 2])
    with col1:
        mostrar_mayorista = st.checkbox("Mostrar Precio por Mayor")
    with col2:
        mostrar_descuento = st.checkbox("Mostrar calculador de descuento")
    descuento = st.number_input("Calcular descuento (%)", min_value=0, max_value=100, step=1, value=0) if mostrar_descuento else 0

    # Mostrar el producto con las opciones
    mostrar_producto_completo(producto_data, mostrar_mayorista=mostrar_mayorista, mostrar_descuento=mostrar_descuento, descuento=descuento)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
