# Importar las bibliotecas necesarias
import streamlit as st
import pandas as pd
import os

# Título del buscador
st.title('Super Buscador de Productos')

# Ruta del archivo de Excel
ruta_excel = '1083_productos_al_24_de_sep.xlsx'  # Cambiar por la ruta donde tengas el Excel

# Verificar si el archivo Excel existe
if not os.path.exists(ruta_excel):
    st.error(f"Archivo no encontrado en la ruta: {ruta_excel}")
    st.stop()

# Cargar el DataFrame desde el archivo de Excel
try:
    df = pd.read_excel(ruta_excel)
    st.success("DataFrame cargado exitosamente.")
except Exception as e:
    st.error(f"Error al cargar el archivo de Excel: {e}")
    st.stop()

# Función para obtener valores de manera segura
def obtener_valor(producto, campo):
    valor = producto.get(campo, 'Sin datos')
    if pd.isna(valor) or valor == '':
        return 'Sin datos'
    return valor

# Función para mostrar la información de un producto
def mostrar_producto(producto):
    st.subheader(f"Producto: {producto['Nombre']}")
    st.write(f"Código: {producto['Codigo']}")
    st.write(f"Stock: {producto['Stock']}")
    st.write(f"Precio Jugueterías: ${producto['Precio Jugueterias face']}")
    st.write(f"Descripción: {producto['Descripción']}")
    # Mostrar imagen si está disponible
    if not pd.isna(producto['imagen']):
        st.image(producto['imagen'], caption=producto['Nombre'], use_column_width=True)
    else:
        st.write("Imagen no disponible.")

# Búsqueda por nombre del producto
nombre_producto = st.text_input('Buscar por nombre de producto')

if nombre_producto:
    # Filtrar DataFrame según el nombre ingresado
    resultados = df[df['Nombre'].str.contains(nombre_producto, case=False, na=False)]
    
    if not resultados.empty:
        for idx, producto in resultados.iterrows():
            mostrar_producto(producto)
    else:
        st.write("No se encontraron productos con ese nombre.")

# Mostrar lista de productos más recientes
if st.checkbox('Mostrar 100 productos más recientes'):
    if 'Fecha Creado' in df.columns:
        df['Fecha Creado'] = pd.to_datetime(df['Fecha Creado'], errors='coerce')
        productos_recientes = df.sort_values(by='Fecha Creado', ascending=False).head(100)
        for idx, producto in productos_recientes.iterrows():
            mostrar_producto(producto)
    else:
        st.write("La columna 'Fecha Creado' no existe en el DataFrame.")
