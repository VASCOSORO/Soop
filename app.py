import os
os.system('pip install --upgrade pip')
os.system('pip install pillow==9.2.0')

import streamlit as st
import pandas as pd
import os

# Título de la aplicación
st.title('Super Buscador de Productos')

# Ruta del archivo Excel
ruta_excel = '1083_productos_al_24_de_sep.xlsx'  # Asegúrate de que este archivo esté en el repositorio

# Cargar el DataFrame desde el archivo de Excel
@st.cache_data
def cargar_datos(ruta):
    try:
        df = pd.read_excel(ruta)
        st.success("DataFrame cargado exitosamente.")
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo de Excel: {e}")
        return None

df = cargar_datos(ruta_excel)

if df is not None:
    # Convertir la columna 'Fecha Creado' a datetime si existe
    if 'Fecha Creado' in df.columns:
        df['Fecha Creado'] = pd.to_datetime(df['Fecha Creado'], errors='coerce')
    else:
        st.warning("La columna 'Fecha Creado' no existe en el DataFrame.")

    # Obtener categorías únicas
    def obtener_categorias_unicas(df):
        if 'Categorias' in df.columns:
            categorias_series = df['Categorias'].dropna().apply(lambda x: [cat.strip() for cat in x.split(',')])
            todas_categorias = set()
            for lista_cats in categorias_series:
                todas_categorias.update(lista_cats)
            return sorted(todas_categorias)
        else:
            st.warning("La columna 'Categorias' no existe en el DataFrame.")
            return []

    lista_categorias = obtener_categorias_unicas(df)

    # Sidebar para filtros
    st.sidebar.header("Filtros de Búsqueda")

    nombre_producto = st.sidebar.text_input('Buscar por nombre de producto')
    categoria_seleccionada = st.sidebar.selectbox('Seleccionar Categoría', ['Todas'] + lista_categorias)
    ordenar_novedad = st.sidebar.checkbox('Ordenar por Novedad')

    # Filtrar DataFrame según los filtros
    def filtrar_datos(df, nombre, categoria, ordenar):
        if nombre:
            df = df[df['Nombre'].str.contains(nombre, case=False, na=False)]
        if categoria and categoria != 'Todas':
            df = df[df['Categorias'].str.contains(categoria, case=False, na=False)]
        if ordenar and 'Fecha Creado' in df.columns:
            df = df.sort_values('Fecha Creado', ascending=False)
        return df

    df_filtrado = filtrar_datos(df, nombre_producto, categoria_seleccionada, ordenar_novedad)

    # Mostrar resultados
    st.subheader("Resultados de la Búsqueda")
    st.dataframe(df_filtrado)

    # Detalles del producto seleccionado
    producto_seleccionado = st.selectbox('Seleccionar Producto', df_filtrado['Nombre'].unique())

    if producto_seleccionado:
        producto = df_filtrado[df_filtrado['Nombre'] == producto_seleccionado].iloc[0]
        st.markdown(f"### {producto['Nombre']}")
        st.image(producto.get('imagen', ''), caption=producto['Nombre'], use_column_width=True)
        st.write(f"**Código:** {producto.get('Codigo', 'Sin datos')}")
        st.write(f"**Stock:** {producto.get('Stock', 'Sin datos')}")
        st.write(f"**Precio Jugueterías:** ${producto.get('Precio Jugueterias face', 'Sin datos')}")
        st.write(f"**Descripción:** {producto.get('Descripción', 'Sin datos')}")
        st.write(f"**Categorías:** {producto.get('Categorias', 'Sin datos')}")
        st.write(f"**Pasillo:** {producto.get('Pasillo', 'Sin datos')}")
        st.write(f"**Estante:** {producto.get('Estante', 'Sin datos')}")
        st.write(f"**Proveedor:** {producto.get('Proveedor', 'Sin datos')}")
