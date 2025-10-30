#!/usr/bin/env bash
# Pequeño script para arrancar / parar / ver estado de la app Streamlit
# Ubicación: ./run.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT_DIR/.venv"
APP="rubrica-streamlit/app.py"
LOG="$ROOT_DIR/streamlit_8501.log"
PID_DIR="$ROOT_DIR/.run"
PID_FILE="$PID_DIR/streamlit.pid"
PORT=8501

ensure_pid_dir() {
  mkdir -p "$PID_DIR"
}

start() {
  ensure_pid_dir
  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Streamlit parece ya estar corriendo (PID=$(cat $PID_FILE)). Usa './run.sh status' o './run.sh stop'"
    return 0
  fi

  if [ -d "$VENV" ]; then
    # shellcheck disable=SC1090
    . "$VENV/bin/activate"
  else
    echo "Aviso: no se encontró .venv en $VENV — activa el entorno manualmente si hace falta"
  fi

  nohup streamlit run "$APP" --server.port $PORT --server.address 0.0.0.0 > "$LOG" 2>&1 &
  NEWPID=$!
  echo $NEWPID > "$PID_FILE"
  echo "Arrancado Streamlit (PID=$NEWPID). Logs en $LOG"
}

stop() {
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID" && echo "Terminado PID $PID" || echo "No se pudo terminar PID $PID"
    else
      echo "PID $PID no está activo. Eliminando archivo pid." 
    fi
    rm -f "$PID_FILE"
  else
    echo "No hay PID guardado. Intentando matar procesos de streamlit por patrón..."
    pkill -f "streamlit run" || true
  fi
}

status() {
  if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
      echo "Streamlit corriendo (PID=$PID)"
    else
      echo "PID almacenado ($PID) no está activo"
    fi
  else
    echo "No existe PID guardado. Comprueba puertos o logs."
  fi
  echo "Puertos (8501/8502):"
  ss -ltnp 2>/dev/null | grep -E ':8501|:8502' || true
}

logs() {
  tail -n 200 "$LOG" || echo "No hay log disponible en $LOG"
}

case ${1:-} in
  start)
    start
    ;;
  stop)
    stop
    ;;
  status)
    status
    ;;
  logs)
    logs
    ;;
  restart)
    stop || true
    start
    ;;
  *)
    echo "Uso: $0 {start|stop|restart|status|logs}"
    exit 1
    ;;
esac
