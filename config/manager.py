import json
import re
import subprocess
from collections import OrderedDict
from utils import paths

def save_monitor_configuration(monitors, profile_name="default"):
    """Saves monitor configuration to a specific profile file in the XDG config directory."""
    profile_path = paths.get_profile_path(profile_name)
    with open(profile_path, 'w') as json_file:
        json.dump(monitors, json_file, indent=4)
    print(f"Configuration saved to {profile_path}")

def get_monitor_properties():
    """Gets monitor properties using xrandr and returns a structured dictionary."""
    try:
        # Execute `xrandr --prop` and capture the output
        result = subprocess.run(['xrandr', '--prop'], capture_output=True, text=True, check=True)
        output = result.stdout
        monitors = {}

        # Regex patterns for extracting values
        edid_line_pattern = re.compile(r'\t\t([0-9a-f]+)')
        primary_pattern = re.compile(r'\s+connected primary')
        mode_pattern = re.compile(r'(\d{3,4}x\d{3,4})')
        position_pattern = re.compile(r'\+(\d+)\+(\d+)')
        rotation_pattern = re.compile(r'\((normal|left|inverted|right)\s[xy]\saxis\s[xy]\saxis\)')
        refresh_pattern = re.compile(r'(\d+\.\d+)\*')
        colorspace_pattern = re.compile(r'Colorspace:\s(\w+)')
        bpc_pattern = re.compile(r'max bpc:\s(\d+)')
        non_desktop_pattern = re.compile(r'non-desktop:\s(\d)')
        scaling_pattern = re.compile(r'scaling mode:\s(\w+)')
        tearfree_pattern = re.compile(r'TearFree:\s(\w+)')

        current_monitor = {}
        edid_value = ""
        for line in output.splitlines():
            # Detect monitor name (e.g., eDP, HDMI-A-0) and connection status
            if " connected" in line or " disconnected" in line:
                # If a new monitor is found and the current monitor data exists, add it to the dictionary
                if current_monitor:
                    if not current_monitor['connected']:
                        monitors[current_monitor["name"]] = OrderedDict({
                            "connected": False
                        })
                    else:
                        current_monitor['edid'] = edid_value
                        # Format the position as "x y" without the "+" symbols
                        position = current_monitor.get('position', "+0+0")
                        x, y = position.strip("+").split("+")
                        current_monitor['position'] = f"{x}x{y}"

                        # Organize keys in the desired order
                        monitors[current_monitor["name"]] = OrderedDict({
                            "connected": current_monitor['connected'],
                            "active": current_monitor.get('active', False),
                            "primary": current_monitor.get('primary', False),
                            "mode": current_monitor.get('mode', "Unknown"),
                            "position": current_monitor['position'],
                            "rotation": current_monitor.get('rotation', "normal"),
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
                edid_value = ""  # Reset EDID

                # If the monitor is connected, extract properties
                if current_monitor['connected']:
                    # Check if it's the primary monitor
                    current_monitor['primary'] = bool(primary_pattern.search(line))

                    # Extract resolution, position, and rotation from the connection line
                    mode_match = mode_pattern.search(line)
                    position_match = position_pattern.search(line)
                    rotation_match = rotation_pattern.search(line)
                    current_monitor['mode'] = mode_match.group(1) if mode_match else "Unknown"
                    current_monitor['position'] = f"+{position_match.group(1)}+{position_match.group(2)}" if position_match else "+0+0"
                    current_monitor['rotation'] = rotation_match.group(1) if rotation_match else "normal"
                    current_monitor['active'] = current_monitor['mode'] != "Unknown" and current_monitor['mode'] != "0x0"

            # Extract EDID (concatenate all lines of EDID)
            edid_line_match = edid_line_pattern.search(line)
            if edid_line_match:
                edid_value += edid_line_match.group(1)

            # Extract additional properties if the monitor is connected
            if current_monitor.get('connected', False):
                refresh_match = refresh_pattern.search(line)
                if refresh_match:
                    current_monitor['refresh_rate'] = float(refresh_match.group(1))

                colorspace_match = colorspace_pattern.search(line)
                if colorspace_match:
                    current_monitor['colorspace'] = colorspace_match.group(1)

                bpc_match = bpc_pattern.search(line)
                if bpc_match:
                    current_monitor['bpc'] = int(bpc_match.group(1))

                non_desktop_match = non_desktop_pattern.search(line)
                if non_desktop_match:
                    current_monitor['non_desktop'] = bool(int(non_desktop_match.group(1)))

                scaling_match = scaling_pattern.search(line)
                if scaling_match:
                    current_monitor['scaling_mode'] = scaling_match.group(1)

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
                # Format the position correctly
                position = current_monitor.get('position', "+0+0")
                x, y = position.strip("+").split("+")
                current_monitor['position'] = f"{x}x{y}"

                monitors[current_monitor["name"]] = OrderedDict({
                    "connected": current_monitor['connected'],
                    "active": current_monitor.get('active', False),
                    "primary": current_monitor.get('primary', False),
                    "mode": current_monitor.get('mode', "Unknown"),
                    "position": current_monitor['position'],
                    "rotation": current_monitor.get('rotation', "normal"),
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

