# ================================================================
# RESPONSABILIDAD / MÓDULO: Javier Tadeo | Sprint 4 T47 | validación estricta de rango de fechas
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Sprint 4 - T47 (Javier): validación de fechas, sin tocar SQLite.

Este módulo NO implementa la consulta de ventas: depende de T45, aún sin
CREATE TABLE ni funciones confirmadas. No modifica los archivos del equipo.
"""

from datetime import date
from re import fullmatch


def validar_rango_t47(fecha_inicial: str, fecha_final: str) -> tuple[str, str]:
    """Devuelve fechas 'AAAA-MM-DD' válidas, incluyendo ambos extremos.

    Valida las entradas, pero NO consulta la base de datos.
    """
    fechas = []
    for nombre, valor in (("inicial", fecha_inicial), ("final", fecha_final)):
        if not isinstance(valor, str) or not fullmatch(r"\d{4}-\d{2}-\d{2}", valor.strip()):
            raise ValueError(f"La fecha {nombre} debe tener el formato AAAA-MM-DD.")
        try:
            fechas.append(date.fromisoformat(valor.strip()))
        except ValueError as error:
            raise ValueError(f"La fecha {nombre} no es válida.") from error

    inicio, fin = fechas
    if inicio > fin:
        raise ValueError("La fecha inicial no puede ser posterior a la final.")
    return inicio.isoformat(), fin.isoformat()


def enviar_rango_validado_t47(fecha_inicial: str, fecha_final: str, consulta_confirmada):
    """Envía fechas válidas a una función de consulta REAL cuando exista T45.

    `consulta_confirmada` la proporcionará el integrador al confirmar la
    función de T45 y el contrato de retorno. No se presupone ninguna tabla.
    """
    if not callable(consulta_confirmada):
        raise TypeError("Falta una función de consulta confirmada por el responsable de T45.")
    inicio, fin = validar_rango_t47(fecha_inicial, fecha_final)
    return consulta_confirmada(inicio, fin)
