
#!/bin/bash

# Monitoriza eventos en el bus del sistema D-Bus
dbus-monitor --system "type='signal',path=/org/freedesktop/UPower" | while read x; do
    if echo "$x" | grep -q "true"; then
		if [[ $(xrandr --listmonitors | grep -c "^") -gt 1 ]]; then
        # Acción cuando la tapa se cierra
		sleep 1
		xrandr --output eDP --off
		fi
        echo "La tapa se ha cerrado"
		notify-send "monitor" "tapa cerrada"
        # /path/to/your-script-lid-closed.sh
    elif echo "$x" | grep -q "false"; then
        # Acción cuando la tapa se abre
        echo "La tapa se ha abierto"
		sleep 1
		xrandr --output eDP --mode 1920x1080 --right-of HDMI-A-0 --rotate normal
		notify-send "monitor" "tapa abierta"
        # /path/to/your-script-lid-opened.sh
    fi
done
~/.fehbg
