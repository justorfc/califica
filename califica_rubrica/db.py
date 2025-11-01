"""Módulo de acceso a datos para la app de rúbricas.

Provee una interfaz segura y con PRAGMAs adecuados para SQLite
(WAL, synchronous=NORMAL, foreign_keys=ON) y operaciones CRUD
específicas para la tabla `evaluaciones`.
"""

from pathlib import Path
from datetime import datetime
import sqlite3
from typing import Any, Dict, List, Optional
import pandas as pd
import json


DB_DEFAULT = Path(__file__).resolve().parent / "rubrica.db"


class DBError(Exception):
    """Excepción genérica para errores de base de datos."""


def open_conn(path: Optional[str] = None) -> sqlite3.Connection:
    """Abrir conexión a SQLite y aplicar PRAGMAs recomendadas.

    Args:
        path: ruta al fichero de base de datos. Si es None se usa `rubrica.db` en el paquete.

    Returns:
        sqlite3.Connection con row_factory configurado.

    Raises:
        DBError si no se puede abrir la conexión.
    """
    try:
        db_path = Path(path) if path else DB_DEFAULT
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), timeout=30, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        # Aplicar PRAGMAs aconsejadas
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA foreign_keys=ON;")
        # No commit necesario para PRAGMAs en muchos casos, pero aseguramos
        conn.commit()
        return conn
    except Exception as ex:
        raise DBError(f"No se pudo abrir la conexión a la BD: {ex}") from ex


