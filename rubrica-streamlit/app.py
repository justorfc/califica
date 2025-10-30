import streamlit as st
import pandas as pd
import datetime
from pathlib import Path
from typing import List

from utils import TEMPLATES, get_template, validate_notas, nota_final, niveles_texto

from db import (
    init_db,
    insert_evaluacion,
    list_resumen,
    list_detalle,
    export_csv,
    backup_csv_timestamp,
    seed_demo,
    DBError,
)


# Configuración de la página
st.set_page_config(page_title="Gestor de Evaluaciones", page_icon=":memo:", layout="wide")


# Inicializar DB
init_db()

# Acceso seguro a secretos: en algunos entornos (CI, contenedores) no existe
# el archivo `.streamlit/secrets.toml`. Si no es accesible, usamos un dict vacío
try:
    _st_secrets = st.secrets
except Exception:
    # Cualquier problema accediendo a st.secrets: tratamos como no hay secretos
    _st_secrets = {}


# Sidebar — parámetros y controles
st.sidebar.title("Controles")

# Control de acceso opcional vía secreto `EVAL_KEY` (mostrado al inicio de la barra lateral)
if _st_secrets.get("EVAL_KEY"):
    pw = st.sidebar.text_input("Contraseña de acceso", type="password", placeholder="Introduce la contraseña de acceso")
    if not pw:
        st.sidebar.warning("Introduce la contraseña para continuar.")
        st.stop()
    if pw != _st_secrets.get("EVAL_KEY"):
        st.sidebar.error("Contraseña incorrecta. Acceso denegado.")
        st.stop()

logo_url = st.sidebar.text_input("Logo URL (opcional)", placeholder="https://.../logo.png")
curso_sb = st.sidebar.text_input("Curso", value="", placeholder="Nombre del curso o materia")
evaluacion_sb = st.sidebar.text_input("Evaluación", value="", placeholder="Ej: Parcial 1, Proyecto")
fecha_sb = st.sidebar.date_input("Fecha", value=datetime.date.today())
grupos_text = st.sidebar.text_area("Grupos/Estudiantes (1 por línea)", placeholder="Escribe cada grupo o estudiante en una línea")
modo_almacenamiento = st.sidebar.selectbox("Modo de almacenamiento", ["SQLite", "Sólo CSV"]) 

# Selección de plantilla de rúbrica
plantilla_sel = st.sidebar.selectbox("Plantilla de rúbrica", list(TEMPLATES.keys()), index=0)

# Botón para cargar datos demo (en sidebar)
if st.sidebar.button("Cargar datos demo"):
    if modo_almacenamiento == "SQLite":
        try:
            ids = seed_demo()
            st.sidebar.success(f"Insertadas {len(ids)} evaluaciones demo (SQLite)")
        except DBError as e:
            st.sidebar.error(f"No se pudieron cargar los datos demo. Detalle: {e}")
    else:
        # Crear registros demo localmente en CSV
        demo_items = [
            {
                "curso": "Matemáticas I",
                "evaluacion": "Parcial 1",
                "fecha": "2025-10-01",
                "grupo_o_estudiante": "Grupo A",
                "estructura": 4.0,
                "programacion": 4.5,
                "teoria": 4.0,
                "ia": 3.5,
                "reflexion": 4.0,
                "presentacion": 4.2,
                "nota_final": 4.2,
                "observaciones": "Buen desempeño general",
                "plantilla": plantilla_sel,
            },
            {
                "curso": "Programación",
                "evaluacion": "Proyecto",
                "fecha": "2025-10-05",
                "grupo_o_estudiante": "Estudiante 23",
                "estructura": 4.5,
                "programacion": 5.0,
                "teoria": 3.8,
                "ia": 4.0,
                "reflexion": 4.1,
                "presentacion": 4.7,
                "nota_final": 4.5,
                "observaciones": "Proyecto sobresaliente",
                "plantilla": plantilla_sel,
            },
            {
                "curso": "Inteligencia Artificial",
                "evaluacion": "Tarea 2",
                "fecha": "2025-10-12",
                "grupo_o_estudiante": "Grupo B",
                "estructura": 3.5,
                "programacion": 3.8,
                "teoria": 4.2,
                "ia": 4.5,
                "reflexion": 3.9,
                "presentacion": 4.0,
                "nota_final": 3.98,
                "observaciones": "Necesita mejorar la implementación",
                "plantilla": plantilla_sel,
            },
            {
                "curso": "Física",
                "evaluacion": "Examen Final",
                "fecha": "2025-06-20",
                "grupo_o_estudiante": "Estudiante 07",
                "estructura": 4.0,
                "programacion": 0.0,
                "teoria": 4.8,
                "ia": 0.0,
                "reflexion": 4.4,
                "presentacion": 4.1,
                "nota_final": 4.3,
                "observaciones": "Muy buen manejo teórico",
                "plantilla": plantilla_sel,
            },
            {
                "curso": "Química",
                "evaluacion": "Laboratorio",
                "fecha": "2025-09-15",
                "grupo_o_estudiante": "Grupo C",
                "estructura": 3.9,
                "programacion": 0.0,
                "teoria": 3.7,
                "ia": 0.0,
                "reflexion": 3.8,
                "presentacion": 3.9,
                "nota_final": 3.83,
                "observaciones": "Resultados esperados, documentar más",
                "plantilla": plantilla_sel,
            },
        ]
        data_dir = Path(__file__).resolve().parent / "data"
        data_dir.mkdir(exist_ok=True)
        out = data_dir / "evaluaciones_only_csv.csv"
        df = pd.DataFrame(demo_items)
        # Si el archivo existe, anexar sin duplicar encabezado
        if out.exists():
            df.to_csv(out, mode="a", header=False, index=False)
        else:
            df.to_csv(out, index=False)
        st.sidebar.success(f"Insertadas {len(demo_items)} evaluaciones demo (CSV): {out}")


