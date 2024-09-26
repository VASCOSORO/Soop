import os
import streamlit as st
import pandas as pd

# Actualización de pip y pillow para evitar errores de instalación
os.system('pip install --upgrade pip')
os.system('pip install pillow==9.2.0')

# Título de la aplicación
st.title('Super Buscador de Productos')

# Ruta del archivo Excel
ruta_excel = '1083.xlsx'  # Asegúrate de que este archivo esté en el repositorio

# Mensaje de depuración para verificar que la aplicación empieza
st.write("Iniciando la aplicación...")

# Cargar el DataFrame desde el archivo de Excel
@st.cache_data
def cargar_datos(ruta):
    try:
        df = pd.read_excel(ruta)
        st.success("Archivo cargado exitosamente.")  # Mensaje de depuración
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Verificar si el archivo fue cargado
df = cargar_datos(ruta_excel)

if df is None:
    st.error("No se pudo cargar el archivo de Excel.")
else:
    st.write(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Convertir la columna 'Fecha Creado' a datetime si no lo está
if 'Fecha Creado' in df.columns:
    df['Fecha Creado'] = pd.to_datetime(df['Fecha Creado'], errors='coerce')

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

# Widgets de búsqueda
ver_categorias = st.checkbox('Ver lista por Categorías')
ordenar_novedad = st.checkbox('Ordenar por Novedad')
sugerir_rubro = st.checkbox('Sugerir por Rubro (Próximamente)', disabled=True)

# Dropdown para seleccionar la categoría si se activa la opción de ver categorías
if ver_categorias:
    categoria_seleccionada = st.selectbox("Categorías:", options=lista_categorias)

# Búsqueda por nombre
entrada_busqueda = st.text_input("🔍 Ingresá el nombre del producto")

if entrada_busqueda:
    # Filtrar productos por nombre
    coincidencias = df[df['Nombre'].str.contains(entrada_busqueda, case=False, na=False)]
    if not coincidencias.empty:
        st.write(f"Se encontraron {coincidencias.shape[0]} productos.")
        st.table(coincidencias[['Nombre', 'Codigo', 'Stock', 'Precio', 'Categorias']])
    else:
        st.write("No se encontraron productos con ese nombre.")
elif ver_categorias and categoria_seleccionada:
    # Filtrar productos por categoría seleccionada
    coincidencias = df[df['Categorias'].str.contains(categoria_seleccionada, case=False, na=False)]
    st.write(f"Productos en la categoría {categoria_seleccionada}:")
    st.table(coincidencias[['Nombre', 'Codigo', 'Stock', 'Precio', 'Categorias']])
else:
    st.write("Esperando entrada de búsqueda o selección de categoría...")

# Mostrar imagen si existe
ruta_imagen = 'super_buscador.png'  # Asegúrate de que la imagen esté en el repositorio
if os.path.exists(ruta_imagen):
    st.image(ruta_imagen, caption="Super Buscador", use_column_width=True)
else:
    st.error("Imagen del Super Buscador no encontrada.")
