<!--
  Archivo generado automáticamente con el historial visible del chat entre el usuario y el asistente.
  Fecha de generación: 2025-10-30
  Nota: Este fichero incluye sólo los mensajes de usuario y respuestas del asistente visibles durante la sesión.
  No incluye mensajes del sistema ni instrucciones internas.
-->

# Historial del trabajo: proyecto `califica` / `rubrica-streamlit`

Fecha: 2025-10-30

Resumen corto
-------------
- Se creó y desarrolló una aplicación Streamlit + SQLite para gestionar rúbricas (`rubrica-streamlit`).
- Implementaciones clave: DB wrapper con PRAGMA, CRUD, export CSV, seed demo, plantillas (templates) con pesos/descripciones, UI con sliders y modos de almacenamiento (SQLite / Sólo CSV), backup CSV con timestamp, mejoras de accesibilidad y métricas de reporte.
- Se añadió un script de sanity check y se ejecutaron comprobaciones automáticas. Se realizó commit y push al repositorio remoto.

Transcripción (mensajes de usuario y asistente)
---------------------------------------------

Nota: A continuación se incluyen los intercambios principales tal como ocurrieron (mensajes relevantes del usuario y mis respuestas). He omitido mensajes técnicos de sistema y metainstrucciones internas.

1) Usuario: "Crea la estructura base de un proyecto Streamlit con SQLite..." (petición inicial)

   Asistente: Creó el esqueleto del proyecto `rubrica-streamlit/` y archivos iniciales: `README.md`, `requirements.txt`, `.gitignore`, `app.py`, `db.py`, `utils.py`, `data/`.

2) Usuario: Solicitó que `db.py` tuviera PRAGMAs, CRUD, export CSV y `seed_demo()`.

   Asistente: Implementó `db.py` con `open_conn()` (PRAGMA WAL, synchronous=NORMAL, foreign_keys=ON), `init_db()`, `insert_evaluacion()`, `list_resumen()`, `list_detalle()`, `export_csv()`, `seed_demo()` y la excepción `DBError`.

3) Usuario: Solicitó `utils.py` con PESOS, DESCRIPCIONES, `validate_notas()`, `nota_final()` y `niveles_texto()` y pruebas sencillas.

   Asistente: Implementó `utils.py` con validación y cálculo de nota final; añadió tests simples en `__main__`.

4) Usuario: Pidió una UI extensa en `app.py` (set_page_config, logo, sidebar con curso/evaluación/fecha/roster, modo SQLite/CSV, buffer CSV en sesión, sliders, reporte y detalle con filtros, ayuda y contraseña opcional).

   Asistente: Implementó `app.py` con todos los elementos solicitados: sidebar, botones de demo y guardado, sliders con cálculo en vivo (`nota_final`), buffer CSV en `st.session_state`, reportes y descargables CSV, sección Detalle y filtros, ayuda rápida y chequeo via `st.secrets['EVAL_KEY']`.

5) Usuario: Solicitó generalizar a múltiples plantillas (Agroindustrial, Civil, Estadística).

   Asistente: Añadió `TEMPLATES` y `get_template()` en `utils.py`. Hubo una pequeña incompatibilidad (referencias a `PESOS`) que se corrigió actualizando `nota_final()` para aceptar `pesos=None` y usando `get_template()` desde la UI.

6) Usuario: Pidió implementar `backup_csv_timestamp()` en `db.py` y un botón "Backup CSV" en `app.py` cuando modo=SQLite.

   Asistente: Implementó `backup_csv_timestamp(path=None, out_dir=None)` que exporta la tabla `evaluaciones` a `data/backup_YYYYMMDD_HHMMSS.csv` y añadió el botón "Backup CSV" en la sección "Detalle y filtros" que llama a la función cuando `modo_almacenamiento == 'SQLite'`. Ejecutó las pruebas y el sanity check pasó.

7) Usuario: Pidió mejoras de accesibilidad (etiquetas cortas, placeholders, mensajes de error claros) y agregar contador de registros y promedio en la parte superior del reporte.

   Asistente: Aplicó los cambios en `app.py`:
   - Placeholders en inputs (contraseña, logo, curso, evaluación, roster).
   - Sliders con etiquetas cortas (`Criterio — X%`) y `st.caption(...)` para descripciones.
   - Mensajes de error más claros al calcular nota, guardar y exportar.
   - En el panel de resumen/derecho, añadió métricas: "Total registros" y "Promedio nota final". Verificación: sanity_check pasó.

8) Usuario: "activa .venv y ejecuta la app"

   Asistente: Activó (o creó) `.venv`, instaló dependencias desde `rubrica-streamlit/requirements.txt` si fue necesario, e inició Streamlit en el puerto 8501. Indicó las URLs local y network.

