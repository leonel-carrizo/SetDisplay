import os

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, "SetDisplay")

def ensure_config_directory():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def get_profile_path(profile_name):
    ensure_config_directory()
    return os.path.join(CONFIG_DIR, f"monitors_config_{profile_name}.json")

