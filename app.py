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
    elif stock <= 1:
        return 'orange'
    else:
        return 'black'

# Mostrar producto en formato completo (con imagen)
def mostrar_producto_completo(producto, mostrar_mayorista, mostrar_descuento, descuento, img_size):
    st.markdown(f"<h3 style='font-size: 36px;'>{producto['Nombre']}</h3>", unsafe_allow_html=True)

    # Mostrar precio según el checkbox de precio por mayor
    if mostrar_mayorista:
        precio_mostrar = producto['Precio']
        tipo_precio = "Precio x Mayor"
    else:
        precio_mostrar = producto['Precio Jugueterias face']
        tipo_precio = "Precio Jugueterías Face"

    precio_formateado = f"{precio_mostrar:,.0f}".replace(",", ".")  # Formatear el precio sin decimales
    stock_color = obtener_color_stock(producto['Stock'])  # Cambiar el color del stock según el valor
    st.markdown(f"<span style='font-size: 28px; font-weight: bold;'>Código: {producto['Codigo']} | {tipo_precio}: ${precio_formateado} | <span style='color: {stock_color};'>Stock: {producto['Stock']}</span></span>", unsafe_allow_html=True)

    # Mostrar el precio con descuento si se aplica
    if mostrar_descuento and descuento > 0:
        precio_descuento = precio_mostrar * (1 - descuento / 100)
        st.markdown(f"<span style='font-size: 24px; color:blue;'>Precio con {descuento}% de descuento: ${precio_descuento:,.0f}</span>", unsafe_allow_html=True)

    # Mostrar descripción y categorías
    st.markdown(f"<p style='font-size: 26px;'>Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}</p>", unsafe_allow_html=True)
    st.write(f"<p style='font-size: 24px;'>Categorías: {producto['Categorias']}</p>", unsafe_allow_html=True)

    # Mostrar la imagen con el tamaño ajustable
    imagen_url = producto.get('imagen', '')
    if imagen_url:
        imagen = cargar_imagen(imagen_url)
        if imagen:
            st.image(imagen, width=img_size)  # Usar el tamaño ajustado por el slider
        else:
            st.write("Imagen no disponible.")

    # Checkbox para mostrar ubicación
    if st.checkbox('Mostrar Ubicación'):
        st.write(f"Pasillo: {producto.get('Pasillo', 'Sin datos')}")
        st.write(f"Estante: {producto.get('Estante', 'Sin datos')}")
        st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")

# Mostrar productos en formato de lista con imágenes (paginar resultados)
def mostrar_lista_productos(df, pagina, img_size, productos_por_pagina=10):
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
                    st.image(imagen, width=img_size)  # Tamaño ajustable de la imagen
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

# Checkbox para mostrar/ocultar la sección de la fecha, mensaje de filas y el botón de actualizar
mostrar_seccion_superior = st.checkbox("Mostrar detalles de archivo y botón de actualización", value=True)

# Si el checkbox está activado, mostrar la sección superior
if mostrar_seccion_superior:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<p style='font-size: 12px;'>Última modificación del archivo {archivo}: {fecha_ultima_modificacion}</p>", unsafe_allow_html=True)
        st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

    with col2:
        if st.button('Actualizar datos'):
            st.cache_data.clear()  # Limpiar la caché para asegurarse de cargar los datos actualizados

# Línea negra sobre el título y arriba de "Soop Buscador"
st.markdown("<hr style='border:2px solid black'>", unsafe_allow_html=True)

# Título
st.markdown("<h1 style='text-align: center;'>🐻 Soop 2.o beta 🧐 </h1>", unsafe_allow_html=True)

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

    # Agregar el checkbox para mostrar precio por mayor, calculador de descuento y slider para ajustar tamaño de imagen
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        mostrar_mayorista = st.checkbox("Mostrar Precio por Mayor")
    with col2:
        mostrar_descuento = st.checkbox("Mostrar calculador de descuento")
    with col3:
        if mostrar_descuento:
            descuento = st.number_input("Calcular descuento (%)", min_value=0, max_value=100, step=1, value=0)
        else:
            descuento = 0
    with col4:
        img_size = st.slider("Tamaño de imagen", min_value=100, max_value=400, value=200)

    # Mostrar el producto con las opciones de precio por mayor, descuento y tamaño de imagen ajustable
    mostrar_producto_completo(producto_data, mostrar_mayorista=mostrar_mayorista, mostrar_descuento=mostrar_descuento, descuento=descuento, img_size=img_size)

# Sección para ver lista por categorías o por novedades
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
        productos_categoria = df[df['Categorias'].apply(lambda x: categoria_seleccionada in str(x).split(','))]
        num_paginas = (len(productos_categoria) // 10) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        mostrar_lista_productos(productos_categoria, pagina, img_size)

# Ordenar por novedad
if ordenar_por_novedad:
    if 'Fecha Creado' in df.columns:
        df_ordenado = df.sort_values('Fecha Creado', ascending=False)
        num_paginas = (len(df_ordenado) // 10) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        mostrar_lista_productos(df_ordenado, pagina, img_size)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
