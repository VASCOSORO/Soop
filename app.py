import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
import pytz  # Para manejar zonas horarias

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

# Mostrar la fecha de la última modificación en la interfaz con letra más chica
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown(f"<p style='font-size: 12px;'>Última modificación del archivo {archivo}: {fecha_ultima_modificacion}</p>", unsafe_allow_html=True)

with col3:
    if st.button('Actualizar datos'):
        st.cache_data.clear()  # Limpiar la caché para asegurarse de cargar los datos actualizados

# Cargar el archivo Excel
@st.cache_data
def load_data():
    df = pd.read_excel('1804.xlsx', engine='openpyxl')  # Cargar el archivo Excel 1804.xlsx
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

# Función para cambiar el color del stock
def obtener_color_stock(stock):
    if stock > 5:
        return 'green'
    elif stock < 0:
        return 'red'
    elif stock < 3:
        return 'orange'
    else:
        return 'black'

# Mostrar producto en formato completo (con imagen)
def mostrar_producto_completo(producto, mostrar_mayorista, descuento, ocultar_descripcion):
    st.markdown(f"<h3 style='font-size: 36px;'>{producto['Nombre']}</h3>", unsafe_allow_html=True)

    # Mostrar precio según el checkbox de precio por mayor
    if mostrar_mayorista:
        precio_mostrar = producto['Precio']
        tipo_precio = "Precio x Mayor"
    else:
        precio_mostrar = producto['Precio Jugueterias face']
        tipo_precio = "Precio Jugueterías Face"

    precio_formateado = f"{precio_mostrar:,.0f}".replace(",", ".")  # Formatear el precio sin decimales
    st.markdown(f"<span style='font-size: 28px; font-weight: bold;'>Código: {producto['Codigo']} | {tipo_precio}: ${precio_formateado} | Stock: {producto['Stock']}</span>", unsafe_allow_html=True)

    # Mostrar u ocultar descripción y categorías
    if not ocultar_descripcion:
        st.markdown(f"<p style='font-size: 26px;'>Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}</p>", unsafe_allow_html=True)
    
    imagen_url = producto.get('imagen', '')
    if imagen_url:
        imagen = cargar_imagen(imagen_url)
        if imagen:
            st.image(imagen, use_column_width=True)
        else:
            st.write("Imagen no disponible.")
    
    if not ocultar_descripcion:
        st.write(f"<p style='font-size: 24px;'>Categorías: {producto['Categorias']}</p>", unsafe_allow_html=True)

    # Checkbox para mostrar ubicación
    if st.checkbox('Mostrar Ubicación'):
        st.write(f"Pasillo: {producto.get('Pasillo', 'Sin datos')}")
        st.write(f"Estante: {producto.get('Estante', 'Sin datos')}")
        st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")

# Cargar datos
df = load_data()

# Título
st.markdown("<h1 style='text-align: center;'>🐻 Soop Buscador 2.0</h1>", unsafe_allow_html=True)

# Mostrar número de filas y columnas cargadas
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Campo de búsqueda
busqueda = st.selectbox("Escribí acá para buscar", [''] + list(df['Nombre'].dropna()), index=0)

# Crear 3 columnas para el checkbox de mostrar precio x mayor, el checkbox de mostrar calculador y el input numérico del descuento
col1, col2, col3 = st.columns(3)

# Checkbox para mostrar precio por mayor
with col1:
    mostrar_mayorista = st.checkbox("Mostrar Precio por Mayor")

# Checkbox para mostrar el calculador de descuento
with col2:
    mostrar_descuento = st.checkbox("Mostrar calculador de descuento")

# Input numérico para el descuento, solo si se activa el checkbox
if mostrar_descuento:
    with col3:
        descuento = st.number_input("Calcular descuento (%)", min_value=0, max_value=100, step=1, value=0)
else:
    descuento = 0

# Checkbox para ocultar descripción y categorías
ocultar_descripcion = st.checkbox("Ocultar descripción y categorías")

# Verificar si se selecciona algo en el selectbox y que no sea vacío
if busqueda.strip() != "":
    productos_filtrados = df[df['Nombre'].str.contains(busqueda.strip(), case=False)]
    if not productos_filtrados.empty:
        producto_seleccionado = productos_filtrados.iloc[0]
        mostrar_producto_completo(producto_seleccionado, mostrar_mayorista, descuento, ocultar_descripcion)
    else:
        st.write(f"No se encontró el producto '{busqueda}'.")

# Variables para verificar si se tildaron las casillas de opciones adicionales
col_opciones = st.columns(3)
with col_opciones[0]:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col_opciones[1]:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")

# Ver lista por categorías
if ver_por_categorias:
    todas_las_categorias = df['Categorias'].dropna().unique()
    categorias_individuales = set()
    for categorias in todas_las_categorias:
        for categoria in categorias.split(','):
            categorias_individuales.add(categoria.strip())
    categoria_seleccionada = st.selectbox('Categorías:', sorted(categorias_individuales))
    if categoria_seleccionada:
        productos_categoria = df[df['Categorias'].str.contains(categoria_seleccionada)]
        num_paginas = (len(productos_categoria) // 10) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        mostrar_lista_productos(productos_categoria, pagina)

# Ordenar por novedad
if ordenar_por_novedad:
    if 'Fecha Creado' in df.columns:
        df_ordenado = df.sort_values('Fecha Creado', ascending=False)
        num_paginas = (len(df_ordenado) // 10) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        mostrar_lista_productos(df_ordenado, pagina)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
