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
        
        # Renombrar columnas para que coincidan con lo esperado
        columnas_renombradas = {
            "Id": "id",
            "Id Externo": "id externo",
            "Codigo": "Codigo",
            "Nombre": "Nombre",
            "Precio x Mayor": "Precio x Mayor",
            "Activo": "Activo",
            "Fecha Creado": "Fecha Creado",
            "Fecha Modificado": "Fecha Modificado",
            "Descripcion": "Descripcion",
            "Orden": "Orden",
            "Codigo de Barras": "Codigo de Barras",
            "unidad por bulto": "unidad por bulto",
            "inner": "Presentacion/paquete",
            "forzar multiplos": "forzar venta x cantidad",
            "Costo usd": "Costo (USD)",
            "Costo": "Costo (Pesos)",
            "Etiquetas": "Etiquetas",
            "Stock": "Stock",
            "StockSuc2": "StockSuc2",
            "Marca": "Marca",
            "categorias": "Categorias",
            "imagen": "imagen",
            "Proveedor": "Proveedor",
            "Pasillo": "Pasillo",
            "Estante": "Estante",
            "de Vencimiento": "Fecha de Vencimiento",
            "Columna": "Columna",
            "Precio": "Precio",
            "Precio face": "Ultimo Precio (Pesos)",
            "Mayorista": "Ultimo Precio (USD)"
        }
        df = df.rename(columns=columnas_renombradas)
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

# Checkbox para mostrar/ocultar la sección de detalles de archivo y actualización
mostrar_seccion_superior = st.checkbox("Mostrar detalles de archivo y botón de actualización", value=False)

# Si el checkbox está activado, mostrar la sección superior
if mostrar_seccion_superior:
    st.success("Archivo cargado correctamente.")
    st.markdown("<hr>", unsafe_allow_html=True)

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

# Funciones adicionales
@st.cache_data
def cargar_imagen(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

def obtener_color_stock(stock):
    if stock > 5:
        return 'green'
    elif stock <= 1:
        return 'orange'
    elif stock < 0:
        return 'red'
    else:
        return 'black'

# Mostrar producto completo
def mostrar_producto_completo(producto, mostrar_mayorista, mostrar_descuento, descuento):
    col_img, col_datos = st.columns([2, 3])
    
    with col_img:
        imagen_url = producto.get('imagen', '')
        if imagen_url:
            imagen = cargar_imagen(imagen_url)
            if imagen:
                img_size = st.session_state.get('img_size', 300)
                st.image(imagen, width=img_size)
            else:
                st.write("Imagen no disponible.")
        st.write("**Ajustar Imagen:**")
        col_btn_plus, col_btn_minus = st.columns([1, 1])
        with col_btn_plus:
            if st.button("➕", key="aumentar_tamano"):
                st.session_state.img_size = min(st.session_state.get('img_size', 300) + 50, 600)
        with col_btn_minus:
            if st.button("➖", key="reducir_tamano"):
                st.session_state.img_size = max(st.session_state.get('img_size', 300) - 50, 100)

    with col_datos:
        st.markdown(f"<h2 style='font-size: 36px;'>{producto['Codigo']} | {producto['Nombre']} | ${producto['Precio']:,.2f}</h2>", unsafe_allow_html=True)
        
        precio = producto['Precio x Mayor'] if mostrar_mayorista else producto['Precio']
        if mostrar_descuento:
            precio_descuento = precio * (1 - descuento / 100)
            st.markdown(f"<span style='font-size: 24px; color:blue;'>Precio con {descuento}% de descuento: ${precio_descuento:,.2f}</span>", unsafe_allow_html=True)
        else:
            precio_descuento = precio

        stock_color = obtener_color_stock(producto['Stock'])
        st.markdown(f"<span style='font-size: 24px; color: {stock_color};'>Stock: {producto['Stock']}</span>", unsafe_allow_html=True)

        stock_suc2 = producto.get('StockSuc2', 0)
        stock_suc2_text = "NO" if stock_suc2 == 0 else int(stock_suc2)
        stock_suc2_color = "red" if stock_suc2 == 0 else "black"
        st.markdown(f"<span style='font-size: 24px; color: {stock_suc2_color};'>StockSuc2: {stock_suc2_text}</span>", unsafe_allow_html=True)

        if st.checkbox('Mostrar Ubicación', value=False):
            st.write(f"**Pasillo**: {producto.get('Pasillo', 'Sin datos')}")
            st.write(f"**Estante**: {producto.get('Estante', 'Sin datos')}")
            st.write(f"**Proveedor**: {producto.get('Proveedor', 'Sin datos')}")

# Filtros
col_cat, col_nov, col_cod = st.columns([1, 1, 1])
with col_cat:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col_nov:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
with col_cod:
    filtro_codigo = st.checkbox("Listado por Inicio de Código")

# Filtro por Inicio de Código
if filtro_codigo:
    prefijo_codigo = st.text_input("Ingresa el prefijo del código (antes del guión)")
    if prefijo_codigo:
        productos_prefijo = df[df['Codigo'].str.startswith(prefijo_codigo + "-", na=False)]
        
        if not productos_prefijo.empty:
            num_paginas = (len(productos_prefijo) - 1) // 10 + 1
            pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1, step=1)
            mostrar_lista_productos(productos_prefijo, pagina)
        else:
            st.warning("No se encontraron productos con ese prefijo.")

# Filtros adicionales
if ver_por_categorias:
    categorias = sorted(set([c.strip() for cat in df['Categorias'].dropna().unique() for c in cat.split(',')]))
    categoria_seleccionada = st.selectbox('Categorías:', categorias)
    productos_categoria = df[df['Categorias'].str.contains(categoria_seleccionada, na=False)]
    num_paginas = (len(productos_categoria) // 10) + 1
    pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
    mostrar_lista_productos(productos_categoria, pagina)

if ordenar_por_novedad:
    if 'Fecha Creado' in df.columns:
        df_ordenado = df.sort_values('Fecha Creado', ascending=False)
        num_paginas = (len(df_ordenado) // 10) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        mostrar_lista_productos(df_ordenado, pagina)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
