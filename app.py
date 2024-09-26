import streamlit as st
import pandas as pd
import os

# Cargar el archivo Excel
ruta_excel = '1083.xlsx'
df = pd.read_excel(ruta_excel)

# Título de la aplicación
st.title('Super Buscador de Productos')

# Verificar si el archivo fue cargado
if df is None:
    st.error("No se pudo cargar el archivo de Excel.")
else:
    st.success(f"Archivo cargado exitosamente.")
    st.write(f"Se cargaron {df.shape[0]} filas y {df.shape[1]} columnas del archivo de Excel.")

# Casillas de verificación
ver_por_categoria = st.checkbox("Ver lista por Categorías")
ordenar_novedad = st.checkbox("Ordenar por Novedad")
sugerir_rubro = st.checkbox("Sugerir por Rubro (Próximamente)", disabled=True)

# Obtener lista de categorías únicas
if 'Categorias' in df.columns:
    df['Categorias_split'] = df['Categorias'].apply(lambda x: [cat.strip() for cat in x.split(',')] if pd.notna(x) else [])
    categorias_unicas = sorted(set([cat for sublist in df['Categorias_split'].tolist() for cat in sublist]))

# Mostrar el dropdown de categorías si se selecciona "Ver lista por Categorías"
if ver_por_categoria:
    categoria_seleccionada = st.selectbox("Categorías:", [""] + categorias_unicas)
    
    if categoria_seleccionada:
        # Filtrar productos por la categoría seleccionada
        productos_filtrados = df[df['Categorias_split'].apply(lambda x: categoria_seleccionada in x)]
        
        # Mostrar productos paginados en formato de tarjetas
        num_productos_por_pagina = 10
        num_paginas = len(productos_filtrados) // num_productos_por_pagina + 1
        pagina_seleccionada = st.selectbox("Página:", range(1, num_paginas + 1))
        
        # Obtener los productos de la página seleccionada
        inicio = (pagina_seleccionada - 1) * num_productos_por_pagina
        fin = inicio + num_productos_por_pagina
        productos_pagina = productos_filtrados.iloc[inicio:fin]
        
        # Mostrar productos en formato de tarjeta
        for idx, producto in productos_pagina.iterrows():
            mostrar_producto_formato_completo(producto)

# Función para obtener valores de manera segura
def obtener_valor(producto, campo):
    valor = producto.get(campo, 'Sin datos')
    return 'Sin datos' if pd.isna(valor) or valor == '' else valor

# Función para mostrar productos en formato de tarjeta (como en Colab)
def mostrar_producto_formato_completo(producto):
    # Obtener valores del producto
    stock = obtener_valor(producto, 'Stock')
    precio_jugueterias_face = obtener_valor(producto, 'Precio Jugueterias face')
    descripcion = obtener_valor(producto, 'Descripción')
    categorias = obtener_valor(producto, 'Categorias')
    nombre = obtener_valor(producto, 'Nombre')
    codigo = obtener_valor(producto, 'Codigo')
    img_url = obtener_valor(producto, 'imagen')  # Asegúrate de tener las imágenes

    # Mostrar el producto en una tarjeta
    st.markdown(f"""
    <div style="border:2px solid #cccccc; padding: 10px; margin: 10px 0; border-radius: 10px; background-color: #f9f9f9;">
        <h3>{nombre}</h3>
        <p><strong>Código:</strong> {codigo}</p>
        <p><strong>Stock:</strong> {stock}</p>
        <p><strong>Precio:</strong> {precio_jugueterias_face}</p>
        <p><strong>Descripción:</strong> {descripcion}</p>
        <p><strong>Categorías:</strong> {categorias}</p>
        <img src="{img_url}" style="width:150px; height:auto; border-radius:5px;"/>
    </div>
    """, unsafe_allow_html=True)

