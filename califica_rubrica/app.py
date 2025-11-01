import streamlit as st
import pandas as pd
import datetime
from pathlib import Path
from typing import List

from utils import TEMPLATES, get_template, validate_notas, nota_final, niveles_texto, ejemplo_por_nota


# Map de títulos completos para cada criterio (mostrar al usuario)
CRITERIA_TITLES = {
    "estructura": "Estructura y claridad del Notebook",
    "programacion": "Programación y calidad del código",
    "teoria": "Fundamentos teóricos",
    "ia": "Aplicación de técnicas de IA",
    "reflexion": "Reflexión y autoevaluación",
    "presentacion": "Presentación y entrega",
}

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

# Nota: no usamos `st.secrets` en esta versión. La app es pública por defecto.


# Sidebar — parámetros y controles
st.sidebar.title("Controles")

# Nota: no hay control de acceso por clave en la interfaz — la app es pública.

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
        # Guardar con BOM UTF-8 para mejorar compatibilidad con Excel/Windows
        if out.exists():
            df.to_csv(out, mode="a", header=False, index=False, encoding="utf-8-sig")
        else:
            df.to_csv(out, index=False, encoding="utf-8-sig")
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

Consejo: en entornos compartidos, considera proteger el acceso mediante autenticación de red o un proxy.
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
# Mostrar rúbrica al inicio
st.header("Rúbrica de evaluación (escala 1–5)")
rubrica_rows = [
    {
        "Criterio": "Estructura y claridad del Notebook",
        "1 (Deficiente)": "Desorden total y sin secciones claras.",
        "2 (Básico)": "Secciones mínimas y confusas.",
        "3 (Aceptable)": "Estructura básica pero incompleta.",
        "4 (Bueno)": "Notebook organizado y legible.",
        "5 (Excelente)": "Presentación profesional, secciones completas y estética cuidada.",
        "Peso (%)": 15,
    },
    {
        "Criterio": "Programación y resultados",
        "1 (Deficiente)": "Código incompleto o erróneo.",
        "2 (Básico)": "Código funcional parcial.",
        "3 (Aceptable)": "Cálculos correctos en la mayoría.",
        "4 (Bueno)": "Cálculos correctos y reproducibles.",
        "5 (Excelente)": "Código optimizado, comentado y con análisis de resultados.",
        "Peso (%)": 20,
    },
    {
        "Criterio": "Comprensión teórica (Apéndices)",
        "1 (Deficiente)": "Sin comprensión del contenido.",
        "2 (Básico)": "Cita la teoría sin aplicarla.",
        "3 (Aceptable)": "Aplica fórmulas con errores menores.",
        "4 (Bueno)": "Explica y aplica la teoría correctamente.",
        "5 (Excelente)": "Integra teoría, análisis y razonamiento crítico.",
        "Peso (%)": 15,
    },
    {
        "Criterio": "Uso documentado de IA",
        "1 (Deficiente)": "No evidencia interacción.",
        "2 (Básico)": "Prompts irrelevantes.",
        "3 (Aceptable)": "Prompts útiles sin reflexión.",
        "4 (Bueno)": "Uso adecuado con reflexión clara.",
        "5 (Excelente)": "Prompts precisos, variados y estratégicos.",
        "Peso (%)": 10,
    },
    {
        "Criterio": "Reflexión técnica e interpretación de resultados",
        "1 (Deficiente)": "Sin conclusiones.",
        "2 (Básico)": "Conclusiones vagas.",
        "3 (Aceptable)": "Análisis básico.",
        "4 (Bueno)": "Argumentación técnica clara.",
        "5 (Excelente)": "Conclusiones profundas y bien justificadas.",
        "Peso (%)": 15,
    },
    {
        "Criterio": "Presentación oral y trabajo en equipo",
        "1 (Deficiente)": "Sin cohesión ni participación.",
        "2 (Básico)": "Exposición incompleta o desorganizada.",
        "3 (Aceptable)": "Participación parcial.",
        "4 (Bueno)": "Presentación fluida con buena coordinación.",
        "5 (Excelente)": "Exposición profesional, colaborativa y con dominio técnico.",
        "Peso (%)": 25,
    },
]
df_rubrica = pd.DataFrame(rubrica_rows)
df_rubrica = df_rubrica.set_index("Criterio")
with st.expander("Mostrar rúbrica de evaluación", expanded=False):
    st.table(df_rubrica)

st.markdown("---")
st.header("Evaluación individual")
# roster desde sidebar (prioridad: texto pegado en la barra lateral > CSV de `data/roster_groups_*.csv` > fallback Grupo 1..5)
roster = [g.strip() for g in grupos_text.splitlines() if g.strip()]
if not roster:
    # Intentar cargar roster desde CSV más reciente en data/
    data_dir = Path(__file__).resolve().parent / "data"
    roster = []
    try:
        files = sorted(data_dir.glob("roster_groups_*.csv"), reverse=True)
        for f in files:
            try:
                df_r = pd.read_csv(f)
                if "group" in df_r.columns:
                    # Mantener orden y eliminar duplicados
                    roster = list(dict.fromkeys([str(x).strip() for x in df_r["group"].tolist() if str(x).strip()]))
                    if roster:
                        break
            except Exception:
                continue
    except Exception:
        roster = []

    if not roster:
        # Fallback rápido útil en demos o si no hay datos
        roster = [f"Grupo {i}" for i in range(1, 6)]

