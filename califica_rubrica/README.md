# rubrica-streamlit

Aplicación Streamlit + SQLite para gestionar rúbricas y evaluaciones.

Este repositorio contiene una app mínima (ubicada en la carpeta `rubrica-streamlit/`) que
permite crear evaluaciones por criterios, calcular notas ponderadas según plantillas,
persistir en SQLite o acumular en un buffer CSV en sesión, y exportar datos.

Estado: proyecto en desarrollo (procedimientos básicos implementados). Fecha: 2025-10-30

## Estructura

- `rubrica-streamlit/app.py` — Interfaz principal (Streamlit).
- `rubrica-streamlit/db.py` — Helpers SQLite (PRAGMAs, init, CRUD, export, backup CSV).
- `rubrica-streamlit/utils.py` — Plantillas, validación y cálculo de nota.
- `rubrica-streamlit/data/` — CSVs generados por la app.
- `rubrica-streamlit/tests/` — Sanity check y pruebas rápidas.

## Requisitos

- Python 3.10+
- pip

Instalar dependencias (desde la raíz del repo):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r rubrica-streamlit/requirements.txt
```

## Ejecutar la app

Desde la raíz del repositorio:

```bash
streamlit run rubrica-streamlit/app.py --server.port 8501
```

La UI estará disponible en `http://localhost:8501` (o en la URL que exponga tu entorno).

### Script de ejecución (recomendado)

Hay un script auxiliar en la raíz del proyecto `run.sh` que facilita arrancar, parar
y revisar la app sin recordar las opciones de Streamlit ni manejar PIDs manualmente.

Usos básicos (desde la raíz del repo):

```bash
./run.sh start    # arranca Streamlit (usa .venv si existe) y guarda PID en .run/streamlit.pid
./run.sh stop     # para el proceso (usa PID guardado o pkill si no existe)
./run.sh status   # muestra estado y puertos escuchando (8501/8502)
./run.sh logs     # muestra las últimas líneas del log (streamlit_8501.log)
```

El script también soporta `restart` y es compatible con entornos donde exista un `.venv`
local creado con `python3 -m venv .venv`.

## Comprobación automática (sanity check)

Hay un script de comprobación rápida que inicializa una DB temporal, inserta registros,
exporta CSV y valida utilidades:

```bash
python rubrica-streamlit/tests/sanity_check.py
```

## Funcionalidades destacadas

- Plantillas de rúbrica (Agroindustrial, Civil, Estadística) con pesos y descripciones.
- Modo de almacenamiento dual: `SQLite` (persistente en el contenedor) o `Sólo CSV` (buffer en sesión con descarga).
- Backup CSV con timestamp: `db.backup_csv_timestamp()` — genera `rubrica-streamlit/data/backup_YYYYMMDD_HHMMSS.csv`.
- Accesibilidad y UX: etiquetas cortas, captions descriptivas, placeholders, mensajes de error claros.
- Exportación CSV desde BD y desde buffer de sesión.

## Notas sobre renombrado del repositorio

El repo fue renombrado desde `califica` a `rubrica-streamlit`. Los remotes locales se han
actualizado automáticamente para apuntar a `https://github.com/justorfc/rubrica-streamlit`.

Si tienes una copia local creada antes del cambio y el remote apunta aún al nombre antiguo,
actualiza el origin con:

```bash
git remote set-url origin https://github.com/<usuario>/rubrica-streamlit
```

GitHub suele mantener redirecciones desde el nombre antiguo, por lo que la mayor parte de
las operaciones seguirá funcionando aún sin cambios locales, pero es recomendable actualizar
el `origin` para reflejar el nuevo nombre.

## Contribuir

1. Fork
2. Crear branch con tus cambios
3. Abrir Pull Request

Para cambios mayores, abre un issue primero describiendo la propuesta.

## Licencia

Revisa el fichero `LICENSE` en la raíz del repo.

---

¿Quieres que además actualice el `README.md` de la raíz del repo (archivo `./README.md`) para que muestre un resumen y enlace hacia `rubrica-streamlit/`? Puedo hacerlo ahora y commitearlo.

# Rubrica Streamlit

Aplicación base para gestionar rúbricas usando Streamlit (UI) y SQLite (almacenamiento).

Este repositorio contiene una plantilla mínima que puedes extender para crear, listar y
exportar rúbricas. Está pensada como punto de partida educativo y práctico.

