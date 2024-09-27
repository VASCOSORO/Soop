import streamlit as st
import pandas as pd

# Función para mostrar la información del producto con formato completo
def mostrar_producto_formato_completo(producto):
    st.subheader(producto['Nombre'])
    st.markdown(f"**Código**: {producto['Codigo']}")
    st.markdown(f"**Stock**: {producto['Stock']}")
    st.markdown(f"**Precio**: {producto['Precio']}")
    st.markdown(f"**Descripción**: {producto['Descripción'] if pd.notna(producto['Descripción']) else 'Sin datos'}")
    st.markdown(f"**Categorías**: {producto['Categorias']}")
    
    # Mostrar la imagen si existe el enlace
    if pd.notna(producto['Imagen']):
        st.image(producto['Imagen'], width=400)
    else:
        st.text("Imagen no disponible")

# Cargar archivo Excel
@st.cache
def cargar_datos():
    df = pd.read_excel('productos.xlsx')  # Asegúrate de que el archivo tenga las columnas correctas
    return df

# Cargar datos del archivo Excel
df = cargar_datos()

st.title("🐻 Super Buscador de Productos")

# Mostrar mensaje de carga exitosa
st.success(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Input para buscar productos por nombre
buscar_producto = st.selectbox("Escribí acá para buscar", [""] + df['Nombre'].tolist())

# Evitar que muestre el mismo producto dos veces y limpiar cuando no haya selección
if buscar_producto:
    producto_seleccionado = df[df['Nombre'] == buscar_producto].iloc[0]
    mostrar_producto_formato_completo(producto_seleccionado)

# Opciones de ver por categorías, ordenar por novedad, y sugerir por rubro
col1, col2, col3 = st.columns(3)
with col1:
    ver_por_categorias = st.checkbox("Ver lista por Categorías")
with col2:
    ordenar_por_novedad = st.checkbox("Ordenar por Novedad")
with col3:
    sugerir_por_rubro = st.checkbox("Sugerir por Rubro (Próximamente)")

# Si se selecciona "Ver lista por Categorías"
if ver_por_categorias:
    categorias = df['Categorias'].unique()
    categoria_seleccionada = st.selectbox("Categorías:", [""] + list(categorias))
    if categoria_seleccionada:
        productos_filtrados = df[df['Categorias'].str.contains(categoria_seleccionada)]
        for _, producto in productos_filtrados.iterrows():
            mostrar_producto_formato_completo(producto)

# Para ordenar por novedad, se asume que hay una columna de fecha en el dataset
if ordenar_por_novedad:
    df_ordenado = df.sort_values(by='Fecha Creado', ascending=False)
    for _, producto in df_ordenado.iterrows():
        mostrar_producto_formato_completo(producto)
