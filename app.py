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
    columnas_requeridas = ["Precio", "Precio x Mayor", "Stock", "StockSuc2"]
    for columna in columnas_requeridas:
        if columna not in df.columns:
            st.error(f"La columna '{columna}' no se encuentra en el archivo cargado.")
            st.stop()

# Checkbox para mostrar/ocultar la sección de detalles de archivo y actualización
mostrar_seccion_superior = st.checkbox("Mostrar detalles de archivo y botón de actualización", value=False)

# Si el checkbox está activado, mostrar la sección superior
if mostrar_seccion_superior:
    st.success("Archivo cargado correctamente.")
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
                        csv_data = pd.read_csv(uploaded_file, encoding="utf-8", sep=None, engine="python")
                        csv_data.to_excel(file_path, index=False, engine='openpyxl')
                        st.success("Archivo CSV convertido a Excel y guardado correctamente.")
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
    st.markdown(f"<h3 style='font-size: 36px;'>{producto['Nombre']}</h3>", unsafe_allow_html=True)
    
    precio = producto['Precio x Mayor'] if mostrar_mayorista else producto['Precio']
    if mostrar_descuento:
        precio_descuento = precio * (1 - descuento / 100)
        st.markdown(f"<span style='font-size: 24px; color:blue;'>Precio con {descuento}% de descuento: ${precio_descuento:,.2f}</span>", unsafe_allow_html=True)
    else:
        precio_descuento = precio

    st.markdown(f"<span style='font-size: 28px; font-weight: bold;'>Código: {producto['Codigo']} | Precio: ${precio_descuento:,.2f} | Disponible en Suc 2: {'Sin stock' if producto['StockSuc2'] == 0 else int(producto['StockSuc2'])}</span>", unsafe_allow_html=True)
    
    stock_color = obtener_color_stock(producto['Stock'])
    st.markdown(f"<span style='font-size: 24px; color: {stock_color};'>Stock: {producto['Stock']}</span>", unsafe_allow_html=True)

    # Mostrar imagen del producto con controles de tamaño
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
        if st.button("➕"):
            st.session_state.img_size = min(st.session_state.get('img_size', 300) + 50, 600)
        if st.button("➖"):
            st.session_state.img_size = max(st.session_state.get('img_size', 300) - 50, 100)

    # Opción para mostrar u ocultar la ubicación
    if st.checkbox('Mostrar Ubicación'):
        st.write(f"Pasillo: {producto.get('Pasillo', 'Sin datos')}")
        st.write(f"Estante: {producto.get('Estante', 'Sin datos')}")
        st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")

# Si se selecciona un código y un nombre, mostrar el producto
if st.session_state.selected_codigo and st.session_state.selected_nombre:
    producto_data = df[df['Codigo'] == st.session_state.selected_codigo].iloc[0]
    mostrar_mayorista = st.checkbox("Mostrar Precio por Mayor")
    mostrar_descuento = st.checkbox("Mostrar calculador de descuento")
    descuento = st.number_input("Calcular descuento (%)", min_value=0, max_value=100, step=1) if mostrar_descuento else 0
    mostrar_producto_completo(producto_data, mostrar_mayorista, mostrar_descuento, descuento)

# Función para mostrar lista de productos con paginación
def mostrar_lista_productos(df, pagina, productos_por_pagina=10):
    inicio = (pagina - 1) * productos_por_pagina
    fin = inicio + productos_por_pagina
    productos_pagina = df.iloc[inicio:fin]

    for _, producto in productos_pagina.iterrows():
        st.write(f"**Nombre:** {producto['Nombre']}")
        st.write(f"**Código:** {producto['Codigo']}")
        st.write(f"**Precio:** ${producto['Precio']:,.2f}")
        st.write(f"**Precio x Mayor:** ${producto['Precio x Mayor']:,.2f}")
        
        # Stock y Disponibilidad en Sucursal 2
        stock_disponible_suc2 = "Sin stock" if producto['StockSuc2'] == 0 else int(producto['StockSuc2'])
        st.write(f"**Disponible en Suc 2:** {stock_disponible_suc2}")
        
        # Otros detalles
        stock_color = 'green' if producto['Stock'] > 5 else 'orange' if producto['Stock'] > 0 else 'red'
        st.markdown(f"<span style='color: {stock_color};'>**Stock:** {producto['Stock']}</span>", unsafe_allow_html=True)
        
        # Información adicional
        st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")
        st.write(f"Ubicación - Pasillo: {producto.get('Pasillo', 'Sin datos')}, Estante: {producto.get('Estante', 'Sin datos')}, Columna: {producto.get('Columna', 'Sin datos')}")
        
        if producto.get("imagen"):
            imagen = cargar_imagen(producto["imagen"])
            if imagen:
                st.image(imagen, width=100)
        st.write("---")

# Filtros para mostrar productos por categoría o novedad
ver_por_categorias = st.checkbox("Ver lista por Categorías")
ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
filtro_codigo = st.checkbox("Listado por Inicio de Código")

# Mostrar lista por categorías
if ver_por_categorias:
    categorias = sorted(set([c.strip() for cat in df['Categorias'].dropna().unique() for c in cat.split(',')]))
    categoria_seleccionada = st.selectbox('Categorías:', categorias)
    productos_categoria = df[df['Categorias'].str.contains(categoria_seleccionada, na=False)]
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

# Filtro por Inicio de Código
if filtro_codigo:
    prefijo_codigo = st.text_input("Ingresa el prefijo del código")
    if prefijo_codigo:
        productos_prefijo = df[df['Codigo'].str.startswith(prefijo_codigo, na=False)]
        num_paginas = (len(productos_prefijo) // 10) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        mostrar_lista_productos(productos_prefijo, pagina)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