## Estructura principal

- `app.py` - Interfaz principal de Streamlit (crear, listar, exportar rúbricas).
- `db.py` - Lógica de acceso a datos con SQLite (inicialización, CRUD básico, exportar CSV).
- `utils.py` - Modelos Pydantic y utilidades (exportar a CSV, validaciones ligeras).
- `requirements.txt` - Dependencias del proyecto.
- `.gitignore` - Archivos y carpetas ignoradas por Git.
- `data/` - Carpeta para exportes CSV generados por la aplicación.

## Requisitos

- Python 3.10+ recomendado
- `pip` para instalar dependencias

Instala dependencias con:

```bash
# Rubrica Streamlit

Aplicación base para gestionar rúbricas y evaluaciones usando Streamlit (UI) y SQLite (almacenamiento).

Esta carpeta contiene una plantilla mínima para crear, listar, evaluar y exportar evaluaciones.

## Comandos rápidos (ejecución local)

- Instalar dependencias:

```bash
pip install -r rubrica-streamlit/requirements.txt
```

- Ejecutar la app (desde la raíz del workspace):

```bash
streamlit run rubrica-streamlit/app.py
```

Recomendado (opcional): crear y activar un entorno virtual antes de instalar.

## Pruebas manuales (lista)

Realiza estas pruebas manuales para comprobar el funcionamiento básico:

1) Guardar evaluación (SQLite) y verla en Resumen/Detalle
  - Selecciona `Modo de almacenamiento = SQLite` en la barra lateral.
  - Rellena `Curso`, `Evaluación`, añade al menos un `Grupo/Estudiante` en el textarea (1 por línea).
  - En el panel principal, selecciona el grupo, ajusta los sliders y pulsa `Guardar evaluación`.
  - Abre `Resumen` y `Detalle y filtros` para verificar que la fila aparece.

2) Modo “Sólo CSV”: agregar filas y descargar
  - Selecciona `Modo de almacenamiento = Sólo CSV`.
  - Guarda varias evaluaciones desde el panel principal (o usa `Guardar evaluaciones` en la barra lateral).
  - Verás que las filas se acumulan en el buffer de sesión; usa el botón `Descargar CSV (buffer)` para obtenerlas.

3) Filtros por texto y fecha
  - En `Detalle y filtros` prueba buscar por texto (p. ej. nombre del curso o parte de las observaciones).
  - Usa el filtro de fecha para mostrar sólo registros de una fecha concreta.

4) Carga de datos demo
  - En la barra lateral pulsa `Cargar datos demo`.
  - Si estás en `SQLite` se insertarán registros en la BD; si estás en `Sólo CSV` se añadirá un fichero `data/evaluaciones_only_csv.csv`.

5) Validación de rangos (notas fuera de 1–5)
  - Intenta introducir valores fuera del rango (la UI limita los sliders, pero prueba llamadas directas a funciones si pruebas programáticamente).
  - `utils.validate_notas()` debe lanzar `ValueError` para notas inválidas.

6) Export CSV desde SQLite y desde memoria
  - En modo `SQLite` usa `Exportar evaluaciones a CSV` para generar `data/evaluaciones_export.csv`.
  - En modo `Sólo CSV` usa `Descargar CSV (buffer completo)` o `Descargar resumen CSV` en el panel derecho.

## Checklist de QA (para pruebas en clase)

Marca cada punto tras verificarlo en tu entorno:

- [ ] La app arranca con `streamlit run rubrica-streamlit/app.py` y muestra la interfaz.
- [ ] Si `EVAL_KEY` está definido en `rubrica-streamlit/.streamlit/secrets.toml`, la app pide contraseña en la barra lateral y bloquea el acceso si no coincide.
- [ ] Se pueden crear evaluaciones en modo `SQLite` y aparecen en `Resumen` y `Detalle`.
- [ ] En modo `Sólo CSV` las evaluaciones se acumulan en el buffer de sesión y se descargan correctamente.
- [ ] Los filtros por texto y fecha devuelven los resultados esperados.
- [ ] La carga de datos demo inserta 5 ejemplos correctamente en ambos modos.
- [ ] `utils.validate_notas()` rechaza notas fuera de 1–5 y `nota_final()` calcula la nota ponderada correctamente.
- [ ] La exportación a CSV funciona desde SQLite (`export_csv`) y desde el buffer en memoria.
- [ ] La UI no lanza errores al interactuar con los sliders y botones principales (guardar, descargar, exportar).

## Sanity check automatizado

Si quieres ejecutar una comprobación rápida automática (inicializa una BD temporal,
inserta registros, exporta CSV y valida utilidades), ejecuta el script de sanity:

```bash
python rubrica-streamlit/tests/sanity_check.py
```

## Notas rápidas
- El fichero `rubrica-streamlit/.streamlit/secrets.toml` sirve para desarrollo local. No subas secretos a un repositorio público.

### Estado de acceso — pública

Esta aplicación está pensada para ser utilizada por el profesorado de la universidad sin
restricciones: por defecto la app no requiere contraseña ni claves para acceder a la interfaz.
Si no existe un fichero de secretos con `EVAL_KEY`, la app no solicitará ninguna contraseña.

Si deseas proteger una instancia particular, puedes crear localmente `.streamlit/secrets.toml`
con la clave `EVAL_KEY`, pero ten en cuenta que el repositorio no contiene claves y `.streamlit/secrets.toml`
está ignorado para evitar fugas accidentales.

### Secrets (clave opcional de acceso)

Para proteger la interfaz en entornos compartidos la app busca la clave `EVAL_KEY` en Streamlit secrets.
No es necesario crear este fichero para ejecutar la app localmente; si no existe, la app no pedirá contraseña.

Si quieres habilitar la contraseña en tu entorno local, copia el ejemplo y edítalo:

```bash
cp rubrica-streamlit/.streamlit/secrets.example.toml rubrica-streamlit/.streamlit/secrets.toml
# luego edita .streamlit/secrets.toml y cambia EVAL_KEY por tu clave
```

Ejemplo de `rubrica-streamlit/.streamlit/secrets.example.toml`:

```toml
# Ejemplo – no usar en producción
EVAL_KEY = "changeme"
```

El repositorio está configurado para ignorar `.streamlit/secrets.toml` y evitar que claves de desarrollo se suban por error.
- Los CSV generados por defecto se guardan en `rubrica-streamlit/data/`.
- Si planeas un despliegue real, considera usar una base de datos externa para persistencia (Postgres/Supabase).

## Despliegue en Render (Web Service)

Puedes desplegar esta app en Render como un "Web Service". Tienes dos opciones principales:

- Usar el build command de Render (sin Docker):

  - Build command: `pip install -r rubrica-streamlit/requirements.txt`
  - Start command: `streamlit run rubrica-streamlit/app.py --server.port $PORT --server.address 0.0.0.0`

- Usar un `Dockerfile` mínimo (opcional). Un ejemplo sencillo:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY rubrica-streamlit/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY rubrica-streamlit/ ./
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port", "$PORT", "--server.address", "0.0.0.0"]
```

