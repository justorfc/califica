# Guía: instalar, preparar portable y (opcional) crear .exe con auto-py-to-exe

Esta guía está pensada para entornos con internet inestable (p.ej. laboratorios o redes universitarias). Detalla paso a paso cómo clonar este repositorio en un PC, dejarlo en una estructura simple llamada `califica_rubrica`, crear un entorno virtual local con todas las dependencias (offline cuando sea necesario) y las instrucciones para generar un ejecutable con `auto-py-to-exe` (Windows). También explico alternativas recomendadas cuando el empaquetado en `.exe` resulta frágil.

Resumen de la estructura final deseada

califica_rubrica/
- .venv/              # entorno virtual (opcional, .venv dentro de la carpeta)
- requirements.txt
- README.md
- app.py              # script principal (copiado desde rubrica-streamlit/app.py)
- db.py               # copia de rubrica-streamlit/db.py
- utils.py            # si aplica
- data/               # datos, CSV y DB (rubrica.db)
- otros módulos .py   # si son necesarios


Índice
1. Requisitos previos
2. Clonar el repositorio (pasos)
3. Preparar la estructura `califica_rubrica` y copiar archivos relevantes
4. Crear entorno virtual y instalar dependencias (online)
5. Preparar instalación offline (descarga de wheels) — para redes inestables
6. Ejecutar y probar la app localmente (Streamlit)
7. Crear ejecutable con auto-py-to-exe (Windows) — advertencias y pasos
8. Alternativa recomendada para despliegue offline
9. Notas finales y problemas comunes


## 1) Requisitos previos
- Python 3.10 o 3.11 instalado en el PC (asegúrate que `python3` o `python` apunta a la versión adecuada).
- Git instalado (`git` en PATH).
- Espacio en disco suficiente (mínimo 200 MB; más si incluyes datos o venv).
- En Windows: para crear un `.exe` necesitarás ejecutar `auto-py-to-exe` en Windows (donde se genera el binario), y tener Visual C++ Build Tools instalados si PyInstaller lo requiere.

Recomendación: realiza la creación del ejecutable en la misma plataforma de destino (Windows → compilar en Windows). Crear .exe en Linux/WSL no produce .exe nativos.


## 2) Clonar el repositorio (pasos)
Abre un terminal y elige la carpeta donde clonarás el repo. Reemplaza la URL por la del repo si es distinto.

```bash
# carpeta de trabajo
cd ~/proyectos

# clonar
git clone https://github.com/justorfc/rubrica-streamlit.git
cd rubrica-streamlit
```

Si la red falla mientras clonas, usa `--depth 1` para clonar sólo la última snapshot:

```bash
git clone --depth 1 https://github.com/justorfc/rubrica-streamlit.git
```


## 3) Preparar la estructura `califica_rubrica`
En tu PC quieres una estructura simple. Vamos a copiar los archivos esenciales a una nueva carpeta `califica_rubrica`.

```bash
# desde la raíz del repo clonado
cd /ruta/al/repo/rubrica-streamlit
# crear carpeta destino
mkdir -p ~/califica_rubrica
cd ~/califica_rubrica

# copiar archivos esenciales (ajusta si tu repo está en otra ruta)
cp /ruta/al/repo/rubrica-streamlit/rubrica-streamlit/app.py ./app.py
cp /ruta/al/repo/rubrica-streamlit/rubrica-streamlit/db.py ./db.py
cp /ruta/al/repo/rubrica-streamlit/rubrica-streamlit/utils.py ./utils.py || true
mkdir -p data
cp /ruta/al/repo/rubrica-streamlit/rubrica-streamlit/data/* data/ 2>/dev/null || true
cp /ruta/al/repo/rubrica-streamlit/requirements.txt ./requirements.txt
cp /ruta/al/repo/rubrica-streamlit/README.md ./README.md

# ahora entra a la carpeta destino
cd ~/califica_rubrica
```

Ajusta rutas y nombres si hiciste cambios locales. Si hay módulos adicionales (.py) necesarios, cópialos también.


## 4) Crear entorno virtual e instalar dependencias (online)
Si tienes conexión, lo más sencillo:

```bash
# en Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

En Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # o Activate.bat en cmd
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Verifica que `streamlit` y `pandas` estén instalados:

```bash
python -c "import streamlit, pandas; print(streamlit.__version__, pandas.__version__)"
```

Si la instalación falla por la conexión, sigue el paso 5 (offline).


## 5) Preparar instalación offline (descargar ruedas/wheels)
Si vas a mover el proyecto a un PC con internet intermitente, prepara una carpeta con las ruedas (.whl) en un equipo con buena conexión y llévala al PC destino (USB, NAS, etc.).

En una máquina con buena conexión:

```bash
mkdir wheelhouse
pip download -r requirements.txt -d wheelhouse
# esto descargará wheel/tar.gz de todas las dependencias a wheelhouse/
# comprueba que tienes streamlit, pandas, numpy, etc.
ls wheelhouse
```

Copia `wheelhouse/` al PC objetivo o al mismo `califica_rubrica` en `wheelhouse/`.

Instalación offline en el PC destino (dentro del .venv):

```bash
# activar .venv
source .venv/bin/activate   # o en Windows .\.venv\Scripts\Activate.ps1
# instalar desde wheelhouse
pip install --no-index --find-links=wheelhouse -r requirements.txt
```

Consejos:
- Si algún paquete no tiene rueda precompilada para tu plataforma (p.ej. paquetes que requieren compilación C), tendrás que compilarlo en el PC destino (necesitas build tools) o descargar la rueda adecuada.
- Para `streamlit` y paquetes de datos, normalmente hay wheels disponibles.


## 6) Ejecutar y probar la app localmente
Con el venv activado, prueba arrancar Streamlit:

```bash
# dentro de califica_rubrica y con .venv activado
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Si quieres probar en un puerto distinto o con binding a localhost:

