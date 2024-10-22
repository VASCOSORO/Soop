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

# Definir los detalles del repositorio
usuario = "VASCOSORO"  # Tu usuario de GitHub
repo = "Soop"  # El nombre de tu repositorio
archivo = '1804no.xlsx'

# Función para cargar datos con opción de subida de archivo si no se encuentra
@st.cache_data
def load_data(file_path):
    try:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"El archivo '{file_path}' no se encuentra en el directorio.")
        df = pd.read_excel(file_path, engine='openpyxl')
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

# Si el archivo no se encuentra, mostrar la opción para subir el archivo
if df is None:
    st.warning("Por favor, subí el archivo Excel si no está presente en el sistema.")
    uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xlsx"])

    if uploaded_file is not None:
        # Guardar el archivo subido como '1804no.xlsx' en el directorio actual
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Archivo subido y guardado correctamente. Recargando datos...")
        # Intentar cargar el archivo nuevamente
        df = load_data(file_path)

# Si los datos se cargan correctamente, continuar con el procesamiento
if df is not None:
    st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")
    # Aquí continuas con el resto de tu código para mostrar productos, categorías, etc.
else:
    st.stop()  # Detener la ejecución si no se pueden cargar los datos

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

# Mostrar producto en formato completo (con imagen y control para cambiar tamaño)
def mostrar_producto_completo(producto, mostrar_mayorista, mostrar_descuento, descuento):
    st.markdown(f"<h3 style='font-size: 36px;'>{producto['Nombre']}</h3>", unsafe_allow_html=True)

    if mostrar_mayorista:
        precio_mostrar = producto['Precio x Mayor']
        tipo_precio = "Precio x Mayor"
    else:
        precio_mostrar = producto['Precio']
        tipo_precio = "Precio"

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

# Mostrar productos en formato de lista con imágenes (paginar resultados, sin control de tamaño)
def mostrar_lista_productos(df, pagina, productos_por_pagina=10):
    inicio = (pagina - 1) * productos_por_pagina
    fin = inicio + productos_por_pagina
    productos_pagina = df.iloc[inicio:fin]

    for i, producto in productos_pagina.iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            imagen_url = producto.get('imagen', '')
            if imagen_url:
                imagen = cargar_imagen(imagen_url)
                if imagen:
                    st.image(imagen, width=150)  # Tamaño fijo para las imágenes en lista
                else:
                    st.write("Imagen no disponible.")

        with col2:
            st.write(f"### {producto['Nombre']}")
            stock_color = obtener_color_stock(producto['Stock'])
            precio_formateado = f"{producto['Precio']:,.0f}".replace(",", ".")  # Formatear el precio sin decimales
            st.markdown(f"Código: {producto['Codigo']} | Precio: ${precio_formateado} | <span style='color: {stock_color};'>STOCK: {producto['Stock']}</span>", unsafe_allow_html=True)
            st.write(f"Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}")
            st.write(f"Categorías: {producto['Categorias']}")
        st.write("---")

# Cargar datos
df = load_data()

# Mostrar los datos
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")
