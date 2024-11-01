import subprocess
import time
import pyautogui
import os
import shutil
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import tempfile
from datetime import datetime
from transformers import pipeline
from tkinter import Tk, filedialog

# Cargar el modelo GPT en español
generador = pipeline('text-generation', model='datificate/gpt2-small-spanish')

# Función para hablar usando Google Text-to-Speech
def hablar(texto):
    tts = gTTS(texto, lang="es")
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(f"{fp.name}.mp3")
        playsound(f"{fp.name}.mp3")

# Función para reconocer comandos de voz
def reconocer_comando():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Escuchando...")
        hablar("Escuchando...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        comando = recognizer.recognize_google(audio, language="es-ES")
        print(f"Has dicho: {comando}")
        return comando.lower()
    except sr.UnknownValueError:
        hablar("No te he entendido, por favor, repite el comando.")
        return None
    except sr.RequestError:
        hablar("Error al conectar con el servicio de reconocimiento de voz.")
        return None

# Función para actualizar productos con CSV especificado
def actualizar_productos(csv_path=None):
    hablar("Actualizando productos, por favor espera.")
    
    # Ruta al ejecutable de Edge y los argumentos para iniciar la aplicación
    command = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge_proxy.exe'
    args = [
        '--profile-directory=Default',
        '--app-id=aaiihkibclfhphlgcllldaaphlhflgoc',
        '--app-url=https://smartycart.com.ar/',
        '--app-run-on-os-login-mode=windowed',
        '--app-launch-source=19'
    ]

    # Ejecutar el comando para abrir Edge en modo aplicación
    subprocess.Popen([command] + args)
    time.sleep(5)

    # Simular teclas y clicks
    try:
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('down')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

        for _ in range(29):
            pyautogui.press('tab')
            time.sleep(0.1)

        pyautogui.press('space')
        time.sleep(1)
        pyautogui.click(x=2960, y=380)
        time.sleep(1)
        pyautogui.click(x=3115, y=308)
        time.sleep(10)

        if not csv_path:
            # Detectar el archivo CSV más reciente en la carpeta de descargas
            download_folder = r'C:\Users\virtu\Downloads'
            files = os.listdir(download_folder)
            paths = [os.path.join(download_folder, file) for file in files]
            recent_file = max(paths, key=os.path.getctime)
            print(f"Archivo más reciente encontrado: {recent_file}")
            csv_path = recent_file

        # Renombrar y mover el archivo CSV
        new_name = 'tmp_28_1728896035.csv'
        new_path = os.path.join(r'C:\Users\virtu\Repositorios\Soop', new_name)
        shutil.move(csv_path, new_path)
        print(f"Archivo CSV movido a {new_path}")

        # Git pull, commit y push al repositorio Soop
        repositorio_path = r'C:\Users\virtu\Repositorios\Soop'
        subprocess.run(['git', '-C', repositorio_path, 'pull', 'origin', 'main'])
        subprocess.run(['git', '-C', repositorio_path, 'add', '.'])
        subprocess.run(['git', '-C', repositorio_path, 'commit', '-m', f'Subida de {new_name}'])
        subprocess.run(['git', '-C', repositorio_path, 'push', 'origin', 'main'])

        # Confirmar la actualización y mostrar la hora
        hora_actualizacion = datetime.now().strftime("%H:%M:%S")
        hablar(f"Productos actualizados correctamente a las {hora_actualizacion}.")
        print(f"Productos actualizados a las {hora_actualizacion}.")

    except Exception as e:
        hablar(f"Error al actualizar productos: {e}")
        print(f"Error: {e}")

# Función para seleccionar un archivo CSV
def seleccionar_csv():
    Tk().withdraw()  # Ocultar la ventana principal
    csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if csv_path:
        hablar("Archivo seleccionado, procediendo a actualizar.")
        actualizar_productos(csv_path)
    else:
        hablar("No se seleccionó ningún archivo.")

# Bucle principal
while True:
    comando = reconocer_comando()
    if comando:
        if "actualizar productos" in comando:
            actualizar_productos()
            break  # Termina el bucle después de la actualización
        elif "subir archivo" in comando:
            seleccionar_csv()
            break
        else:
            # Generar una respuesta con el modelo GPT
            respuesta = generador(comando, max_length=50, num_return_sequences=1, do_sample=True)
            texto_respuesta = respuesta[0]['generated_text']
            print(f"Asistente: {texto_respuesta}")
            hablar(texto_respuesta)
    else:
        hablar("No te he entendido, por favor, repite el comando.")