Notas importantes sobre Render y costes:

- Render ofrece planes gratuitos y de pago. El plan gratuito puede suspender la app por inactividad y tiene límites de recursos. Para uso en clase o producción se recomienda al menos un plan pago o el uso de instancias que no se suspendan — consulta los precios en https://render.com/pricing (aproximadamente desde unos pocos dólares/mes para servicios básicos, varía según región y recursos).
- Persistencia: el sistema de archivos de Render no está pensado para almacenamiento duradero entre despliegues o reinstancias. El archivo `rubrica.db` (SQLite) que se crea en el contenedor NO es persistente a largo plazo. Recomendaciones:
  - Para datos duraderos usa una base de datos gestionada (Postgres, Cloud SQL, Supabase) y adapta `db.open_conn()`/config para usarla.
  - Como alternativa temporal, exporta periódicamente los CSV a un almacenamiento de objetos (S3, DigitalOcean Spaces) o descarga los CSV desde la UI antes de redeploy.


## Contribuir

Si quieres contribuir, crea un fork, haz tus cambios y abre un Pull Request. Para cambios grandes, abre un issue primero describiendo la propuesta.

## Licencia

Revisa el fichero `LICENSE` en la raíz del repo.

---

¿Quieres que añada un apartado con comandos de prueba automatizados (pytest) o un script de sanity-check que inserte y verifique algunos registros automáticamente?
	- UI para añadir/editar criterios, pesos y descripciones
