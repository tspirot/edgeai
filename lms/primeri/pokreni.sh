#!/bin/bash
# ==============================================================================
#            POKRETAČ PROJEKATA — RASPBERRY PI 5 (primeri)
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Python iz okruzenja pored skripte (primeri/env), a ako ga nema - sistemski python3
PY="$DIR/env/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

# Provera ekrana za grafički prozor
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    export DISPLAY="${DISPLAY:-:0}"
    export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
    exec "$PY" pokretac.py "$@"
else
    # Ako se pokreće preko SSH bez ekrana, pokreni interaktivni meni u terminalu
    exec "$PY" pokretac.py --cli "$@"
fi
