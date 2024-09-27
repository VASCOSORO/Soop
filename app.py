import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# Cargar el archivo Excel
@st.cache_data
def load_data():
    df = pd.read_excel('1083.xlsx', engine='openpyxl')  # Asegúrate de que el archivo Excel esté en el mismo directorio y se carguen todas las filas
    return df

# Función para cargar la imagen desde una URL
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
    elif stock < 0:  # Cambiado para incluir stock negativo
        return 'red'
    elif stock < 3:
        return 'orange'
    else:
        return 'black'  # Color por defecto para stock >= 3

# Mostrar producto en formato completo (con imagen)
def mostrar_producto_completo(producto):
    st.markdown(f"<h3 style='font-size: 36px;'>{producto['Nombre']}</h3>", unsafe_allow_html=True)  # Ajustar tamaño del título
    st.markdown(f"<span style='font-size: 28px; font-weight: bold;'>Código: {producto['Codigo']} | Precio: ${producto['Precio']} | Stock: {producto['Stock']}</span>", unsafe_allow_html=True)  # Mostrar código, precio y stock

    imagen_url = producto.get('imagen', '')
    if imagen_url:
        imagen = cargar_imagen(imagen_url)
        if imagen:
            st.image(imagen, use_column_width=True)
        else:
            st.write("Imagen no disponible.")

    # Mostrar descripción debajo de la imagen
    st.markdown(f"<p style='font-size: 26px;'>Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}</p>", unsafe_allow_html=True)
    
    # Mostrar categorías debajo de la descripción
    st.write(f"<p style='font-size: 24px;'>Categorías: {producto['Categorias']}</p>", unsafe_allow_html=True)

    # Checkbox para mostrar ubicación
    if st.checkbox('Mostrar Ubicación'):
        st.write(f"Pasillo: {producto.get('Pasillo', 'Sin datos')}")
        st.write(f"Estante: {producto.get('Estante', 'Sin datos')}")
        st.write(f"Proveedor: {producto.get('Proveedor', 'Sin datos')}")

# Mostrar productos en formato de lista con imágenes (paginar resultados)
def mostrar_lista_productos(df, pagina, productos_por_pagina=10):
    inicio = (pagina - 1) * productos_por_pagina
    fin = inicio + productos_por_pagina
    productos_pagina = df.iloc[inicio:fin]

    for i, producto in productos_pagina.iterrows():
        col1, col2 = st.columns([1, 3])  # Dos columnas: una para la imagen y otra para los detalles
        with col1:
            imagen_url = producto.get('imagen', '')
            if imagen_url:
                imagen = cargar_imagen(imagen_url)
                if imagen:
                    st.image(imagen, width=140)  # Imagen al 30% más grande
                else:
                    st.write("Imagen no disponible.")

        with col2:
            st.write(f"### {producto['Nombre']}")
            stock_color = obtener_color_stock(producto['Stock'])
            st.markdown(f"Código: {producto['Codigo']} | Precio: ${producto['Precio']} | <span style='color: {stock_color};'>STOCK: {producto['Stock']}</span>", unsafe_allow_html=True)  # Cambiar color del stock
            st.write(f"Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}")
            st.write(f"Categorías: {producto['Categorias']}")
        st.write("---")
    
    total_paginas = (len(df) + productos_por_pagina - 1) // productos_por_pagina
    col1, col2, col3 = st.columns([1, 2, 1])

# Cargar datos
df = load_data()

# Título
st.markdown("<h1 style='text-align: center;'>🐻 Super Buscador de Productos</h1>", unsafe_allow_html=True)  # Centrar título

# Mostrar número de filas y columnas cargadas
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Campo de búsqueda
busqueda = st.selectbox("Escribí acá para buscar", [''] + list(df['Nombre']), index=0)

# Condición para mostrar la imagen del bot
if busqueda == '':
    st.image('bot (8).png', width=200)  # Mostrar imagen solo si el buscador está vacío

# Verificar si el usuario ha escrito algo y filtrar productos
if busqueda:
    productos_filtrados = df[df['Nombre'].str.contains(busqueda, case=False)]
    if not productos_filtrados.empty:
        # Mostrar producto seleccionado
        producto_seleccionado = productos_filtrados.iloc[0]  # Solo muestra el primero
        mostrar_producto_completo(producto_seleccionado)

# Alinear correctamente las opciones con un espacio arriba
st.write("")  # Espacio
col_opciones = st.columns(3)
with col_opciones[0]:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col_opciones[1]:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
with col_opciones[2]:
    sugerir_por_rubro = st.checkbox("Sugerir por Rubro (Próximamente)")

# Ver lista por categorías
if ver_por_categorias:
    categoria = st.selectbox('Categorías:', sorted(df['Categorias'].dropna().unique()))
    if categoria:  # Solo proceder si se selecciona una categoría
        productos_categoria = df[df['Categorias'].str.contains(categoria)]
        pagina = st.number_input('Página:', min_value=1, value=1)
        mostrar_lista_productos(productos_categoria, pagina)

# Ordenar por novedad
if ordenar_por_novedad:
    if 'Fecha Creado' in df.columns:
        df_ordenado = df.sort_values('Fecha Creado', ascending=False)
        pagina = st.number_input('Página:', min_value=1, value=1)
        mostrar_lista_productos(df_ordenado, pagina)
    else:
        st.warning("No se encontró la columna 'Fecha Creado'.")

# Sugerir por Rubro (en desarrollo)
if sugerir_por_rubro:
    st.info("Esta función estará disponible próximamente.")
