import json
import os
import re
import subprocess
from collections import OrderedDict

# Define XDG configuration directory
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, "SetDisplay")
DEFAULT_PROFILE_NAME = "default"

def ensure_config_directory():
    """Ensures that the configuration directory exists in XDG_CONFIG_HOME."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

def get_profile_path(profile_name):
    """Returns the full path of the configuration file for a given profile."""
    return os.path.join(CONFIG_DIR, f"monitors_config_{profile_name}.json")

def save_monitor_configuration(monitors, profile_name=DEFAULT_PROFILE_NAME):
    """Save monitor settings to a specific profile file in the XDG directory."""
    ensure_config_directory()
    profile_path = get_profile_path(profile_name)
    with open(profile_path, 'w') as json_file:
        json.dump(monitors, json_file, indent=4)
    print(f"Configuration saved to {profile_path}")

def get_monitor_properties():
    """Gets the properties of monitors using xrandr and returns an organized dictionary."""
    try:
        # Run `xrandr --prop` and capture the output
        result = subprocess.run(['xrandr', '--prop'], capture_output=True, text=True, check=True)
        output = result.stdout

        # Dictionary to store the details of each monitor
        monitors = {}

        # Regular expression variables to extract the values
        edid_line_pattern = re.compile(r'\t\t([0-9a-f]+)')
        primary_pattern = re.compile(r'\s+connected primary')
        mode_pattern = re.compile(r'(\d{3,4}x\d{3,4})')
        position_pattern = re.compile(r'\+(\d+)\+(\d+)')
        refresh_pattern = re.compile(r'(\d+\.\d+)\*')
        colorspace_pattern = re.compile(r'Colorspace:\s(\w+)')
        bpc_pattern = re.compile(r'max bpc:\s(\d+)')
        non_desktop_pattern = re.compile(r'non-desktop:\s(\d)')
        scaling_pattern = re.compile(r'scaling mode:\s(\w+)')
        tearfree_pattern = re.compile(r'TearFree:\s(\w+)')

        # Process the output line by line
        current_monitor = {}
        edid_value = ""
        for line in output.splitlines():
            # Detect the name of the monitor (e.g. eDP, HDMI-A-0) and whether it is connected or not
            if " connected" in line or " disconnected" in line:
                # If we are in a new monitor and there is a current one in progress, add it to the dictionary
                if current_monitor:
                    if not current_monitor['connected']:
                        monitors[current_monitor["name"]] = OrderedDict({
                            "connected": False
                        })
                    else:
                        current_monitor['edid'] = edid_value
                        # Arrange the keys in the desired order
                        monitors[current_monitor["name"]] = OrderedDict({
                            "connected": current_monitor['connected'],
                            "active": current_monitor.get('active', False),
                            "primary": current_monitor.get('primary', False),
                            "mode": current_monitor.get('mode', "Unknown"),
                            "position": current_monitor.get('position', "Unknown"),
                            "tear_free": current_monitor.get('tear_free', "auto"),
                            "colorspace": current_monitor.get('colorspace', "Default"),
                            "bpc": current_monitor.get('bpc', 8),
                            "scaling_mode": current_monitor.get('scaling_mode', "None"),
                            "non_desktop": current_monitor.get('non_desktop', False),
                            "refresh_rate": current_monitor.get('refresh_rate', 60.0),
                            "edid": edid_value
                        })

                # Reset for the new monitor
                current_monitor = {"name": line.split()[0], 'connected': " connected" in line}
                edid_value = ""  # Reset the EDID

                # Check if the monitor is connected to extract properties
                if current_monitor['connected']:
                    # Check if it is the primary monitor
                    current_monitor['primary'] = bool(primary_pattern.search(line))

                    # Extract the resolution and position of the connection line
                    mode_match = mode_pattern.search(line)
                    position_match = position_pattern.search(line)
                    current_monitor['mode'] = mode_match.group(1) if mode_match else "Unknown"
                    current_monitor['position'] = f"+{position_match.group(1)}+{position_match.group(2)}" if position_match else "Unknown"
                    current_monitor['active'] = current_monitor['mode'] != "Unknown" and current_monitor['mode'] != "0x0"

            # Extract the EDID (capture all EDID lines and concatenate them)
            edid_line_match = edid_line_pattern.search(line)
            if edid_line_match:
                edid_value += edid_line_match.group(1)

            # Extract properties only if the monitor is connected
            if current_monitor.get('connected', False):
                # Extract el Refresh rate
                refresh_match = refresh_pattern.search(line)
                if refresh_match:
                    current_monitor['refresh_rate'] = float(refresh_match.group(1))

                # Extract el Colorspace
                colorspace_match = colorspace_pattern.search(line)
                if colorspace_match:
                    current_monitor['colorspace'] = colorspace_match.group(1)

                # Extract Bits per channel (BPC)
                bpc_match = bpc_pattern.search(line)
                if bpc_match:
                    current_monitor['bpc'] = int(bpc_match.group(1))

                # Extract non-desktop
                non_desktop_match = non_desktop_pattern.search(line)
                if non_desktop_match:
                    current_monitor['non_desktop'] = bool(int(non_desktop_match.group(1)))

                # Extract Scaling mode
                scaling_match = scaling_pattern.search(line)
                if scaling_match:
                    current_monitor['scaling_mode'] = scaling_match.group(1)

                # Extract Tear Free
                tearfree_match = tearfree_pattern.search(line)
                if tearfree_match:
                    current_monitor['tear_free'] = tearfree_match.group(1)

        # Add the last monitor in progress
        if current_monitor:
            if not current_monitor['connected']:
                monitors[current_monitor["name"]] = OrderedDict({
                    "connected": False
                })
            else:
                current_monitor['edid'] = edid_value
                monitors[current_monitor["name"]] = OrderedDict({
                    "connected": current_monitor['connected'],
                    "active": current_monitor.get('active', False),
                    "primary": current_monitor.get('primary', False),
                    "mode": current_monitor.get('mode', "Unknown"),
                    "position": current_monitor.get('position', "Unknown"),
                    "tear_free": current_monitor.get('tear_free', "auto"),
                    "colorspace": current_monitor.get('colorspace', "Default"),
                    "bpc": current_monitor.get('bpc', 8),
                    "scaling_mode": current_monitor.get('scaling_mode', "None"),
                    "non_desktop": current_monitor.get('non_desktop', False),
                    "refresh_rate": current_monitor.get('refresh_rate', 60.0),
                    "edid": edid_value
                })

        return monitors

    except subprocess.CalledProcessError as e:
        print("Error executing xrandr:", e)
        return {}

# Get and save the monitor configuration to the XDG directory
monitor_config = get_monitor_properties()
save_monitor_configuration(monitor_config)

