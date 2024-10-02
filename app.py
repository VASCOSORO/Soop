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
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<p style='font-size: 12px;'>Última modificación del archivo {archivo}: {fecha_ultima_modificacion}</p>", unsafe_allow_html=True)

with col2:
    if st.button('Actualizar datos'):
        st.cache_data.clear()  # Limpiar la caché para asegurarse de cargar los datos actualizados

# Cargar el archivo Excel
@st.cache_data
def load_data():
    df = pd.read_excel('1804.xlsx', engine='openpyxl')  # Cargar el archivo Excel 1804.xlsx
    return df

# Cargar datos
df = load_data()

# Línea negra sobre el título
st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

# Mostrar el mensaje de éxito de carga de filas y columnas encima del título
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Título
st.markdown("<h1 style='text-align: center;'>🐻 Soop Buscador de Productos</h1>", unsafe_allow_html=True)

# Funciones para sincronizar los buscadores de código y nombre
if 'selected_codigo' not in st.session_state:
    st.session_state.selected_codigo = ''
if 'selected_nombre' not in st.session_state:
    st.session_state.selected_nombre = ''

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

# Crear dos columnas para los buscadores de código y nombre
col_codigo, col_nombre = st.columns([1, 2])

with col_codigo:
    codigo_lista = [""] + df['Codigo'].astype(str).unique().tolist()
    st.selectbox("Buscar por Código", codigo_lista, key='selected_codigo', on_change=on_codigo_change)

with col_nombre:
    nombre_lista = [""] + df['Nombre'].unique().tolist()
    st.selectbox("Buscar por Nombre", nombre_lista, key='selected_nombre', on_change=on_nombre_change)

# Si se selecciona un código o nombre, mostrar el producto
if st.session_state.selected_codigo and st.session_state.selected_nombre:
    producto_seleccionado = df[df['Codigo'] == st.session_state.selected_codigo].iloc[0]

    # Agregar los checkboxes de precio por mayor y calculador de descuentos
    col1, col2 = st.columns(2)
    with col1:
        mostrar_mayorista = st.checkbox("Mostrar Precio por Mayor")
    with col2:
        descuento = st.number_input("Calcular descuento (%)", min_value=0, max_value=100, step=1, value=0)

    # Mostrar producto completo con formato mejorado
    def mostrar_producto_completo(producto, mostrar_mayorista, descuento):
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

        # Mostrar descripción y categorías
        st.markdown(f"<p style='font-size: 26px;'>Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}</p>", unsafe_allow_html=True)
        st.write(f"<p style='font-size: 24px;'>Categorías: {producto['Categorias']}</p>", unsafe_allow_html=True)

        # Checkbox para mostrar ubicación
        if st.checkbox('Mostrar Ubicación'):
            st.write(f"Pasillo: {producto.get('Pasillo', 'Sin datos')}")
            st.write(f"Estante: {producto.get('Estante', 'Sin datos')}")
            st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")

    mostrar_producto_completo(producto_seleccionado, mostrar_mayorista, descuento)

# Variables para las casillas de categorías, novedades y rubros
col_opciones = st.columns(3)
with col_opciones[0]:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col_opciones[1]:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
with col_opciones[2]:
    sugerir_por_rubro = st.checkbox("Sugerir por Rubro (Próximamente)")

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
        for i, producto in productos_categoria.iloc[(pagina-1)*10:pagina*10].iterrows():
            st.write(f"<span style='font-size: 20px; font-weight: bold;'>{producto['Nombre']}</span> - Código: {producto['Codigo']} | Precio: ${producto['Precio']:,.0f}", unsafe_allow_html=True)

# Ordenar por novedad
if ordenar_por_novedad:
    if 'Fecha Creado' in df.columns:
        df_ordenado = df.sort_values('Fecha Creado', ascending=False)
        num_paginas = (len(df_ordenado) // 10) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        for i, producto in df_ordenado.iloc[(pagina-1)*10:pagina*10].iterrows():
            st.write(f"<span style='font-size: 20px; font-weight: bold;'>{producto['Nombre']}</span> - Código: {producto['Codigo']} | Precio: ${producto['Precio']:,.0f}", unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
