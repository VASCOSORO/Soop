import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from datetime import datetime
import pytz  # Para manejar zonas horarias
# ========Soop 2.0.2 
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

# Mostrar productos en formato de lista con imágenes (paginación, sin control de tamaño)
def mostrar_lista_productos(df, pagina, productos_por_pagina=25):
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
            st.write(f"Categorías: {producto['Etiquetas']}")
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

# Sección para ver lista por categorías o por novedades
col_opciones = st.columns(3)
with col_opciones[0]:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col_opciones[1]:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
with col_opciones[2]:
    st.checkbox("Sugerir por Rubro (Próximamente)")

# Ver lista por categorías
if ver_por_categorias:
    todas_las_categorias = df['Etiquetas'].dropna().unique()
    categorias_individuales = set()
    for categorias in todas_las_categorias:
        for categoria in categorias.split(','):
            categorias_individuales.add(categoria.strip())
    categoria_seleccionada = st.selectbox('Categorías:', sorted(categorias_individuales))
    if categoria_seleccionada:
        productos_categoria = df[df['Etiquetas'].apply(lambda x: categoria_seleccionada in str(x).split(','))]
        num_paginas = (len(productos_categoria) // 25) + 1
        pagina = st.number_input('Página:', min_value=1, max_value=num_paginas, value=1)
        mostrar_lista_productos(productos_categoria, pagina)

# Ordenar por novedad y paginar resultados
if ordenar_por_novedad:
    if 'Fecha Creada' in df.columns:
        # Asegurarse de que la columna esté en formato de fecha
        df['Fecha Creada'] = pd.to_datetime(df['Fecha Creada'], errors='coerce')
        df_ordenado = df.sort_values('Fecha Creada', ascending=False).dropna(subset=['Fecha Creada'])
        
        total_paginas = (len(df_ordenado) // 25) + 1
        pagina_actual = st.number_input('Página:', min_value=1, max_value=total_paginas, value=1)
        mostrar_lista_productos(df_ordenado, pagina_actual)

        # Botones de navegación entre páginas
        col_nav = st.columns(2)
        with col_nav[0]:
            if st.button("⬅️ Página anterior", disabled=(pagina_actual <= 1)):
                st.session_state['pagina_actual'] = pagina_actual - 1
        with col_nav[1]:
            if st.button("➡️ Página siguiente", disabled=(pagina_actual >= total_paginas)):
                st.session_state['pagina_actual'] = pagina_actual + 1

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Powered by VASCO.SORO</p>", unsafe_allow_html=True)
