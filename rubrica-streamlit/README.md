
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
