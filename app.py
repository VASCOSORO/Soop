import streamlit as st
import pandas as pd

# Cargar el archivo de Excel
ruta_excel = '1083.xlsx'

# Verificar si el archivo fue cargado correctamente
@st.cache_data
def cargar_datos(ruta):
    try:
        df = pd.read_excel(ruta)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

df = cargar_datos(ruta_excel)

# Mostrar mensaje si no se carga el DataFrame
if df is None:
    st.stop()

# Convertir la columna 'Fecha Creado' a datetime si existe
if 'Fecha Creado' in df.columns:
    df['Fecha Creado'] = pd.to_datetime(df['Fecha Creado'], errors='coerce')

# Extraer categorías únicas
def obtener_categorias_unicas(df):
    if 'Categorias' in df.columns:
        categorias_series = df['Categorias'].dropna().apply(lambda x: [cat.strip() for cat in x.split(',')])
        todas_categorias = set()
        for lista_cats in categorias_series:
            todas_categorias.update(lista_cats)
        return sorted(todas_categorias)
    else:
        return []

lista_categorias = obtener_categorias_unicas(df)

# Diseño y estructura
st.title("🧐 Super Buscador de Productos")

st.success("Archivo cargado exitosamente.")
st.write(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Opciones de filtrado
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    checkbox_categorias = st.checkbox("Ver lista por Categorías", value=False)
with col2:
    checkbox_ordenar_novedad = st.checkbox("Ordenar por Novedad")
with col3:
    st.checkbox("Sugerir por Rubro (Próximamente)", disabled=True)

# Campo de búsqueda
st.text_input("🔍 Ingresá el nombre del producto", key="producto_buscar")

# Mostrar lista desplegable de categorías si el checkbox está activo
if checkbox_categorias:
    categoria_seleccionada = st.selectbox("Categorías:", options=[""] + lista_categorias)

# Paginación
productos_por_pagina = 10
pagina_actual = st.number_input("Página:", min_value=1, step=1, value=1)

# Filtrar productos por la categoría seleccionada
if checkbox_categorias and categoria_seleccionada:
    df_filtrado = df[df['Categorias'].str.contains(categoria_seleccionada, na=False)]
else:
    df_filtrado = df.copy()

# Filtrar por novedad si está activo
if checkbox_ordenar_novedad and 'Fecha Creado' in df_filtrado.columns:
    df_filtrado = df_filtrado.sort_values(by='Fecha Creado', ascending=False)

# Filtrar productos por búsqueda
producto_buscar = st.session_state.producto_buscar
if producto_buscar:
    df_filtrado = df_filtrado[df_filtrado['Nombre'].str.contains(producto_buscar, case=False, na=False)]

# Paginación
inicio = (pagina_actual - 1) * productos_por_pagina
fin = inicio + productos_por_pagina
df_paginado = df_filtrado.iloc[inicio:fin]

# Mostrar productos en formato "tarjeta"
for idx, fila in df_paginado.iterrows():
    col1, col2 = st.columns([1, 3])
    with col1:
        if 'Imagen' in fila and pd.notna(fila['Imagen']):
            st.image(fila['Imagen'], width=100)  # Mostrar la imagen si está disponible
        else:
            st.image("https://via.placeholder.com/100", width=100)  # Imagen de marcador si no hay imagen disponible
    with col2:
        st.markdown(f"### {fila['Nombre']}")
        st.write(f"**Código**: {fila['Codigo']}")
        st.write(f"**Stock**: {fila['Stock']}")
        st.write(f"**Precio**: {fila['Precio']}")
        st.write(f"**Descripción**: {fila.get('Descripción', 'Sin descripción disponible')}")
        st.write(f"**Categorías**: {fila['Categorias']}")
    st.markdown("---")

# Mostrar botones de navegación de páginas en línea
total_paginas = (len(df_filtrado) // productos_por_pagina) + 1
if total_paginas > 1:
    col1, col2 = st.columns([1, 1])
    with col1:
        if pagina_actual > 1:
            if st.button("Página anterior"):
                st.session_state.pagina_actual = pagina_actual - 1
    with col2:
        if pagina_actual < total_paginas:
            if st.button("Página siguiente"):
                st.session_state.pagina_actual = pagina_actual + 1
    st.write(f"Página {pagina_actual} de {total_paginas}")
