from typing import Dict, Any, List, Tuple

# Plantillas disponibles y sus pesos/descripciones
TEMPLATES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "Agroindustrial": {
        "pesos": {
            "estructura": 15,
            "programacion": 20,
            "teoria": 15,
            "ia": 10,
            "reflexion": 15,
            "presentacion": 25,
        },
        "descripciones": {
            "estructura": "Claridad y organización de la solución",
            "programacion": "Calidad del código y solución técnica",
            "teoria": "Dominio de los conceptos teóricos",
            "ia": "Aplicación de técnicas de IA (si aplica)",
            "reflexion": "Capacidad de autoevaluación y reflexión",
            "presentacion": "Calidad de la presentación y entrega",
        },
    },
    "Civil": {
        "pesos": {
            "estructura": 20,
            "programacion": 10,
            "teoria": 20,
            "ia": 5,
            "reflexion": 15,
            "presentacion": 30,
        },
        "descripciones": {
            "estructura": "Diseño y coherencia estructural",
            "programacion": "Implementación de modelos/algoritmos (si aplica)",
            "teoria": "Dominio de principios teóricos",
            "ia": "Uso de técnicas avanzadas (cuando aplicable)",
            "reflexion": "Evaluación crítica del trabajo",
            "presentacion": "Claridad en planos y presentaciones",
        },
    },
    "Estadística": {
        "pesos": {
            "estructura": 10,
            "programacion": 20,
            "teoria": 25,
            "ia": 15,
            "reflexion": 10,
            "presentacion": 20,
        },
        "descripciones": {
            "estructura": "Organización del análisis estadístico",
            "programacion": "Calidad de scripts y reproducibilidad",
            "teoria": "Aplicación de fundamentos estadísticos",
            "ia": "Uso de métodos de aprendizaje (si aplica)",
            "reflexion": "Interpretación y discusión de resultados",
            "presentacion": "Claridad en visualizaciones y reportes",
        },
    },
}


def get_template(name: str) -> Tuple[Dict[str, int], Dict[str, str]]:
    """Devuelve (pesos, descripciones) para la plantilla solicitada.

    Si la plantilla no existe, devuelve la primera disponible por defecto.
    """
    if name in TEMPLATES:
        t = TEMPLATES[name]
        return t["pesos"], t["descripciones"]
    # fallback
    first = next(iter(TEMPLATES.values()))
    return first["pesos"], first["descripciones"]


def validate_notas(notas: Dict[str, Any]) -> None:
    """Valida que las notas estén en el rango 1..5 para las claves proporcionadas.

    Args:
        notas: diccionario con pares criterio -> valor

    Raises:
        ValueError: si alguna nota está fuera de rango o no es numérica.
    """
    for k, v in notas.items():
        try:
            val = float(v)
        except Exception:
            raise ValueError(f"La nota para '{k}' no es numérica: {v}")
        if not (1.0 <= val <= 5.0):
            raise ValueError(f"La nota para '{k}' está fuera del rango 1-5: {val}")


def nota_final(notas: Dict[str, Any], pesos: Dict[str, int] = None) -> float:
    """Calcula la nota final ponderada usando `pesos`.

    Solo se consideran las claves presentes en `notas` y `pesos`.
    El resultado se redondea a 2 decimales.
    """
    if not notas:
        return 0.0

    validate_notas(notas)

    if pesos is None:
        # use default template first
        first = next(iter(TEMPLATES.values()))
        pesos = first["pesos"]

    total = 0.0
    for k, w in pesos.items():
        if k in notas:
            val = float(notas[k])
            total += val * (w / 100.0)

    result = round(total, 2)
    return result


def niveles_texto() -> str:
    """Retorna la leyenda de niveles en texto.

    Formato: 1=Deficiente · 2=Básico · 3=Aceptable · 4=Bueno · 5=Excelente
    """
    return "1=Deficiente · 2=Básico · 3=Aceptable · 4=Bueno · 5=Excelente"


if __name__ == "__main__":
    # Pruebas simples / asserts
    sample = {
        "estructura": 4,
        "programacion": 5,
        "teoria": 3,
        "ia": 4,
        "reflexion": 4,
        "presentacion": 5,
    }

    # validate_notas no debe lanzar
    validate_notas(sample)

    # Calcular nota final manualmente para comprobar
    # manual: 4*0.15 + 5*0.20 + 3*0.15 + 4*0.10 + 4*0.15 + 5*0.25
    expected = round(4 * 0.15 + 5 * 0.20 + 3 * 0.15 + 4 * 0.10 + 4 * 0.15 + 5 * 0.25, 2)
    got = nota_final(sample)
    assert got == expected, f"nota_final incorrecta: got={got} expected={expected}"

    # Niveles texto
    assert "1=Deficiente" in niveles_texto()

    # Invalid value raises
    try:
        validate_notas({"estructura": 6})
        raise AssertionError("validate_notas no lanzó para valor inválido")
    except ValueError:
        pass

    print("utils.py: tests básicos OK")
