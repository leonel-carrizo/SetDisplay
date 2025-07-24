# 🖥️ SetDisplay

**SetDisplay** is a dynamic and lightweight monitor management tool for Linux environments. It aims to automatically detect connected displays and apply user-defined layouts using `xrandr`.

> ⚠️ This project is currently under active development. Functionality may be incomplete or subject to change.

---

## 📁 About

SetDisplay is being built to simplify multi-monitor management in Linux. The goal is to allow seamless transitions between monitor setups (e.g., docking station, laptop screen, external monitors) without manual `xrandr` adjustments.

---

## 🚧 Development Status

- Language: Python 3
- Structure:
  - `setdisplay.py`: main entry point
  - `config/`: configuration management
  - `utils/`: internal helper functions
  - `monitoring_lid.sh`: optional shell script for lid event handling

> Current features are experimental. No stable release or install process is available yet.

---

## 🛠️ Requirements (planned)

- Python 3.x
- `xrandr`
- Linux with X11

---

## 📌 Goals (in progress)

- Detect active monitors and adjust layout dynamically
- Persist display setups between sessions
- Optional background script for lid-close events

---

## 🤝 Contributing

This project is in its early stages, but contributions and suggestions are welcome!

---

## 📜 License

MIT © Leonel Carrizo