# Estilos CSS para cabecera y cards
css = f"""
<style>
.header {{display:flex; align-items:center; gap:16px; margin-bottom:16px}}
.logo {{height:64px; width:64px; object-fit:contain}}
.card {{background:#f8f9fa; padding:16px; border-radius:8px; box-shadow: 0 1px 4px rgba(0,0,0,0.08);}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# Cabecera con logo (si se proporciona)
with st.container():
    if logo_url:
        st.markdown(f"<div class='header'><img class='logo' src='{logo_url}' alt='logo'/><h1>Gestor de Evaluaciones</h1></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='header'><h1>Gestor de Evaluaciones</h1></div>", unsafe_allow_html=True)

# Ayuda rápida
with st.expander("Ayuda rápida"):
    st.write(
        """
Pasos rápidos para usar en clase:

1. En la barra lateral, completa `Curso` y `Evaluación`.
2. Pega la lista de grupos o estudiantes (una por línea) en `Grupos/Estudiantes`.
3. Selecciona el `Modo de almacenamiento`: "SQLite" para persistir en la base de datos local, o "Sólo CSV" para trabajar con un buffer descargable.
4. Para crear varias evaluaciones a la vez usa `Guardar evaluaciones` (crea una fila por cada línea del roster).
5. Para evaluar un único alumno/grupo, usa el panel principal: selecciona el grupo, ajusta los sliders y pulsa `Guardar evaluación`.
6. Usa `Cargar datos demo` para poblar ejemplos (útil para demostraciones rápidas).
7. En el panel derecho puedes descargar el resumen o el detalle filtrado en CSV.

