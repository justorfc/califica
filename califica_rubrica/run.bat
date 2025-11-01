@echo off
REM Activar venv y arrancar Streamlit (Windows)
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
) else (
  echo No se encontró .venv. Activa el entorno manualmente o crea uno con: python -m venv .venv
)
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
