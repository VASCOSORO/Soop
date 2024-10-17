import subprocess
import time
import pyautogui
import os
import shutil

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
    # Enviar Tabuladores y Enter para seleccionar productos y descargar CSV
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

    print(f"Archivo {new_name} subido a GitHub en Soop.")

except Exception as e:
    print(f"Error: {e}")
