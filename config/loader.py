import json
import subprocess
from utils import paths

def load_monitor_configuration(profile_name="default"):
    profile_path = paths.get_profile_path(profile_name)
    try:
        with open(profile_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"No configuration file found for profile '{profile_name}' at {profile_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON in the configuration file: {profile_path}")
        return {}

def apply_monitor_configuration(config):
    for monitor_name, settings in config.items():
        if settings.get("connected", False):
            xrandr_command = ["xrandr", "--output", monitor_name]
            if settings.get("active", False):
                mode = settings.get("mode", "1920x1080")
                position = settings.get("position", "0x0")
                rotation = settings.get("rotation", "normal")
                xrandr_command.extend(["--mode", mode, "--pos", position, "--rotate", rotation])
                if settings.get("primary", False):
                    xrandr_command.append("--primary")
            else:
                xrandr_command.append("--off")

            print(f"Applying configuration for {monitor_name}: {' '.join(xrandr_command)}")
            try:
                subprocess.run(xrandr_command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to apply configuration for {monitor_name}: {e}")

