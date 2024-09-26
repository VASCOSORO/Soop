import os
import streamlit as st
import pandas as pd

# Título de la aplicación
st.set_page_config(page_title="Super Buscador de Productos", layout="wide")
st.title('🔍 Super Buscador de Productos')

# Ruta del archivo Excel
ruta_excel = '1083.xlsx'  # Asegúrate de que este archivo esté en el repositorio

# Mensaje de depuración para verificar que la aplicación empieza
st.write("Iniciando la aplicación...")

# Cargar el DataFrame desde el archivo de Excel
@st.cache_data
def cargar_datos(ruta):
    try:
        df = pd.read_excel(ruta)
        st.success("Archivo cargado exitosamente.")  # Mensaje de éxito
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Verificar si el archivo fue cargado
df = cargar_datos(ruta_excel)

if df is None:
    st.write("No se pudo cargar el archivo de Excel.")
else:
    st.write(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Convertir la columna 'Fecha Creado' a datetime si no lo está
if 'Fecha Creado' in df.columns:
    df['Fecha Creado'] = pd.to_datetime(df['Fecha Creado'], errors='coerce')
    st.write("Columna 'Fecha Creado' convertida a formato de fecha.")
else:
    st.write("La columna 'Fecha Creado' no existe en el DataFrame.")

# Separar las categorías individuales y obtener una lista única
def obtener_categorias_unicas(df):
    if 'Categorias' in df.columns:
        categorias_series = df['Categorias'].dropna().apply(lambda x: [cat.strip() for cat in x.split(',')])
        todas_categorias = set()
        for lista_cats in categorias_series:
            todas_categorias.update(lista_cats)
        return sorted(todas_categorias)
    else:
        st.write("La columna 'Categorias' no existe en el DataFrame.")
        return []

lista_categorias = obtener_categorias_unicas(df)
st.write(f"Categorías únicas encontradas: {lista_categorias}")

# Función para mostrar el producto seleccionado con el estilo preferido
def mostrar_producto_formato_completo(producto):
    st.subheader(f"Detalles del producto: {producto['Nombre']}")
    st.write(f"**Código**: {producto['Codigo']}")
    st.write(f"**Stock**: {producto['Stock']}")
    st.write(f"**Precio Jugueterías Face**: ${producto.get('Precio Jugueterias face', 'Sin datos')}")
    st.write(f"**Precio Mayorista**: ${producto.get('Precio', 'Sin datos')}")
    st.write(f"**Categorías**: {producto['Categorias']}")
    st.write(f"**Descripción**: {producto.get('Descripción', 'Sin datos')}")
    # Si hay URL de imagen, mostrarla
    img_url = producto.get('imagen', '')
    if img_url and img_url != 'Sin datos':
        st.image(img_url, width=300, caption="Imagen del producto")

# Cuadro de búsqueda centrado
entrada_busqueda = st.text_input("🔍 Ingresá el nombre del producto")

# Filtrar los productos por nombre cuando se ingresa un texto en la búsqueda
if entrada_busqueda:
    coincidencias = df[df['Nombre'].str.contains(entrada_busqueda, case=False, na=False)]
    if not coincidencias.empty:
        st.write(f"Se encontraron {coincidencias.shape[0]} productos.")
        # Mostrar los resultados en una tabla
        st.dataframe(coincidencias[['Nombre', 'Codigo', 'Stock', 'Precio', 'Categorias']].reset_index(drop=True))

        # Selección del primer producto para mostrar detalles
        primer_producto = coincidencias.iloc[0].to_dict()
        mostrar_producto_formato_completo(primer_producto)
    else:
        st.warning("No se encontraron productos con ese nombre.")
else:
    st.info("Esperando entrada de búsqueda...")

# Mostrar imagen del Super Buscador si no hay búsqueda
ruta_imagen_super_buscador = 'bot_8.png'  # Asegúrate de que esta imagen esté en el repositorio

if os.path.exists(ruta_imagen_super_buscador):
    st.image(ruta_imagen_super_buscador, caption="Super Buscador de Productos", use_column_width=True)
else:
    st.error("Imagen del Super Buscador no encontrada.")
