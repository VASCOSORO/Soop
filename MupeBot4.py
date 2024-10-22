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

# Función para actualizar productos
def actualizar_productos():
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

    # Esperar unos segundos para que la aplicación se abra correctamente
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

        # Detectar el archivo CSV más reciente
        download_folder = r'C:\Users\virtu\Downloads'
        files = os.listdir(download_folder)
        paths = [os.path.join(download_folder, file) for file in files]
        recent_file = max(paths, key=os.path.getctime)
        print(f"Archivo más reciente encontrado: {recent_file}")

        # Renombrar el archivo CSV
        new_name = 'tmp_28_1728896035.csv'
        new_path = os.path.join(download_folder, new_name)
        shutil.move(recent_file, new_path)
        print(f"Archivo renombrado a: {new_path}")

        # Mover el archivo renombrado al repositorio Soop
        repositorio_path = r'C:\Users\virtu\Repositorios\Soop'
        shutil.move(new_path, os.path.join(repositorio_path, new_name))

        # Hacer el commit y push al repositorio Soop
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

# Bucle principal
while True:
    comando = reconocer_comando()
    if comando:
        if "actualizar productos" in comando:
            actualizar_productos()
            break  # Termina el bucle después de la actualización
        else:
            # Generar una respuesta con el modelo GPT
            respuesta = generador(comando, max_length=50, num_return_sequences=1, do_sample=True)
            texto_respuesta = respuesta[0]['generated_text']
            print(f"Asistente: {texto_respuesta}")
            hablar(texto_respuesta)
    else:
        hablar("No te he entendido, por favor, repite el comando.")
