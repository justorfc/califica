"""
Carga masiva de CSV de evaluaciones a la tabla `evaluaciones` en `rubrica.db`.

Requisitos:
  pip install pandas

Uso:
  python tools/load_csv_to_sqlite.py --csv data/demo_evaluaciones_15.csv

Notas:
  - No elimina la base si existe; inserta filas adicionales (id autoincremental).
  - La tabla `evaluaciones` se crea si no existe.
"""
from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
import sys
import os
import pandas as pd
from typing import Dict, Any


REQUIRED_COLUMNS = [
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
    "observaciones",
]


def open_conn(path: str = "rubrica.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False, timeout=30)
    cur = conn.cursor()
    # PRAGMAs según especificación
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.execute("PRAGMA foreign_keys=ON;")
    conn.commit()
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            created_at TEXT
        )
        """
    )
    conn.commit()


def validar_fila(row: Dict[str, Any]) -> None:
    # validar notas
    for col in ["estructura", "programacion", "teoria", "ia", "reflexion", "presentacion"]:
        try:
            val = float(row[col])
        except Exception:
            raise ValueError(f"Columna {col} debe ser numérica en la fila: {row}")
        if not (1.0 <= val <= 5.0):
            raise ValueError(f"Valor fuera de rango en columna {col}: {val} (debe estar entre 1.0 y 5.0)")

    # validar fecha ISO YYYY-MM-DD
    try:
        datetime.strptime(str(row["fecha"]), "%Y-%m-%d")
    except Exception:
        raise ValueError(f"Fecha inválida (esperado YYYY-MM-DD): {row.get('fecha')}")


WEIGHTS = {
    "estructura": 15,
    "programacion": 20,
    "teoria": 15,
    "ia": 10,
    "reflexion": 15,
    "presentacion": 25,
}


def calc_nota_final(row: Dict[str, Any]) -> float:
    total_weight = sum(WEIGHTS.values())
    s = 0.0
    for k, w in WEIGHTS.items():
        s += float(row[k]) * w
    nota = s / total_weight
    return round(nota, 2)


def insert_row(conn: sqlite3.Connection, row: Dict[str, Any]) -> tuple[int, str]:
    cur = conn.cursor()
    now = datetime.now().isoformat()
    params = (
        row["curso"],
        row["evaluacion"],
        row["fecha"],
        row["grupo_o_estudiante"],
        float(row["estructura"]),
        float(row["programacion"]),
        float(row["teoria"]),
        float(row["ia"]),
        float(row["reflexion"]),
        float(row["presentacion"]),
        float(row["nota_final"]),
        row.get("observaciones", ""),
        now,
    )
    cur.execute(
        """
        INSERT INTO evaluaciones (
            curso, evaluacion, fecha, grupo_o_estudiante,
            estructura, programacion, teoria, ia, reflexion, presentacion,
            nota_final, observaciones, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        params,
    )
    conn.commit()
    return cur.lastrowid, now


def find_existing(conn: sqlite3.Connection, row: Dict[str, Any]) -> tuple[int, float] | None:
    """Busca una fila existente por clave natural y devuelve (id, nota_final) si existe."""
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nota_final FROM evaluaciones WHERE curso=? AND evaluacion=? AND fecha=? AND grupo_o_estudiante=? LIMIT 1",
        (row["curso"], row["evaluacion"], row["fecha"], row["grupo_o_estudiante"]),
    )
    r = cur.fetchone()
    if r:
        return int(r[0]), float(r[1]) if r[1] is not None else 0.0
    return None


def main(csv_path: str) -> None:
    if not os.path.exists(csv_path):
        print(f"Archivo no encontrado: {csv_path}")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except Exception as e:
        print(f"Error leyendo CSV: {e}")
        sys.exit(1)

    # comprobar columnas
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"Faltan columnas requeridas en el CSV: {missing}")
        sys.exit(1)

    # abrir DB y crear tabla si hace falta
    conn = open_conn("rubrica.db")
    init_db(conn)

    inserted = 0
    skipped = 0
    inserted_rows: list[Dict[str, Any]] = []
    skipped_rows: list[Dict[str, Any]] = []
    for _, r in df.iterrows():
        row = {c: r[c] for c in REQUIRED_COLUMNS}
        # calcular nota_final si no existe
        if "nota_final" not in r.index or pd.isna(r.get("nota_final", None)):
            row["nota_final"] = calc_nota_final(row)
        else:
            row["nota_final"] = float(r["nota_final"])

        try:
            validar_fila(row)
        except ValueError as e:
            print(f"Fila inválida: {e}")
            continue

        try:
            # deduplicación: evitar insertar si ya existe la misma combinación clave
            exists = find_existing(conn, row)
            if exists:
                ex_id, ex_nota = exists
                skipped += 1
                skipped_rows.append(
                    {
                        "existing_id": ex_id,
                        "curso": row["curso"],
                        "evaluacion": row["evaluacion"],
                        "fecha": row["fecha"],
                        "grupo_o_estudiante": row["grupo_o_estudiante"],
                        "existing_nota_final": ex_nota,
                    }
                )
            else:
                lastid, created_at = insert_row(conn, row)
                inserted += 1
                inserted_rows.append(
                    {
                        "id": lastid,
                        "curso": row["curso"],
                        "evaluacion": row["evaluacion"],
                        "fecha": row["fecha"],
                        "grupo_o_estudiante": row["grupo_o_estudiante"],
                        "nota_final": row["nota_final"],
                        "created_at": created_at,
                    }
                )
        except Exception as e:
            print(f"Error insertando fila: {e}")

    conn.close()
    print(f"Cargadas {inserted} filas desde {csv_path} -> rubrica.db")

    # Generar informe CSV con los ids insertados y notas calculadas
    report_dir = os.path.dirname(csv_path) or "data"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(report_dir, f"insert_report_{ts}.csv")
    try:
        if inserted_rows:
            pd.DataFrame(inserted_rows).to_csv(report_path, index=False, encoding="utf-8")
        else:
            # crear archivo vacío con cabeceras si no hubo inserts
            pd.DataFrame(columns=["id", "curso", "evaluacion", "fecha", "grupo_o_estudiante", "nota_final", "created_at"]).to_csv(report_path, index=False, encoding="utf-8")
        print(f"Informe de inserción creado: {report_path}")
    except Exception as e:
        print(f"No se pudo escribir el informe CSV: {e}")

    # Generar resumen agregado (inserted count, skipped count, avg/min/max de nota_final sobre los insertados)
    summary_path = os.path.join(report_dir, f"insert_report_{ts}_summary.csv")
    try:
        if inserted_rows:
            notas = [r["nota_final"] for r in inserted_rows]
            summary = {
                "inserted_count": inserted,
                "skipped_count": skipped,
                "nota_avg": round(float(sum(notas) / len(notas)), 2),
                "nota_min": min(notas),
                "nota_max": max(notas),
            }
        else:
            summary = {"inserted_count": 0, "skipped_count": skipped, "nota_avg": "", "nota_min": "", "nota_max": ""}

        pd.DataFrame(list(summary.items()), columns=["metric", "value"]).to_csv(summary_path, index=False, encoding="utf-8")
        print(f"Resumen agregado creado: {summary_path}")
    except Exception as e:
        print(f"No se pudo escribir el resumen agregado: {e}")

    print("Verifica en la app Streamlit o usando: sqlite3 rubrica.db 'select count(*) from evaluaciones;'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cargar CSV de evaluaciones a rubrica.db")
    parser.add_argument("--csv", default="data/demo_evaluaciones_15.csv", help="Ruta al CSV de entrada")
    args = parser.parse_args()
    main(args.csv)
