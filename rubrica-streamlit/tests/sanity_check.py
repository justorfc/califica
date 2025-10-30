#!/usr/bin/env python3
"""Sanity check script for rubrica-streamlit.

This script performs a few quick smoke tests against a temporary sqlite DB in
`rubrica-streamlit/tests/` to verify core behaviors: init DB, insert, list,
export CSV, utils validation, and seed_demo. It prints progress and exits with
non-zero on failure (exceptions will propagate).
"""
from pathlib import Path
import sys
import shutil

# Ensure module imports find rubrica-streamlit sources
HERE = Path(__file__).resolve().parent
# Add the package root (parent of tests/) so imports like `from db import ...` work
sys.path.insert(0, str(HERE.parent))

from db import init_db, insert_evaluacion, list_resumen, list_detalle, export_csv, seed_demo
from utils import validate_notas, nota_final


def main() -> None:
    workspace = HERE
    tmp_db = workspace / "sanity_test.db"
    if tmp_db.exists():
        tmp_db.unlink()

    print("[1/6] Inicializando DB...")
    init_db(path=str(tmp_db))

    print("[2/6] Insertando evaluación de prueba...")
    item = {
        "curso": "Sanity Curso",
        "evaluacion": "Sanity Eval",
        "fecha": "2025-10-30",
        "grupo_o_estudiante": "Test Student",
        "estructura": 4.0,
        "programacion": 4.5,
        "teoria": 4.0,
        "ia": 3.5,
        "reflexion": 4.0,
        "presentacion": 4.2,
        "nota_final": 4.2,
        "observaciones": "Prueba automática",
    }
    new_id = insert_evaluacion(item, path=str(tmp_db))
    assert new_id and new_id > 0
    print(f"  -> Insertado id={new_id}")

    print("[3/6] Listando resumen...")
    resumen = list_resumen(path=str(tmp_db))
    assert isinstance(resumen, list) and len(resumen) >= 1
    print(f"  -> {len(resumen)} filas en resumen")

    print("[4/6] Listando detalle y comprobando fila insertada...")
    detalle = list_detalle(path=str(tmp_db), filtro_texto=None, fecha=None)
    ids = [r["id"] for r in detalle]
    assert new_id in ids
    print("  -> detalle OK")

    print("[5/6] Exportando CSV desde BD...")
    out_csv = workspace / "sanity_export.csv"
    if out_csv.exists():
        out_csv.unlink()
    out_path = export_csv(path=str(tmp_db), out_path=str(out_csv))
    assert Path(out_path).exists()
    print(f"  -> CSV exportado a {out_path}")

    print("[6/6] Validando utilidades y seed_demo...")
    notas = {"estructura": 4, "programacion": 5, "teoria": 3, "ia": 4, "reflexion": 4, "presentacion": 5}
    validate_notas(notas)
    nf = nota_final(notas)
    assert isinstance(nf, float)
    demo_ids = seed_demo(path=str(tmp_db))
    assert isinstance(demo_ids, list) and len(demo_ids) >= 1
    print("  -> utils y seed_demo OK")

    print("\nSANITY CHECK: OK ✅")


if __name__ == "__main__":
    main()
