
import os
import subprocess
import re
from configparser import ConfigParser

# Obtener el directorio de inicio del usuario desde la variable de entorno HOME
config_dir = os.path.join(os.environ["HOME"], ".config/monitors")
config_file = os.path.join(config_dir, "monitor_layout.conf")

# Crear el directorio y archivo de configuración si no existen
os.makedirs(config_dir, exist_ok=True)
if not os.path.exists(config_file):
    with open(config_file, "w") as f:
        f.write("# Archivo de configuración de monitores\n")

# Función para ejecutar xrandr y obtener su salida
def get_xrandr_output():
    try:
        output = subprocess.check_output(["xrandr", "--verbose"], encoding="utf-8")
        return output
    except subprocess.CalledProcessError:
        print("Error al ejecutar xrandr.")
        return ""

# Función para parsear la salida de xrandr y guardar en archivo de configuración
def parse_and_save_xrandr_output(output):
    # Configurar el archivo de configuración
    config = ConfigParser()
    monitor = None

    # Variable para acumular EDID en varias líneas
    is_collecting_edid = False
    edid = ""

    for line in output.splitlines():
        # Detectar el nombre del monitor y si es primario
        match_monitor = re.match(r"^(\S+) connected (primary)? (\d+x\d+\+\d+\+\d+)", line)
        if match_monitor:
            # Si estamos procesando un monitor nuevo, guarda el anterior (si existe)
            if monitor and edid:
                config[monitor]["edid"] = edid
                edid = ""

            monitor = match_monitor.group(1)
            config[monitor] = {}
            config[monitor]["primary"] = "yes" if match_monitor.group(2) else "no"
            config[monitor]["resolution_position"] = match_monitor.group(3)

        # Detectar brillo
        match_brightness = re.match(r"^\s*Brightness:\s*(\d+\.\d+)", line)
        if match_brightness and monitor:
            config[monitor]["brightness"] = match_brightness.group(1)

        # Detectar inicio del bloque EDID
        if "EDID:" in line and monitor:
            is_collecting_edid = True
            edid = ""
            continue

        # Acumular EDID si estamos en el bloque
        if is_collecting_edid:
            # Rompe el bloque EDID al encontrar una línea que no empieza con espacio/tabulación
            if not line.startswith(" "):
                is_collecting_edid = False
                config[monitor]["edid"] = edid
            else:
                edid += line.strip()

    # Guardar el último EDID si quedó sin cerrar
    if monitor and edid:
        config[monitor]["edid"] = edid

    # Guardar la configuración en un archivo .ini
    with open(config_file, "w") as configfile:
        config.write(configfile)

# Obtener la salida de xrandr
output = get_xrandr_output()
if output:
    parse_and_save_xrandr_output(output)
    print(f"Configuración de monitores guardada en {config_file}")
else:
    print("No se pudo obtener la configuración de xrandr.")