def init_db(path: Optional[str] = None) -> None:
    """Inicializa la base de datos creando la tabla `evaluaciones` si no existe."""
    create_sql = """
    CREATE TABLE IF NOT EXISTS evaluaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plantilla TEXT,
        curso TEXT,
        evaluacion TEXT,
        fecha TEXT,
        grupo_o_estudiante TEXT,
        estructura REAL,
        programacion REAL,
        teoria REAL,
        ia REAL,
        reflexion REAL,
        presentacion REAL,
        nota_final REAL,
        observaciones TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        conn = open_conn(path)
        cur = conn.cursor()
        cur.execute(create_sql)
        conn.commit()
    except DBError:
        raise
    except Exception as ex:
        raise DBError(f"Error inicializando la BD: {ex}") from ex
    finally:
        try:
            conn.close()
        except Exception:
            pass


def insert_evaluacion(item: Dict[str, Any], path: Optional[str] = None) -> int:
    """Inserta una evaluación en la tabla `evaluaciones`.

    Args:
        item: dict con campos compatibles (curso, evaluacion, fecha, grupo_o_estudiante,
              estructura, programacion, teoria, ia, reflexion, presentacion, nota_final, observaciones)
        path: ruta opcional a la BD.

    Returns:
        id insertado (int)

    Raises:
        DBError en caso de fallo.
    """
    allowed = [
        "plantilla",
        "curso",
        "evaluacion",
        "fecha",
        "grupo_o_estudiante",
        "estructura",
        "programacion",
        "teoria",
        "ia",
        "reflexion",
        "presentacion",
        "nota_final",
        "observaciones",
    ]

    # Construir columnas y parámetros de forma segura
    cols = []
    vals: List[Any] = []
    for k in allowed:
        if k in item:
            cols.append(k)
            vals.append(item[k])

    if not cols:
        raise DBError("No se proporcionaron columnas válidas para insertar")

    placeholders = ",".join(["?" for _ in cols])
    sql = f"INSERT INTO evaluaciones ({', '.join(cols)}) VALUES ({placeholders})"

    try:
        conn = open_conn(path)
        cur = conn.cursor()
        cur.execute(sql, tuple(vals))
        conn.commit()
        return cur.lastrowid
    except DBError:
        raise
    except Exception as ex:
        raise DBError(f"Error insertando evaluación: {ex}") from ex
    finally:
        try:
            conn.close()
        except Exception:
            pass


def list_resumen(path: Optional[str] = None, order: str = "DESC") -> List[Dict[str, Any]]:
    """Devuelve un resumen de evaluaciones: id, fecha, grupo_o_estudiante, nota_final.

    Args:
        path: ruta opcional a la BD.
        order: 'ASC' o 'DESC' para el orden por `fecha` (por defecto DESC).
    """
    if order.upper() not in ("ASC", "DESC"):
        order = "DESC"
    sql = f"SELECT id, fecha, grupo_o_estudiante, nota_final FROM evaluaciones ORDER BY fecha {order}"
    try:
        conn = open_conn(path)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        result: List[Dict[str, Any]] = []
        for r in rows:
            result.append({
                "id": r["id"],
                "fecha": r["fecha"],
                "grupo_o_estudiante": r["grupo_o_estudiante"],
                "nota_final": r["nota_final"],
            })
        return result
    except DBError:
        raise
    except Exception as ex:
        raise DBError(f"Error listando resumen: {ex}") from ex
    finally:
        try:
            conn.close()
        except Exception:
            pass


def list_detalle(path: Optional[str] = None, filtro_texto: Optional[str] = None, fecha: Optional[str] = None, order: str = "DESC") -> List[Dict[str, Any]]:
    """Devuelve detalles de evaluaciones con filtros opcionales.

    Args:
        path: ruta opcional a la BD.
        filtro_texto: texto para buscar en `curso`, `evaluacion`, `grupo_o_estudiante` o `observaciones`.
        fecha: filtrar por fecha exacta (string en el formato guardado en `fecha`).
        order: 'ASC' o 'DESC' para ordenar por `fecha`.
    """
    if order.upper() not in ("ASC", "DESC"):
        order = "DESC"

    where_clauses: List[str] = []
    params: List[Any] = []

    if filtro_texto:
        like = f"%{filtro_texto}%"
        where_clauses.append("(curso LIKE ? OR evaluacion LIKE ? OR grupo_o_estudiante LIKE ? OR observaciones LIKE ?)")
        params.extend([like, like, like, like])

    if fecha:
        where_clauses.append("fecha = ?")
        params.append(fecha)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    sql = f"SELECT * FROM evaluaciones {where_sql} ORDER BY fecha {order}"

    try:
        conn = open_conn(path)
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        result: List[Dict[str, Any]] = []
        for r in rows:
            # Con sqlite3.Row se puede acceder por nombre
            result.append({k: r[k] for k in r.keys()})
        return result
    except DBError:
        raise
    except Exception as ex:
        raise DBError(f"Error listando detalle: {ex}") from ex
    finally:
        try:
            conn.close()
        except Exception:
            pass


def export_csv(path: Optional[str] = None, out_path: Optional[str] = None) -> str:
    """Exporta todas las filas de `evaluaciones` a CSV y devuelve la ruta escrita.

    Args:
        path: ruta opcional a la BD.
        out_path: ruta de salida opcional. Si no se proporciona, se usa `data/evaluaciones_export.csv`.
    Returns:
        Ruta al fichero CSV creado.
    """
    try:
        conn = open_conn(path)
        df = pd.read_sql_query("SELECT * FROM evaluaciones ORDER BY fecha DESC", conn)
        data_dir = Path(__file__).resolve().parent / "data"
        data_dir.mkdir(exist_ok=True)
        if out_path:
            out = Path(out_path)
        else:
            out = data_dir / "evaluaciones_export.csv"
        # Conservar versión RAW (con saltos) y crear versión sanitizada para Excel
        if "observaciones" in df.columns:
            df["observaciones_raw"] = df["observaciones"].fillna("").astype(str)
            df["observaciones"] = df["observaciones_raw"].apply(lambda s: " | ".join([p.strip() for p in s.splitlines() if p.strip()]))
        # Escribir con BOM UTF-8 para mejorar compatibilidad con Excel/Windows
        df.to_csv(out, index=False, encoding="utf-8-sig")
        return str(out)
    except DBError:
        raise
    except Exception as ex:
        raise DBError(f"Error exportando CSV: {ex}") from ex
    finally:
        try:
            conn.close()
        except Exception:
            pass


def backup_csv_timestamp(path: Optional[str] = None, out_dir: Optional[str] = None) -> str:
    """Exporta todas las filas de `evaluaciones` a un CSV con timestamp en data/backup_YYYYMMDD_HHMMSS.csv.

    Args:
        path: ruta opcional a la BD.
        out_dir: directorio de salida opcional. Si no se proporciona, se usa `data/` dentro del paquete.

    Returns:
        Ruta al fichero CSV creado (string).

    Raises:
        DBError en caso de fallo.
    """
    try:
        conn = open_conn(path)
        df = pd.read_sql_query("SELECT * FROM evaluaciones ORDER BY fecha DESC", conn)
        base_dir = Path(__file__).resolve().parent / "data"
        if out_dir:
            base_dir = Path(out_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = base_dir / f"backup_{ts}.csv"
        # Conservar versión RAW (con saltos) y crear versión sanitizada para Excel
        if "observaciones" in df.columns:
            df["observaciones_raw"] = df["observaciones"].fillna("").astype(str)
            df["observaciones"] = df["observaciones_raw"].apply(lambda s: " | ".join([p.strip() for p in s.splitlines() if p.strip()]))
        # Escribir con BOM UTF-8 para mejorar compatibilidad con Excel/Windows
        df.to_csv(out, index=False, encoding="utf-8-sig")
        return str(out)
    except DBError:
        raise
    except Exception as ex:
        raise DBError(f"Error creando backup CSV: {ex}") from ex
    finally:
        try:
            conn.close()
        except Exception:
            pass


def seed_demo(path: Optional[str] = None) -> List[int]:
    """Inserta 5 registros de ejemplo para pruebas y devuelve la lista de ids.

    No se ejecuta automáticamente — debe llamarse explícitamente desde la UI.
    """
    demo_items: List[Dict[str, Any]] = [
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
            "observaciones": "Buen desempeño general"
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
            "observaciones": "Proyecto sobresaliente"
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
            "observaciones": "Necesita mejorar la implementación"
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
            "observaciones": "Muy buen manejo teórico"
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
            "observaciones": "Resultados esperados, documentar más"
        }
    ]

    inserted_ids: List[int] = []
    try:
        for itm in demo_items:
            try:
                new_id = insert_evaluacion(itm, path=path)
                inserted_ids.append(new_id)
            except Exception as ex:
                # Continuar intentando insertar los demás, pero registrar el error
                # Re-lanzamos al final si no se insertó ninguno
                continue

        if not inserted_ids:
            raise DBError("No se pudieron insertar registros demo")

        return inserted_ids
    except DBError:
        raise
    except Exception as ex:
        raise DBError(f"Error cargando datos demo: {ex}") from ex

