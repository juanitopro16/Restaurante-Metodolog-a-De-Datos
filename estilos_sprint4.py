# ================================================================
# RESPONSABILIDAD / MÓDULO: Patricio Cosaín | Sprint 4 T63 | estilos compartidos y componentes Tkinter
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""
estilos_sprint4.py  -  T63 · Estilos y componentes visuales compartidos
Sistema de Comandas para Restaurante · Sprint 4

Autor: Patricio Cosaín Torres (con apoyo de IA, revisado por el autor)

Archivo ÚNICO de estilos para todo el equipo. Solo usa Tkinter + ttk
(no requiere instalar nada). No modifica pantallas existentes: cada
compañero lo importa cuando rediseñe su pantalla.

Uso rápido:
    import estilos_sprint4 as est

    est.aplicar_estilos(ventana)                    # una vez, al crear la ventana
    est.crear_titulo(frame, "Inventario").pack()
    est.crear_boton(frame, "Guardar", comando, "primario").pack()
    tabla = est.crear_tabla(frame, ("id", "nombre"), ("ID", "Nombre"))
    est.configurar_tags_estado(tabla)
    tabla.insert("", "end", values=(1, "Tomate"), tags=(est.tag_estado("Pendiente"),))
"""

import tkinter as tk
from tkinter import ttk

# ---------------------------------------------------------------
# 1. PALETA DE COLORES
# ---------------------------------------------------------------
COLORES = {
    "fondo":        "#F5F6FA",   # fondo general de ventanas
    "panel":        "#FFFFFF",   # tarjetas / paneles
    "primario":     "#2C3E50",   # azul oscuro: títulos, botón principal
    "primario_hover": "#3D5469",
    "secundario":   "#7F8C8D",   # gris: botones secundarios
    "exito":        "#27AE60",   # verde: OK, recibido, libre
    "advertencia":  "#F39C12",   # naranja: en mínimo, pendiente
    "peligro":      "#C0392B",   # rojo: bajo mínimo, eliminar, ocupada
    "info":         "#2980B9",   # azul: solicitada, información
    "texto":        "#2D3436",
    "texto_claro":  "#FFFFFF",
    "borde":        "#DCDDE1",
}

# Fondos suaves para filas de tablas (más legibles que el color fuerte)
FONDOS_FILA = {
    "exito":       "#D5F5E3",
    "advertencia": "#FDEBD0",
    "peligro":     "#FADBD8",
    "info":        "#D6EAF8",
}

# ---------------------------------------------------------------
# 2. TIPOGRAFÍA
# ---------------------------------------------------------------
FUENTE_BASE = "Segoe UI"   # viene en Windows; si no existe, Tk usa otra

FUENTES = {
    "titulo":    (FUENTE_BASE, 18, "bold"),
    "subtitulo": (FUENTE_BASE, 13, "bold"),
    "normal":    (FUENTE_BASE, 10),
    "negrita":   (FUENTE_BASE, 10, "bold"),
    "pequena":   (FUENTE_BASE, 9),
    "boton":     (FUENTE_BASE, 10, "bold"),
}

# ---------------------------------------------------------------
# 3. MÁRGENES Y TAMAÑOS
# ---------------------------------------------------------------
MARGEN = 10          # padx / pady estándar
MARGEN_GRANDE = 20
ANCHO_BOTON = 18     # en caracteres
ALTO_FILA_TABLA = 26

# ---------------------------------------------------------------
# 4. ESTADOS -> COLOR  (mesas, órdenes de compra, pedidos, stock)
# ---------------------------------------------------------------
ESTADOS = {
    # Órdenes de compra (T58)
    "pendiente":  "advertencia",
    "solicitada": "info",
    "recibida":   "exito",
    # Mesas (T52)
    "libre":      "exito",
    "ocupada":    "peligro",
    # Inventario (T57)
    "ok":         "exito",
    "minimo":     "advertencia",
    "bajo":       "peligro",
}


def color_estado(estado):
    """Regresa el color fuerte de un estado (texto, insignias)."""
    clave = ESTADOS.get(str(estado).strip().lower(), "secundario")
    return COLORES[clave]


def tag_estado(estado):
    """Nombre de tag de Treeview para un estado (ej. 'Pendiente' -> 'est_advertencia')."""
    return "est_" + ESTADOS.get(str(estado).strip().lower(), "normal")


def nivel_stock(existencia, minimo):
    """
    Clasifica un insumo SIN cambiar cantidades (para T57).
    'bajo'   -> existencia < mínimo
    'minimo' -> existencia == mínimo
    'ok'     -> existencia > mínimo
    """
    try:
        existencia = float(existencia)
        minimo = float(minimo)
    except (TypeError, ValueError):
        return "ok"   # si falta el dato no se genera alerta falsa
    if existencia < minimo:
        return "bajo"
    if existencia == minimo:
        return "minimo"
    return "ok"


# ---------------------------------------------------------------
# 5. APLICAR ESTILOS (llamar una vez por ventana raíz)
# ---------------------------------------------------------------
def aplicar_estilos(raiz):
    """Configura los estilos ttk del equipo. Seguro de llamar varias veces."""
    raiz.configure(bg=COLORES["fondo"])
    estilo = ttk.Style(raiz)
    try:
        estilo.theme_use("clam")   # tema que sí respeta colores en Windows
    except tk.TclError:
        pass

    estilo.configure(".", font=FUENTES["normal"], background=COLORES["fondo"],
                     foreground=COLORES["texto"])
    estilo.configure("TFrame", background=COLORES["fondo"])
    estilo.configure("Panel.TFrame", background=COLORES["panel"],
                     relief="solid", borderwidth=1)
    estilo.configure("TLabel", background=COLORES["fondo"], foreground=COLORES["texto"])
    estilo.configure("Titulo.TLabel", font=FUENTES["titulo"], foreground=COLORES["primario"])
    estilo.configure("Subtitulo.TLabel", font=FUENTES["subtitulo"], foreground=COLORES["primario"])

    # Tablas
    estilo.configure("Treeview", rowheight=ALTO_FILA_TABLA, font=FUENTES["normal"],
                     background=COLORES["panel"], fieldbackground=COLORES["panel"])
    estilo.configure("Treeview.Heading", font=FUENTES["negrita"],
                     background=COLORES["primario"], foreground=COLORES["texto_claro"])
    estilo.map("Treeview.Heading", background=[("active", COLORES["primario_hover"])])
    estilo.map("Treeview", background=[("selected", COLORES["info"])],
               foreground=[("selected", COLORES["texto_claro"])])
    return estilo


# ---------------------------------------------------------------
# 6. COMPONENTES (helpers mínimos)
# ---------------------------------------------------------------
def crear_titulo(padre, texto, subtitulo=False):
    """Etiqueta de título o subtítulo con el estilo del equipo."""
    return tk.Label(padre, text=texto,
                    font=FUENTES["subtitulo" if subtitulo else "titulo"],
                    fg=COLORES["primario"], bg=_bg(padre))


def crear_etiqueta(padre, texto, negrita=False):
    return tk.Label(padre, text=texto,
                    font=FUENTES["negrita" if negrita else "normal"],
                    fg=COLORES["texto"], bg=_bg(padre))


def crear_boton(padre, texto, comando=None, tipo="primario", ancho=ANCHO_BOTON):
    """
    Botón tk.Button uniforme.
    tipo: 'primario' | 'secundario' | 'exito' | 'advertencia' | 'peligro' | 'info'
    """
    color = COLORES.get(tipo, COLORES["primario"])
    boton = tk.Button(padre, text=texto, command=comando, width=ancho,
                      font=FUENTES["boton"], bg=color, fg=COLORES["texto_claro"],
                      activebackground=COLORES["primario_hover"],
                      activeforeground=COLORES["texto_claro"],
                      relief="flat", bd=0, cursor="hand2", padx=8, pady=6)
    # Efecto hover sencillo
    boton.bind("<Enter>", lambda e: boton.config(bg=_oscurecer(color)))
    boton.bind("<Leave>", lambda e: boton.config(bg=color))
    return boton


def crear_panel(padre):
    """Frame blanco con borde, para agrupar contenido como 'tarjeta'."""
    return tk.Frame(padre, bg=COLORES["panel"], highlightthickness=1,
                    highlightbackground=COLORES["borde"], padx=MARGEN, pady=MARGEN)


def crear_insignia(padre, estado):
    """Etiqueta pequeña de color para mostrar un estado (Pendiente, Libre, Bajo...)."""
    return tk.Label(padre, text=f" {estado} ", font=FUENTES["pequena"],
                    bg=color_estado(estado), fg=COLORES["texto_claro"], padx=4)


def crear_tabla(padre, columnas, encabezados=None, anchos=None, alto=12):
    """
    Treeview con scrollbar vertical. Regresa la tabla; el contenedor se
    empaqueta con tabla.contenedor.pack(...) o .grid(...).
    """
    contenedor = tk.Frame(padre, bg=_bg(padre))
    tabla = ttk.Treeview(contenedor, columns=columnas, show="headings", height=alto)
    barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)

    encabezados = encabezados or columnas
    for i, col in enumerate(columnas):
        tabla.heading(col, text=encabezados[i])
        ancho = anchos[i] if anchos and i < len(anchos) else 120
        tabla.column(col, width=ancho, anchor="center")

    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    tabla.contenedor = contenedor
    configurar_tags_estado(tabla)
    return tabla


def configurar_tags_estado(tabla):
    """Registra los colores de fila por estado en un Treeview existente."""
    for nombre, fondo in FONDOS_FILA.items():
        tabla.tag_configure("est_" + nombre, background=fondo)
    tabla.tag_configure("est_normal", background=COLORES["panel"])


# ---------------------------------------------------------------
# Funciones internas
# ---------------------------------------------------------------
def _bg(widget):
    try:
        return widget.cget("bg")
    except tk.TclError:
        return COLORES["fondo"]


def _oscurecer(hex_color, factor=0.85):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return "#{:02X}{:02X}{:02X}".format(int(r * factor), int(g * factor), int(b * factor))


# ---------------------------------------------------------------
# 7. PRUEBA AISLADA:  py estilos_sprint4.py
#    (no toca main.py ni la base de datos)
# ---------------------------------------------------------------
if __name__ == "__main__":
    ventana = tk.Tk()
    ventana.title("Prueba de estilos · Sprint 4 (T63)")
    ventana.geometry("760x520")
    aplicar_estilos(ventana)

    crear_titulo(ventana, "Prueba de estilos del equipo").pack(pady=(MARGEN_GRANDE, 4))
    crear_etiqueta(ventana, "Ventana de demostración; no usa restaurante.db").pack()

    panel = crear_panel(ventana)
    panel.pack(fill="both", expand=True, padx=MARGEN_GRANDE, pady=MARGEN)

    crear_titulo(panel, "Insumos (datos de ejemplo)", subtitulo=True).pack(anchor="w")
    tabla = crear_tabla(panel, ("insumo", "existencia", "minimo", "estado"),
                        ("Insumo", "Existencia", "Mínimo", "Estado"),
                        anchos=(200, 110, 110, 120), alto=6)
    tabla.contenedor.pack(fill="both", expand=True, pady=MARGEN)

    ejemplo = [("Tomate", 20, 10), ("Queso", 5, 5), ("Tortilla", 2, 15)]
    nombres = {"ok": "OK", "minimo": "En mínimo", "bajo": "Bajo mínimo"}
    for insumo, exi, mini in ejemplo:
        nivel = nivel_stock(exi, mini)
        tabla.insert("", "end", values=(insumo, exi, mini, nombres[nivel]),
                     tags=(tag_estado(nivel),))

    fila = tk.Frame(panel, bg=COLORES["panel"])
    fila.pack(pady=MARGEN)
    for estado in ("Pendiente", "Solicitada", "Recibida", "Libre", "Ocupada"):
        crear_insignia(fila, estado).pack(side="left", padx=4)

    botones = tk.Frame(ventana, bg=COLORES["fondo"])
    botones.pack(pady=MARGEN)
    crear_boton(botones, "Primario", lambda: print("primario")).pack(side="left", padx=5)
    crear_boton(botones, "Secundario", None, "secundario").pack(side="left", padx=5)
    crear_boton(botones, "Éxito", None, "exito").pack(side="left", padx=5)
    crear_boton(botones, "Cerrar", ventana.destroy, "peligro").pack(side="left", padx=5)

    ventana.mainloop()