```bash
streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```

Comprueba en el navegador la URL: http://localhost:8501

Si todo carga, prueba la exportación y generar backups desde la UI.


## 7) Crear un ejecutable con auto-py-to-exe (Windows) — advertencias
IMPORTANTE: Streamlit no está pensado originalmente para distribuirse como un único `.exe`. Streamlit arranca un servidor web y tiene recursos dinámicos. Empaquetarlo con PyInstaller / auto-py-to-exe puede funcionar parcialmente pero a menudo requiere ajustes finos (hidden imports, incluir paquetes, lidiar con recursos y websockets). Por eso:

- Recomendación: si quieres una "aplicación portable" para PC de aula con internet muy inestable, la opción más robusta es proporcionar una carpeta `califica_rubrica` con `.venv` preinstalado y un script `run.bat` (Windows) o `run.sh` (Linux) que active el entorno y arranque `streamlit run app.py`.

Si aun así quieres intentar el `.exe`, sigue estas instrucciones (sigue la sección de fallos comunes abajo):

### 7.1 Preparar el entorno Windows
- Traslada `califica_rubrica` al PC Windows donde construirás el .exe.
- Instala Python 3.10/3.11 en Windows (misma versión que usarás para ejecutar).
- Crea y activa un entorno virtual en Windows y pip install -r requirements.txt.
- Instala `auto-py-to-exe`:

```powershell
pip install auto-py-to-exe
# lanza la GUI
auto-py-to-exe
```

### 7.2 Configuración recomendada en la GUI de auto-py-to-exe
- Script location: apunta a `app.py` (ruta completa o relativa dentro de `califica_rubrica`).
- Onefile vs Onedir: recomiendo `onedir` (carpeta) para facilitar inclusión de datos y reducir problemas. `onefile` produce un solo .exe que extrae a temp en tiempo de ejecución; puede ser menos estable.
- Console Window: `Hidden` (si no quieres la consola), o `Console` para ver logs.
- Additional Files / Add Data:
  - Añade la carpeta `data` -> desde `califica_rubrica/data` a `data` (en Windows usar el separador `;`):
    - `data;data`
  - Si hay `rubrica.db` en la raíz, añádelo: `data/rubrica.db;.`  (origen;destino)
- Advanced:
  - En `Additional PyInstaller Options` añade flags que necesites, por ejemplo:
    --collect-all streamlit --collect-submodules streamlit
  - A veces es necesario añadir `--hidden-import` para submódulos dinámicos: p.e. `--hidden-import=streamlit.web.server.server` u otros (depende de la versión).

- Output Directory: elige una carpeta, p.ej. `dist/`.
- Click `Convert .py to .exe`.

### 7.3 Comando alternativo (PyInstaller) — ejemplo
Auto-py-to-exe usa PyInstaller por debajo; el comando equivalente puede ser:

```txt
pyinstaller --onedir --noconsole --add-data "data;data" --add-data "data/rubrica.db;." --hidden-import=streamlit --collect-submodules streamlit app.py
```

(En Linux/macOS cambia `;` por `:` en `--add-data`.)


### 7.4 Ejecución del binario generado
- Si generaste `onedir`, ve a `dist/app/` y ejecuta `app.exe`. Se debe abrir (si todo bien) y arrancar el servicio web (puerto local). Después abre `http://localhost:8501`.


### 7.5 Problemas comunes y recomendaciones
- Mucho menos frágil: distribuir `.venv` + script de arranque en lugar de `.exe`.
- PyInstaller puede no recoger recursos estáticos de `streamlit` o algunos paquetes; si ves errores, inspecciona el log de PyInstaller para ver qué módulo faltó (añade `--hidden-import` según el error).
- Si el ejecutable no arranca, prueba `--onedir` y ejecuta la app dentro del directorio `dist/` para ver archivos faltantes.
- A veces conviene transformar `streamlit` en un wrapper: crear `runner.py` que haga `import subprocess; subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py', '--server.port', '8501'])` y empaquetar `runner.py` como exe; así `streamlit` correrá con el intérprete embebido. Esto sigue sin ser 100% garantizado.


## 8) Alternativa robusta: carpeta portable con .venv (recomendada para redes inestables)
La forma más estable es entregar una carpeta `califica_rubrica` que contenga `.venv` ya preparado y un script para arrancar.

