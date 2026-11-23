# ================================================================
# RESPONSABILIDAD / MÓDULO: Javier Tadeo | Sprint 4 T47 | widgets de filtro por fecha
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Sprint 4 - T47 (Javier): filtro visual independiente en Tkinter.

No sustituye mostrar_caja_javier ni modifica permisos. Se monta en la pantalla
T55 cuando la función REAL de consulta T45 esté disponible.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from javier_t47_fechas import validar_rango_t47


def crear_filtros_t47(contenedor, al_consultar):
    """Crea entradas de fecha y llama `al_consultar(inicio, fin)` si son válidas.

    `al_consultar` es una función pasada por T55 / integrador; no se inventa
    su implementación ni se presume qué columnas tiene la base de datos.
    """
    if not callable(al_consultar):
        raise TypeError("al_consultar debe ser una función real de la pantalla de reportes.")

    marco = ttk.LabelFrame(contenedor, text="T47 · Ventas entre fechas")
    marco.pack(fill="x", padx=10, pady=8)

    ttk.Label(marco, text="Fecha inicial (AAAA-MM-DD)").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entrada_inicio = ttk.Entry(marco, width=15)
    entrada_inicio.grid(row=1, column=0, padx=5, pady=3, sticky="ew")

    ttk.Label(marco, text="Fecha final (AAAA-MM-DD)").grid(row=0, column=1, padx=5, pady=5, sticky="w")
    entrada_fin = ttk.Entry(marco, width=15)
    entrada_fin.grid(row=1, column=1, padx=5, pady=3, sticky="ew")

    def consultar():
        try:
            inicio, fin = validar_rango_t47(entrada_inicio.get(), entrada_fin.get())
        except ValueError as error:
            messagebox.showwarning("Rango inválido", str(error), parent=marco.winfo_toplevel())
            return
        al_consultar(inicio, fin)

    boton = ttk.Button(marco, text="Consultar periodo", command=consultar)
    boton.grid(row=1, column=2, padx=5, pady=3, sticky="ew")
    for columna in range(2):
        marco.columnconfigure(columna, weight=1)
    return marco
