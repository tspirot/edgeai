#!/bin/bash
# ==============================================================================
#            POKRETAČ PROJEKATA — RASPBERRY PI 5 (primeri)
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Provera ekrana za grafički prozor
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export DISPLAY="${DISPLAY:-:0}"
    export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
    exec /home/pi/primeri/env/bin/python pokretac.py "$@"
else
    # Ako se pokreće preko SSH bez ekrana, pokreni interaktivni meni u terminalu
    exec /home/pi/primeri/env/bin/python pokretac.py --cli "$@"
fi
