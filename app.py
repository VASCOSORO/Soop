import os
import streamlit as st
import pandas as pd

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
        st.write("Archivo cargado exitosamente.")  # Mensaje de depuración
        return df
    except Exception as e:
        st.write(f"Error al cargar el archivo: {e}")
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

# Variable global para almacenar el producto seleccionado
producto_seleccionado = None

# Función para obtener valores del producto de manera segura
def obtener_valor(producto, campo):
    valor = producto.get(campo, 'Sin datos')
    if pd.isna(valor) or valor == '':
        return 'Sin datos'
    return valor

# Función para mostrar el producto seleccionado con el estilo preferido
def mostrar_producto_formato_completo(producto):
    global producto_seleccionado
    producto_seleccionado = producto  # Guardar el producto seleccionado para acciones posteriores

    # Obtener datos del producto
    stock = obtener_valor(producto, 'Stock')
    try:
        stock_valor = float(stock)
        stock_color = "red" if stock_valor < 5 else "green"
    except ValueError:
        stock_color = "black"

    # Obtener el precio y asegurarse de que sea numérico
    precio_jugueterias_face = obtener_valor(producto, 'Precio Jugueterias face')
    try:
        precio_jugueterias_face = float(precio_jugueterias_face)
    except ValueError:
        precio_jugueterias_face = 0

    forzar_multiplos = obtener_valor(producto, 'forzar multiplos')
    try:
        forzar_multiplos = int(forzar_multiplos)
        if forzar_multiplos > 0:
            venta_forzada_texto = f"Venta Forzada: {forzar_multiplos}"
            venta_forzada_color = "red"
            precio_caja_venta = forzar_multiplos * precio_jugueterias_face
            mostrar_precio_caja = True
        else:
            venta_forzada_texto = "Venta Forzada: NO"
            venta_forzada_color = "green"
            precio_caja_venta = precio_jugueterias_face
            mostrar_precio_caja = False
    except ValueError:
        venta_forzada_texto = "Venta Forzada: NO"
        venta_forzada_color = "green"
        precio_caja_venta = precio_jugueterias_face
        mostrar_precio_caja = False

    precio_mayorista = obtener_valor(producto, 'Precio')
    unidades_por_bulto = obtener_valor(producto, 'unidad por bulto')
    descripcion = obtener_valor(producto, 'Descripción') if 'Descripción' in producto else obtener_valor(producto, 'Descripcion')
    categorias = obtener_valor(producto, 'Categorias')
    pasillo = obtener_valor(producto, 'Pasillo')
    estante = obtener_valor(producto, 'Estante')
    proveedor = obtener_valor(producto, 'Proveedor')
    codigo = obtener_valor(producto, 'Codigo')
    nombre = obtener_valor(producto, 'Nombre')

    # Mostrar detalles del producto
    st.write(f"Producto seleccionado: {nombre}, Código: {codigo}")
    st.write(f"Stock: {stock}, Precio: {precio_jugueterias_face}")

# Cuadro de búsqueda centrado
entrada_busqueda = st.text_input("🔍 Ingresá el nombre del producto")

# Filtrar los productos por nombre cuando se ingresa un texto en la búsqueda
if entrada_busqueda:
    coincidencias = df[df['Nombre'].str.contains(entrada_busqueda, case=False, na=False)]
    if not coincidencias.empty:
        st.write(f"Se encontraron {coincidencias.shape[0]} productos.")
        # Mostrar la información del primer producto como ejemplo
        primer_producto = coincidencias.iloc[0].to_dict()
        mostrar_producto_formato_completo(primer_producto)
    else:
        st.write("No se encontraron productos con ese nombre.")
else:
    st.write("Esperando entrada de búsqueda...")
