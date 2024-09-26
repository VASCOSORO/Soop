import os
import streamlit as st
import pandas as pd

# Título de la aplicación
st.title('🧐 Super Buscador de Productos')

# Ruta del archivo Excel
ruta_excel = '1083.xlsx'

# Cargar el DataFrame desde el archivo de Excel
@st.cache_data
def cargar_datos(ruta):
    try:
        df = pd.read_excel(ruta)
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Función para obtener valores del producto de manera segura
def obtener_valor(producto, campo):
    valor = producto.get(campo, 'Sin datos')
    return 'Sin datos' if pd.isna(valor) or valor == '' else valor

# Función para mostrar el producto seleccionado con el estilo preferido
def mostrar_producto_formato_completo(producto):
    stock = obtener_valor(producto, 'Stock')
    precio = obtener_valor(producto, 'Precio')
    descripcion = obtener_valor(producto, 'Descripción') or obtener_valor(producto, 'Descripcion')
    categorias = obtener_valor(producto, 'Categorias')
    codigo = obtener_valor(producto, 'Codigo')
    nombre = obtener_valor(producto, 'Nombre')
    img_url = obtener_valor(producto, 'imagen')  # El campo de la imagen
    pasillo = obtener_valor(producto, 'Pasillo')
    estante = obtener_valor(producto, 'Estante')
    proveedor = obtener_valor(producto, 'Proveedor')
    
    # Mostrar detalles del producto con imagen y opciones de ubicación
    st.write(f"### {nombre}")
    st.write(f"**Código:** {codigo}")
    st.write(f"**Stock:** {stock}")
    st.write(f"**Precio:** {precio}")
    st.write(f"**Descripción:** {descripcion}")
    st.write(f"**Categorías:** {categorias}")

    # Mostrar la imagen del producto si está disponible
    if img_url != 'Sin datos':
        st.image(img_url, use_column_width=True)
    else:
        st.write("Imagen no disponible")

    # Checkbox para mostrar/ocultar ubicación
    if st.checkbox('Mostrar Ubicación'):
        st.write(f"**Pasillo:** {pasillo}")
        st.write(f"**Estante:** {estante}")
        st.write(f"**Proveedor:** {proveedor}")

# Función para filtrar productos por búsqueda de nombre
def filtrar_productos(df, texto):
    if 'Nombre' in df.columns:
        coincidencias = df[df['Nombre'].str.contains(texto, case=False, na=False)]
        return coincidencias
    else:
        st.write("No se encuentra la columna 'Nombre' en los datos.")
        return pd.DataFrame()

# Cargar el archivo Excel
df = cargar_datos(ruta_excel)

if df is None:
    st.stop()

# Input de búsqueda
entrada_busqueda = st.text_input("🔍 Ingresá el nombre del producto")

# Mostrar la búsqueda en tiempo real con selección dinámica
if entrada_busqueda:
    productos_filtrados = filtrar_productos(df, entrada_busqueda)
    opciones = {f"{fila['Nombre']} (Código: {fila['Codigo']})": fila.to_dict() for idx, fila in productos_filtrados.iterrows()}

    if opciones:
        seleccionado = st.selectbox('Seleccionar:', opciones.keys())
        if seleccionado:
            producto = opciones[seleccionado]
            mostrar_producto_formato_completo(producto)
    else:
        st.write("No se encontraron productos con ese nombre.")

# Casillas de verificación
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    ver_lista_por_categoria = st.checkbox("Ver lista por Categorías")
with col2:
    ordenar_novedad = st.checkbox("Ordenar por Novedad")
with col3:
    sugerir_rubro = st.checkbox("Sugerir por Rubro (Próximamente)")

# Lógica para la paginación
if ver_lista_por_categoria:
    categorias_unicas = df['Categorias'].str.split(',', expand=True).stack().str.strip().unique()
    categoria_seleccionada = st.selectbox('Categorías:', [''] + list(categorias_unicas))
    
    if categoria_seleccionada:
        df_categoria = df[df['Categorias'].str.contains(categoria_seleccionada, na=False)]
        productos_por_pagina = 10
        total_paginas = (len(df_categoria) + productos_por_pagina - 1) // productos_por_pagina
        pagina_actual = st.number_input("Página:", min_value=1, max_value=total_paginas, value=1)
        
        inicio = (pagina_actual - 1) * productos_por_pagina
        fin = inicio + productos_por_pagina
        productos_pagina = df_categoria.iloc[inicio:fin]

        for idx, producto in productos_pagina.iterrows():
            mostrar_producto_formato_completo(producto)

        col1, col2 = st.columns([1, 1])
        with col1:
            if pagina_actual > 1:
                st.button("Página anterior", on_click=lambda: st.session_state.update({"pagina_actual": pagina_actual - 1}))
        with col2:
            if pagina_actual < total_paginas:
                st.button("Página siguiente", on_click=lambda: st.session_state.update({"pagina_actual": pagina_actual + 1}))