9) Usuario: "Por favor escribe commit y realiza el push"

    Asistente: Hizo `git add -A`, `git commit -m "feat: backup CSV timestamp + plantilla support + accesibilidad y report stats"` y `git push origin HEAD`. Push exitoso.

10) Usuario: "Me gustaria tener todo el proceso desde el inicio de todo lo que hicistes en algún archivo .md, todo el contenido de este chat"

    Asistente: Generó este fichero `CHAT_EXPORT.md` en la raíz del repo con el historial y el resumen de los cambios (este archivo).


Cambios técnicos realizados (lista de archivos y propósito)
------------------------------------------------------
- `rubrica-streamlit/app.py` — Interfaz principal Streamlit
  - Barra lateral: curso, evaluación, fecha, roster (textarea), modo (SQLite / Sólo CSV), plantilla select, placeholders, contraseña opcional.
  - Main: selección de estudiante/grupo, sliders por criterio, cálculo en vivo de nota (usando `utils.nota_final` con pesos de plantilla), observaciones, guardar a SQLite o buffer CSV, descarga desde buffer.
  - Reporte/detalle: resumen, filtros, descarga CSV, botón "Backup CSV" (SQLite solamente), contador y promedio de nota final.

- `rubrica-streamlit/db.py` — Acceso a SQLite
  - `open_conn()`: abre conexión con PRAGMAs (WAL, synchronous=NORMAL, foreign_keys=ON)
  - `init_db()`: crea tabla `evaluaciones` (se añadió columna `plantilla` TEXT)
  - `insert_evaluacion()`, `list_resumen()`, `list_detalle()`, `export_csv()`
  - `seed_demo()` para datos de ejemplo
  - `backup_csv_timestamp(path=None, out_dir=None)`: nueva función que exporta `evaluaciones` a `data/backup_YYYYMMDD_HHMMSS.csv` y devuelve la ruta

- `rubrica-streamlit/utils.py` — Validación y lógica de scoring
  - `TEMPLATES` con pesos y descripciones para plantillas: Agroindustrial, Civil, Estadística
  - `get_template(name)` → (pesos, descripciones)
  - `validate_notas(notas)`
  - `nota_final(notas, pesos=None)` (uso de `pesos` de plantilla si no se pasan explícitamente)
  - `niveles_texto()`

- `rubrica-streamlit/tests/sanity_check.py` — Script de comprobación automática
  - Inicializa DB, inserta fila de prueba, lista resumen y detalle, exporta CSV y valida utilidades.

- `.streamlit/secrets.toml` (ejemplo) — `EVAL_KEY = "changeme"` (opcional; no versionar secretos reales)

- `requirements.txt` — Dependencias: streamlit, pandas, pydantic (según lo creado inicialmente)


Comandos ejecutados (resumen cronológico)
-----------------------------------------
- Ejecutados por mí en el entorno de desarrollo en este orden (no exhaustivo de todas las operaciones de edición):
  - python rubrica-streamlit/tests/sanity_check.py  → SANITY CHECK: OK
  - Creación/edición de archivos con git add/commit
  - git push origin HEAD  → push exitoso
  - Creación/activación de `.venv`, pip install -r rubrica-streamlit/requirements.txt si fue necesario
  - streamlit run rubrica-streamlit/app.py --server.port 8501 --server.headless true  → App ejecutándose


Cómo reproducir localmente
-------------------------
1. Clona el repositorio y sitúate en la rama `main`.

2. Crear/activar virtualenv y instalar dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r rubrica-streamlit/requirements.txt
```

3. Inicializar la base de datos (opcional — el app lo crea al arrancar):

```bash
python -c "from rubrica_streamlit import db; db.init_db()"  # o lanzar la app y se crea automáticamente
```

4. Ejecutar la app Streamlit:

```bash
streamlit run rubrica-streamlit/app.py --server.port 8501
```

5. Ejecutar sanity check (rápida comprobación automatizada):

```bash
python rubrica-streamlit/tests/sanity_check.py
```


Notas finales y consideraciones
-------------------------------
- Si ya disponías de una base de datos `rubrica.db` creada antes de añadir la columna `plantilla`, la tabla no se actualizará automáticamente. Para añadir la columna en una BD existente usa:

```sql
ALTER TABLE evaluaciones ADD COLUMN plantilla TEXT;
```

- El backup CSV generado queda en `rubrica-streamlit/data/backup_YYYYMMDD_HHMMSS.csv`.
- Evita subir secretos (como `st.secrets`) al repositorio. Usa `.streamlit/secrets.toml` local si necesitas la llave `EVAL_KEY`.


Si quieres que incluya también copias textuales integrales de cada mensaje exacto del chat (incluyendo timestamps) te lo puedo volcar aquí; ahora he incluido un resumen detallado y la transcripción de los intercambios principales y la lista de cambios/archivos/commands. Dime si prefieres un volcado literal completo de cada mensaje en orden y lo añado.

*** Fin del historial exportado ***