Pasos rápidos para preparar la carpeta portable en el PC con buena conexión y luego llevarla al PC objetivo:

1. En máquina con buena conexión, dentro de `califica_rubrica`:
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Opcional: limpiar caches grandes
pip cache purge
```
2. Comprime la carpeta `califica_rubrica` (zip/7z) y copia al PC de aula.
3. En el PC destino, descomprime, activa el venv y ejecuta `streamlit run app.py`.

Crear un `run.bat` (Windows) en `califica_rubrica`:

```bat
@echo off
:: activar venv
call .venv\Scripts\activate.bat
:: arrancar streamlit
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
```

Crear un `run.sh` (Linux/macOS):

```bash
#!/usr/bin/env bash
source .venv/bin/activate
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Esta alternativa evita muchos problemas de empaquetado y requiere menos ajustes.


## 9) Notas finales y checklist de verificación
- Antes de mover la carpeta al PC destino, prueba lo siguiente en la máquina de preparación:
  - `python -c "import streamlit, pandas; print(streamlit.__version__)"`
  - `streamlit run app.py` y cargar la UI.
  - Ejecutar `python -m db` o un pequeño script que invoque `db.export_csv()` para verificar que las exportaciones funcionan.
- Si quieres que haga el ZIP portable aquí en el Codespace con la estructura `califica_rubrica` (con o sin .venv), dime y lo creo; ten en cuenta que el `.venv` será grande y subirlo a un repo no es ideal.


---

Si quieres, ahora puedo:
- generar `docs/guia_app.md` (ya lo creé en `docs/guia_app.md` en el proyecto),
- preparar un ZIP `califica_rubrica.zip` con la estructura base (sin `.venv`) listo para descargar, o
- intentar construir un `.exe` de prueba en este entorno (solo si el entorno admite creación de binarios Windows — lo normal es que no). 

Dime qué prefieres que haga a continuación: crear ZIP minimal, incluir `.venv` grande en el ZIP, o preparar pasos adicionales para auto-py-to-exe (comandos PyInstaller concretos).
 
## Apéndice: ZIP creado — `califica_rubrica.zip`

He generado un ZIP llamado `califica_rubrica.zip` dentro del workspace con una copia de la estructura mínima lista para llevar a un PC local. A continuación tienes información práctica y comandos para usarlo.

- Ruta en este workspace (ejemplo): `/workspaces/rubrica-streamlit/califica_rubrica.zip`
- Contenido principal del ZIP:
  - `app.py`, `db.py`, `utils.py` (scripts principales)
  - `requirements.txt`, `README.md`
  - `data/` (contiene CSVs y `rubrica.db` si estaba presente)
  - `run.sh` (Linux/macOS) y `run.bat` (Windows)
  - `tests/` (si existían)

Notas importantes sobre el ZIP y el entorno:

- El ZIP NO incluye el `.venv` (entorno virtual) por defecto. Esto mantiene el archivo pequeño y portable. Incluir `.venv` es posible pero el ZIP será mucho mayor.
- Si necesitas máxima fiabilidad (evitar instalaciones en máquinas con internet inestable), lo ideal es crear `.venv` en la máquina con buena conexión, instalar dependencias, y luego comprimir la carpeta completa `califica_rubrica/` (incluyendo `.venv`) para moverla al PC destino.

Cómo extraer y usar el ZIP (Linux/macOS)

```bash
# en el PC destino, por ejemplo en tu carpeta de documentos
unzip califica_rubrica.zip -d ~/califica_rubrica
cd ~/califica_rubrica

# Crear y activar venv localmente (si no llevaste .venv en el ZIP)
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# arrancar la app
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Cómo extraer y usar el ZIP (Windows PowerShell)

```powershell
# en PowerShell (ejecutar en una carpeta destino)
Expand-Archive -Path .\califica_rubrica.zip -DestinationPath .\califica_rubrica
cd .\califica_rubrica

# Crear y activar venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # o Activate.bat en cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# arrancar la app
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Uso rápido con los scripts incluidos

- Windows: ejecutar `run.bat` (hace `activate` y `streamlit run app.py`).
- Linux/macOS: ejecutar `./run.sh start` (si lo haces ejecutable con `chmod +x run.sh`) o `./run.sh restart`.

Si quieres incluir `.venv` en el ZIP (opcional)

1. En una máquina con buena conexión, dentro de `califica_rubrica` crea el venv e instala dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
```

2. Comprime incluyendo `.venv`:

```bash
zip -r califica_rubrica_with_venv.zip califica_rubrica
```

Advertencia: el ZIP con `.venv` puede ser muy grande (decenas o centenares de MB). Solo recomendarlo si vas a mover el paquete por USB o red interna.

Descarga desde este Codespace / repositorio

Puedes descargar el ZIP desde la interfaz del editor (archivos -> click derecho -> Download) o usando la funcionalidad de la plataforma (si existe). También puedes copiarlo con scp/sftp si accedes al host.

Si quieres que prepare otra variante del ZIP (por ejemplo `onedir` con dependencias incluidas o un ZIP sin tests/data), dime exactamente qué incluir y lo creo.