# Mostrar selectbox con el roster, seleccionar el primero por defecto
selected = st.selectbox("Seleccionar grupo/estudiante", roster, index=0)

def _open_expander(criterio: str):
    """Callback para abrir el expander de un criterio cuando el slider cambia."""
    st.session_state[f"show_{criterio}"] = True


def _close_all_expanders():
    for c in ["estructura", "programacion", "teoria", "ia", "reflexion", "presentacion"]:
        st.session_state[f"show_{c}"] = False


st.subheader("Puntuaciones por criterio")
notas: dict = {}
# Obtener pesos/descripciones desde la plantilla seleccionada
pesos, descripciones = get_template(plantilla_sel)
for criterio in ["estructura", "programacion", "teoria", "ia", "reflexion", "presentacion"]:
    # Usar título completo si está disponible
    titulo = CRITERIA_TITLES.get(criterio, criterio.capitalize())
    short_label = f"{titulo} — {pesos.get(criterio,0)}%"

    show_key = f"show_{criterio}"
    slider_key = f"slider_{criterio}"
    if show_key not in st.session_state:
        st.session_state[show_key] = False

    c1, c2 = st.columns([2, 3])
    with c1:
        notas[criterio] = st.slider(short_label, min_value=1.0, max_value=5.0, step=0.5, value=3.0, key=slider_key, on_change=_open_expander, args=(criterio,))
    with c2:
        with st.expander(f"Descripción — {titulo}", expanded=st.session_state.get(show_key, False)):
            desc = descripciones.get(criterio, "")
            st.write(desc)
            st.markdown(f"**Peso:** {pesos.get(criterio,0)}%")
            st.markdown(f"**Niveles:** {niveles_texto()}")

            # Mostrar ejemplo dinámico según el valor actual del slider
            try:
                current_val = st.session_state.get(slider_key, 3.0)
                iv = int(round(float(current_val)))
            except Exception:
                iv = 3
            iv = max(1, min(5, iv))
            ejemplo = ejemplo_por_nota(criterio, iv)
            st.markdown(f"**Ejemplo para nota {iv}:**")
            st.info(ejemplo)

    # cálculo en vivo
    try:
        validate_notas(notas)
        final = nota_final(notas, pesos=pesos)
    except Exception as ex:
        final = 0.0
        st.error(f"Error al calcular la nota final: {ex}. Revisa que todas las puntuaciones estén entre 1 y 5.")

st.metric("Nota final (ponderada)", f"{final}")

# Generar observaciones automáticas a partir de las notas seleccionadas
def _build_observaciones():
    lines = []
    for criterio in ["estructura", "programacion", "teoria", "ia", "reflexion", "presentacion"]:
        slider_key = f"slider_{criterio}"
        titulo = CRITERIA_TITLES.get(criterio, criterio.capitalize())
        try:
            current_val = st.session_state.get(slider_key, 3.0)
            iv = int(round(float(current_val)))
        except Exception:
            iv = 3
        iv = max(1, min(5, iv))
        ejemplo = ejemplo_por_nota(criterio, iv)
        # Formato: "Título — N. Ejemplo"
        lines.append(f"{titulo} — {iv}. {ejemplo}")
    return "\n".join(lines)

# Checkbox para permitir bloquear la actualización automática si el docente quiere editar a mano
if "observaciones_lock" not in st.session_state:
    st.session_state["observaciones_lock"] = False

generated_obs = _build_observaciones()
lock = st.checkbox("Bloquear observaciones (no actualizar automáticamente)", value=st.session_state.get("observaciones_lock", False), key="observaciones_lock")
if lock:
    # mantener texto previo si existe
    if "observaciones_text" not in st.session_state:
        st.session_state["observaciones_text"] = ""
    obs_main = st.text_area("Observaciones", value=st.session_state.get("observaciones_text", ""), key="observaciones_text")
else:
    # Forzar actualización del contenido en session_state para que el widget muestre el texto generado
    st.session_state["observaciones_text"] = generated_obs
    obs_main = st.text_area("Observaciones", value=st.session_state.get("observaciones_text", ""), key="observaciones_text")

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
            # Descargar el buffer en UTF-8 con BOM para evitar problemas en Excel
            csv_bytes = st.session_state.csv_buffer.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
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
            csv_bytes = st.session_state.csv_buffer.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button("Descargar CSV (buffer completo)", data=csv_bytes, file_name="evaluaciones_buffer_full.csv", mime="text/csv")