Consejo: en entornos compartidos, configura `st.secrets['EVAL_KEY']` para proteger la interfaz.
"""
    )


# Botón para guardar evaluaciones — se guardará una fila por cada línea en 'grupos_text'
if st.sidebar.button("Guardar evaluaciones"):
    grupos = [g.strip() for g in grupos_text.splitlines() if g.strip()]
    if not grupos:
        grupos = ["-"]

    fecha_iso = fecha_sb.isoformat() if isinstance(fecha_sb, datetime.date) else str(fecha_sb)

    inserted = 0
    errors: List[str] = []
    for g in grupos:
        item = {
            "plantilla": plantilla_sel,
            "curso": curso_sb.strip(),
            "evaluacion": evaluacion_sb.strip(),
            "fecha": fecha_iso,
            "grupo_o_estudiante": g,
            "nota_final": 0.0,
            "observaciones": "",
        }
        try:
            if modo_almacenamiento == "SQLite":
                insert_evaluacion(item)
            else:
                # Append to CSV
                data_dir = Path(__file__).resolve().parent / "data"
                data_dir.mkdir(exist_ok=True)
                out = data_dir / "evaluaciones_only_csv.csv"
                df = pd.DataFrame([item])
                if out.exists():
                    df.to_csv(out, mode="a", header=False, index=False)
                else:
                    df.to_csv(out, index=False)
            inserted += 1
        except DBError as e:
            errors.append(str(e))

    if inserted:
        st.sidebar.success(f"Guardadas {inserted} evaluaciones ({modo_almacenamiento})")
    if errors:
        st.sidebar.error("Errores: " + "; ".join(errors))


# --- Panel principal: evaluación individual (selectbox, sliders, cálculo en vivo) ---
st.markdown("---")
st.header("Evaluación individual")
# roster desde sidebar
roster = [g.strip() for g in grupos_text.splitlines() if g.strip()]
if not roster:
    roster = ["-"]

selected = st.selectbox("Seleccionar grupo/estudiante", roster)

st.subheader("Puntuaciones por criterio")
notas: dict = {}
# Obtener pesos/descripciones desde la plantilla seleccionada
pesos, descripciones = get_template(plantilla_sel)
for criterio in ["estructura", "programacion", "teoria", "ia", "reflexion", "presentacion"]:
    # Etiqueta corta + porcentaje; la descripción completa se muestra como caption para accesibilidad
    short_label = f"{criterio.capitalize()} — {pesos.get(criterio,0)}%"
    notas[criterio] = st.slider(short_label, min_value=1.0, max_value=5.0, step=0.5, value=3.0)
    st.caption(descripciones.get(criterio, ""))

# cálculo en vivo
    try:
        validate_notas(notas)
        final = nota_final(notas, pesos=pesos)
    except Exception as ex:
        final = 0.0
        st.error(f"Error al calcular la nota final: {ex}. Revisa que todas las puntuaciones estén entre 1 y 5.")

st.metric("Nota final (ponderada)", f"{final}")

obs_main = st.text_area("Observaciones")

if "csv_buffer" not in st.session_state:
    st.session_state.csv_buffer = pd.DataFrame(columns=["plantilla","curso","evaluacion","fecha","grupo_o_estudiante","estructura","programacion","teoria","ia","reflexion","presentacion","nota_final","observaciones","created_at"])

if st.button("Guardar evaluación"):
    # validar notas
    try:
        validate_notas(notas)
    except ValueError as e:
        st.error(f"Validación de notas falló: {e}")
    else:
        item = {
            "plantilla": plantilla_sel,
            "curso": curso_sb.strip(),
            "evaluacion": evaluacion_sb.strip(),
            "fecha": fecha_sb.isoformat() if isinstance(fecha_sb, datetime.date) else str(fecha_sb),
            "grupo_o_estudiante": selected,
            "estructura": float(notas.get("estructura",0)),
            "programacion": float(notas.get("programacion",0)),
            "teoria": float(notas.get("teoria",0)),
            "ia": float(notas.get("ia",0)),
            "reflexion": float(notas.get("reflexion",0)),
            "presentacion": float(notas.get("presentacion",0)),
            "nota_final": float(final),
            "observaciones": obs_main.strip(),
        }

        if modo_almacenamiento == "SQLite":
            try:
                new_id = insert_evaluacion(item)
                st.success(f"Evaluación guardada en SQLite (id={new_id})")
            except DBError as e:
                st.error(f"Error al guardar en SQLite: {e}")
        else:
            # acumular en buffer y ofrecer descarga inmediata
            df = st.session_state.csv_buffer
            item_row = item.copy()
            item_row["created_at"] = datetime.datetime.now().isoformat()
            st.session_state.csv_buffer = pd.concat([df, pd.DataFrame([item_row])], ignore_index=True)
            st.success("Evaluación añadida al buffer CSV en sesión")
            csv_bytes = st.session_state.csv_buffer.to_csv(index=False).encode("utf-8")
            st.download_button("Descargar CSV (buffer)", data=csv_bytes, file_name="evaluaciones_buffer.csv", mime="text/csv")


# Área principal: resumen y export
# Layout: contenido principal + panel derecho para reporte
left_col, right_col = st.columns([2, 1])

with left_col:
    st.header("Resumen de evaluaciones")
    # Obtener resumen según modo
    if modo_almacenamiento == "SQLite":
        try:
            rows = list_resumen()
            df_resumen = pd.DataFrame(rows)
        except DBError as e:
            st.error(f"Error obteniendo resumen desde la BD: {e}")
            df_resumen = pd.DataFrame(columns=["id", "fecha", "grupo_o_estudiante", "nota_final"])
    else:
        # Desde buffer CSV en sesión
        df = st.session_state.get("csv_buffer", pd.DataFrame())
        if df.empty:
            df_resumen = pd.DataFrame(columns=["id", "fecha", "grupo_o_estudiante", "nota_final"])
        else:
            df_resumen = df.reset_index(drop=True).copy()
            df_resumen.insert(0, "id", df_resumen.index + 1)
            # Asegurar columnas
            for c in ["fecha", "grupo_o_estudiante", "nota_final"]:
                if c not in df_resumen.columns:
                    df_resumen[c] = ""

    if not df_resumen.empty:
        st.dataframe(df_resumen[["id", "fecha", "grupo_o_estudiante", "nota_final"]])
    else:
        st.info("No hay evaluaciones todavía. Usa el formulario en la barra lateral o carga datos demo.")

    # Exportar todo (usa export_csv() para SQLite, o buffer para CSV)
    if modo_almacenamiento == "SQLite":
        if st.button("Exportar evaluaciones a CSV"):
            try:
                path = export_csv()
                st.success(f"Exportado a {path}")
            except DBError as e:
                st.error(f"Error exportando CSV: {e}")
    else:
        if not st.session_state.csv_buffer.empty:
            csv_bytes = st.session_state.csv_buffer.to_csv(index=False).encode("utf-8")
            st.download_button("Descargar CSV (buffer completo)", data=csv_bytes, file_name="evaluaciones_buffer_full.csv", mime="text/csv")

with right_col:
    st.header("Reporte")
    st.write("Tabla resumen rápida")
    if not df_resumen.empty:
        st.table(df_resumen[["id", "fecha", "grupo_o_estudiante", "nota_final"]].head(10))
        # Descarga rápida del resumen
        csv_res = df_resumen[["id", "fecha", "grupo_o_estudiante", "nota_final"]].to_csv(index=False).encode("utf-8")
        st.download_button("Descargar resumen CSV", data=csv_res, file_name="resumen_evaluaciones.csv", mime="text/csv")
    else:
        st.info("No hay datos para el reporte")

# Sección: Detalle y filtros
st.markdown("---")
st.header("Detalle y filtros")
filtro_texto = st.text_input("Filtro de texto (buscar en curso/evaluacion/grupo/observaciones)")
fecha_filtro = st.date_input("Filtrar por fecha (dejar vacío para omitir)", value=None)
order = st.selectbox("Orden por fecha", ["DESC", "ASC"], index=0)

if st.button("Aplicar filtros"):
    # Obtener detalle según modo
    if modo_almacenamiento == "SQLite":
        try:
            fecha_param = fecha_filtro.isoformat() if fecha_filtro else None
            detalle = list_detalle(filtro_texto=filtro_texto or None, fecha=fecha_param, order=order)
            df_detalle = pd.DataFrame(detalle)
        except DBError as e:
            st.error(f"Error obteniendo detalle desde la BD: {e}")
            df_detalle = pd.DataFrame()
    else:
        df = st.session_state.get("csv_buffer", pd.DataFrame())
        if df.empty:
            df_detalle = pd.DataFrame()
        else:
            df_detalle = df.copy()
            if filtro_texto:
                mask = (
                    df_detalle["curso"].astype(str).str.contains(filtro_texto, case=False, na=False)
                    | df_detalle["evaluacion"].astype(str).str.contains(filtro_texto, case=False, na=False)
                    | df_detalle["grupo_o_estudiante"].astype(str).str.contains(filtro_texto, case=False, na=False)
                    | df_detalle["observaciones"].astype(str).str.contains(filtro_texto, case=False, na=False)
                )
                df_detalle = df_detalle[mask]
            if fecha_filtro:
                df_detalle = df_detalle[df_detalle["fecha"].astype(str) == fecha_filtro.isoformat()]
            if order == "DESC":
                df_detalle = df_detalle.sort_values(by="fecha", ascending=False)
            else:
                df_detalle = df_detalle.sort_values(by="fecha", ascending=True)

    if df_detalle.empty:
        st.info("No hay registros que cumplan los filtros")
    else:
        st.dataframe(df_detalle)
        csv_det = df_detalle.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar detalle CSV", data=csv_det, file_name="detalle_evaluaciones.csv", mime="text/csv")

    # Backup completo de la tabla a CSV con timestamp (solo cuando usamos SQLite)
    if modo_almacenamiento == "SQLite":
        if st.button("Backup CSV"):
            try:
                backup_path = backup_csv_timestamp()
                st.success(f"Backup creado: {backup_path}")
            except DBError as e:
                st.error(f"No se pudo crear el backup: {e}")
