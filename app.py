import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
import pytz  # Para manejar zonas horarias

# Definir la zona horaria de Argentina
tz_argentina = pytz.timezone('America/Argentina/Buenos_Aires')

# Función alternativa para obtener la fecha de la última modificación del archivo en GitHub
def obtener_fecha_modificacion_github(usuario, repo, archivo):
    try:
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
            return "Sin información disponible"
    except:
        return "Sin información disponible"

# Definir los detalles del repositorio
usuario = "VASCOSORO"  # Tu usuario de GitHub
repo = "Soop"  # El nombre de tu repositorio
archivo = "1804.xlsx"  # El archivo del cual querés obtener la fecha

# Obtener la fecha de la última modificación del archivo en GitHub
fecha_ultima_modificacion = obtener_fecha_modificacion_github(usuario, repo, archivo)

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

    # Mostrar el precio con descuento si se aplica
    if descuento > 0:
        precio_descuento = precio_mostrar * (1 - descuento / 100)
        st.markdown(f"<span style='font-size: 24px; color:blue;'>Precio con {descuento}% de descuento: ${precio_descuento:,.0f}</span>", unsafe_allow_html=True)

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

# Cargar datos
df = load_data()

# Mostrar el botón de actualizar arriba y el mensaje de carga de datos justo debajo de la fecha de modificación
col_modif, col_btn = st.columns([3, 1])
with col_modif:
    st.markdown(f"<p style='font-size: 12px;'>Última modificación del archivo 1804.xlsx: {fecha_ultima_modificacion}</p>", unsafe_allow_html=True)
with col_btn:
    if st.button('Actualizar datos'):
        st.cache_data.clear()  # Limpiar la caché para asegurarse de cargar los datos actualizados

st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

        # Insertar una línea horizontal negra para separar las secciones
        st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)


# Título del buscador
st.markdown("<h1 style='text-align: center;'>🐻 Soop Buscador 2.0</h1>", unsafe_allow_html=True)

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

    # Agregar el checkbox para mostrar precio por mayor y calcular descuento
    col1, col2, col3 = st.columns(3)
    with col1:
        mostrar_mayorista = st.checkbox("Mostrar Precio por Mayor")
    with col2:
        mostrar_descuento = st.checkbox("Mostrar calculador de descuento")
    with col3:
        if mostrar_descuento:
            descuento = st.number_input("Calcular descuento (%)", min_value=0, max_value=100, step=1, value=0)
        else:
            descuento = 0
    
    # Mostrar el producto con las opciones de precio por mayor y descuento
    mostrar_producto_completo(producto_data, mostrar_mayorista=mostrar_mayorista, descuento=descuento, ocultar_descripcion=False)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
