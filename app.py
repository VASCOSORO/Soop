import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# Cargar el archivo Excel
@st.cache_data
def load_data():
    df = pd.read_excel('1083.xlsx')  # Asegúrate de que el archivo Excel esté en el mismo directorio
    return df

# Función para cargar la imagen desde una URL
def cargar_imagen(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

# Mostrar producto en formato completo (con imagen)
def mostrar_producto_completo(producto):
    st.markdown(f"### {producto['Nombre']}")
    st.write(f"Código: {producto['Codigo']}")
    st.write(f"Stock: {producto['Stock']}")
    st.write(f"Precio: {producto['Precio']}")
    st.write(f"Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}")
    st.write(f"Categorías: {producto['Categorias']}")

    imagen_url = producto.get('imagen', '')
    if imagen_url:
        imagen = cargar_imagen(imagen_url)
        if imagen:
            st.image(imagen, use_column_width=True)
        else:
            st.write("Imagen no disponible.")
    
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
        st.write(f"### {producto['Nombre']}")
        st.write(f"Código: {producto['Codigo']}")
        st.write(f"Stock: {producto['Stock']}")
        st.write(f"Precio: {producto['Precio']}")
        st.write(f"Descripción: {producto['Descripcion'] if not pd.isna(producto['Descripcion']) else 'Sin datos'}")
        st.write(f"Categorías: {producto['Categorias']}")
        
        imagen_url = producto.get('imagen', '')
        if imagen_url:
            imagen = cargar_imagen(imagen_url)
            if imagen:
                st.image(imagen, width=100)  # Mostrar imagen en pequeño
            else:
                st.write("Imagen no disponible.")
        st.write("---")
    
    total_paginas = (len(df) + productos_por_pagina - 1) // productos_por_pagina
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if pagina > 1:
            st.button('Página anterior', on_click=lambda: st.session_state.update({'pagina': pagina - 1}))
    with col2:
        st.write(f"Página {pagina} de {total_paginas}")
    with col3:
        if pagina < total_paginas:
            st.button('Página siguiente', on_click=lambda: st.session_state.update({'pagina': pagina + 1}))

# Cargar datos
df = load_data()

# Título
st.markdown("# 🐻 Super Buscador de Productos")

# Mostrar número de filas y columnas cargadas
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Campo de búsqueda con el comportamiento que describiste
busqueda = st.selectbox("Escribí acá para buscar", [''] + list(df['Nombre']), index=0)

# Verificar si el usuario ha escrito algo y filtrar productos
if busqueda:
    productos_filtrados = df[df['Nombre'].str.contains(busqueda, case=False)]
    if not productos_filtrados.empty:
        seleccion = st.selectbox("Seleccionar:", productos_filtrados.apply(lambda row: f"{row['Nombre']} (Código: {row['Codigo']})", axis=1))

        # Mostrar producto seleccionado
        producto_seleccionado = productos_filtrados[productos_filtrados.apply(lambda row: f"{row['Nombre']} (Código: {row['Codigo']})", axis=1) == seleccion].iloc[0]
        mostrar_producto_completo(producto_seleccionado)

# Espacio entre el buscador y las opciones
st.write("\n")  # Esto agrega un espacio en blanco

# Alinear correctamente las opciones
col_opciones = st.columns(3)
with col_opciones[0]:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col_opciones[1]:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
with col_opciones[2]:
    sugerir_por_rubro = st.checkbox("Sugerir por Rubro (Próximamente)")

# Ver lista por categorías
if ver_por_categorias:
    # Asegurarse de mostrar categorías individuales
    categorias_unicas = sorted(set(df['Categorias'].str.split(',').explode()))
    categoria = st.selectbox('Categorías:', [''] + categorias_unicas)
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
