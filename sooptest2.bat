@echo off
REM Inicializar Conda
CALL "C:\Users\virtu\miniforge3\Scripts\activate.bat"

REM Activar el entorno 'soopenv'
CALL conda activate soopenv

REM Cambiar al directorio de tu aplicación
"C:\Users\virtu\Repositorios\Soop"

REM Ejecutar la aplicación Streamlit
streamlit run app.py

REM Mantener la ventana abierta
PAUSE