with right_col:
    st.header("Reporte")
    st.write("Tabla resumen rápida")
    if not df_resumen.empty:
        st.table(df_resumen[["id", "fecha", "grupo_o_estudiante", "nota_final"]].head(10))
        # Descarga rápida del resumen
        csv_res = df_resumen[["id", "fecha", "grupo_o_estudiante", "nota_final"]].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("Descargar resumen CSV", data=csv_res, file_name="resumen_evaluaciones.csv", mime="text/csv")
    else:
        st.info("No hay datos para el reporte")

    # --- Exportes detallados: por evaluación actual y para todas las evaluaciones ---
    st.markdown("---")
    st.subheader("Exportes detallados")

    def build_detailed_df_from_rows(rows: list):
        # rows: list of dicts from DB or constructed current item
        items = []

        def _sanitize_text(s: object) -> str:
            """Eliminar saltos de línea y normalizar texto para CSV (una línea por celda)."""
            if s is None:
                return ""
            txt = str(s)
            parts = [p.strip() for p in txt.splitlines() if p.strip()]
            return " | ".join(parts)

        for r in rows:
            item = r.copy()
            # Añadir textos cualitativos por criterio y sanitizarlos
            for crit in ["estructura", "programacion", "teoria", "ia", "reflexion", "presentacion"]:
                try:
                    val = int(round(float(item.get(crit, 3))))
                except Exception:
                    val = 3
                item[f"{crit}_text"] = _sanitize_text(ejemplo_por_nota(crit, val))
            # Conservar versión raw de observaciones y sanitizar la que irá al CSV
            if "observaciones" in item:
                item["observaciones_raw"] = str(item.get("observaciones", ""))
                item["observaciones"] = _sanitize_text(item.get("observaciones"))
            items.append(item)

        df = pd.DataFrame(items)
        # Ordenar columnas para legibilidad
        cols = ["id","plantilla","curso","evaluacion","fecha","grupo_o_estudiante"] if "id" in df.columns else ["plantilla","curso","evaluacion","fecha","grupo_o_estudiante"]
        for crit in ["estructura","programacion","teoria","ia","reflexion","presentacion"]:
            cols.extend([crit, f"{crit}_text"])
        cols.extend(["nota_final","observaciones","created_at"]) if "created_at" in df.columns else cols.extend(["nota_final","observaciones"])
        # keep only existing columns in that order
        cols = [c for c in cols if c in df.columns]
        return df[cols]

    # Exportar evaluación actual (detallada) — siempre mostrar botón de descarga que toma el estado actual
    current = {
        "plantilla": plantilla_sel,
        "curso": curso_sb.strip(),
        "evaluacion": evaluacion_sb.strip(),
        "fecha": fecha_sb.isoformat() if isinstance(fecha_sb, datetime.date) else str(fecha_sb),
        "grupo_o_estudiante": selected or "current",
    }
    for crit in ["estructura","programacion","teoria","ia","reflexion","presentacion"]:
        current[crit] = float(notas.get(crit, 3.0))
    current["nota_final"] = float(final)
    current["observaciones"] = obs_main.strip()
    df_det = build_detailed_df_from_rows([current])
    # Descargar con BOM UTF-8 para compatibilidad con Excel
    csv_bytes = df_det.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    safe_name = str(current.get("grupo_o_estudiante", "current")).replace(" ", "_")
    st.download_button("Descargar evaluación actual (CSV)", data=csv_bytes, file_name=f"evaluacion_{safe_name}.csv", mime="text/csv")

    # Exportar todas las evaluaciones detalladas desde la BD
    if st.button("Exportar todas las evaluaciones (detalladas)"):
        try:
            rows = list_detalle()
            df_all = build_detailed_df_from_rows(rows)
            data_dir = Path(__file__).resolve().parent / "data"
            data_dir.mkdir(exist_ok=True)
            out = data_dir / "evaluaciones_detalldas_export.csv"
            # Guardar archivo en disco usando UTF-8 BOM
            df_all.to_csv(out, index=False, encoding="utf-8-sig")
            csv_bytes = df_all.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.success(f"Exportadas {len(df_all)} evaluaciones (detalladas)")
            st.download_button("Descargar todas evaluaciones (detalladas)", data=csv_bytes, file_name="evaluaciones_detalladas.csv", mime="text/csv")
        except DBError as e:
            st.error(f"Error exportando detalle: {e}")

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
    csv_det = df_detalle.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button("Descargar detalle CSV", data=csv_det, file_name="detalle_evaluaciones.csv", mime="text/csv")

    # Backup completo de la tabla a CSV con timestamp (solo cuando usamos SQLite)
    if modo_almacenamiento == "SQLite":
        if st.button("Backup CSV"):
            try:
                backup_path = backup_csv_timestamp()
                st.success(f"Backup creado: {backup_path}")
            except DBError as e:
                st.error(f"No se pudo crear el backup: {e}")
