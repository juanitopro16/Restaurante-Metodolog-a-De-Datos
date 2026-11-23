# ================================================================
# RESPONSABILIDAD / MÓDULO: Patricio Cosaín | Sprints 3–4 T56 T57 T58 | inventario, alertas y órdenes de compra
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Pantallas de Patricio Cosaín Torres.
Sprint 3: T39, T40, T42 y T43.
Sprint 4: T56 (rediseño de inventario), T57 (alertas visuales de stock bajo)
          y T58 (rediseño de órdenes de compra), usando estilos_sprint4 (T63).

Se llaman desde main.py (opción «Consultar existencias» del almacén)
sin reemplazar pantallas de otros compañeros.

Sprint 4: SOLO se cambió la presentación. Las funciones de datos de
pato_almacen.py (registrar_salida, listar_existencias, listar_bajo_minimo,
crear_orden_compra, etc.) y el esquema SQLite quedan igual.
Hecho con apoyo de IA y revisado por el autor.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from pato_almacen import (
    MOTIVOS_SALIDA, _formato, registrar_salida, listar_existencias, listar_bajo_minimo,
    listar_movimientos, listar_proveedores_activos, crear_orden_compra,
    listar_ordenes_compra, obtener_orden_compra,
)
import estilos_sprint4 as est   # T63: estilos comunes del equipo

ROLES_ALMACEN = ("almacen", "gerente")

# T57: texto que se muestra para cada nivel de stock (lo calcula est.nivel_stock)
TEXTO_NIVEL = {"ok": "OK", "minimo": "En mínimo", "bajo": "BAJO MÍNIMO"}


# ================================================================
# SPRINT 3 - TAREAS 40 Y 42  |  SPRINT 4 - TAREAS 56 Y 57
# Nombre: Pantalla de inventario (existencias + alertas)
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Pantalla principal de almacén.
#   T56: se reorganizó en tarjetas: resumen arriba, tabla de existencias con
#        columna «Estado», barra de acciones y tabla de alertas.
#   T57: cada fila se pinta según su nivel: verde (OK), naranja (en el
#        mínimo) y rojo (bajo mínimo). La tabla de alertas sigue usando
#        listar_bajo_minimo() (T42), así que «en mínimo» se avisa pero NO
#        cuenta como alerta (criterio acordado con Said). No cambia cantidades.
#   app.refrescar_existencias sigue disponible para Said (T38) y Aarón (T44).
# ================================================================
def mostrar_almacen_pato(app):
    if not app.sesion or app.sesion["rol"] not in ROLES_ALMACEN:
        messagebox.showerror("Acceso denegado", "Esta opción es exclusiva de almacén.")
        return
    app.limpiar_pantalla()
    marco = app.marco
    est.aplicar_estilos(app.ventana)
    try:
        marco.configure(bg=est.COLORES["fondo"])
    except tk.TclError:
        pass

    est.crear_titulo(marco, "Almacén · Inventario").pack(pady=(4, 2))

    # --- T56: resumen con insignias ---
    resumen = est.crear_panel(marco)
    resumen.pack(fill="x", pady=4)
    lbl_total = est.crear_etiqueta(resumen, "", negrita=True)
    lbl_total.pack(side="left", padx=est.MARGEN)
    lbl_minimo = tk.Label(resumen, font=est.FUENTES["negrita"], bg=est.COLORES["panel"],
                          fg=est.COLORES["advertencia"])
    lbl_minimo.pack(side="left", padx=est.MARGEN)
    lbl_bajo = tk.Label(resumen, font=est.FUENTES["negrita"], bg=est.COLORES["panel"],
                        fg=est.COLORES["peligro"])
    lbl_bajo.pack(side="left", padx=est.MARGEN)

    # --- T40 + T56 + T57: tabla de existencias ---
    panel_tabla = est.crear_panel(marco)
    panel_tabla.pack(fill="both", expand=True, pady=4)
    est.crear_titulo(panel_tabla, "Existencias", subtitulo=True).pack(anchor="w")
    contenedor = tk.Frame(panel_tabla, bg=est.COLORES["panel"])
    contenedor.pack(fill="both", expand=True, pady=2)
    tabla = ttk.Treeview(contenedor, columns=("existencia", "minimo", "estado"),
                         show="tree headings", height=7, selectmode="browse")
    barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.heading("#0", text="Insumo"); tabla.heading("existencia", text="Existencia")
    tabla.heading("minimo", text="Mínimo"); tabla.heading("estado", text="Estado")
    tabla.column("#0", width=200); tabla.column("existencia", width=120, anchor="center")
    tabla.column("minimo", width=120, anchor="center"); tabla.column("estado", width=120, anchor="center")
    est.configurar_tags_estado(tabla)                     # T57: colores de fila
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")

    # Leyenda de colores (T57)
    leyenda = tk.Frame(panel_tabla, bg=est.COLORES["panel"])
    leyenda.pack(anchor="w", pady=(2, 0))
    for nivel in ("ok", "minimo", "bajo"):
        tk.Label(leyenda, text=f" {TEXTO_NIVEL[nivel]} ", font=est.FUENTES["pequena"],
                 bg=est.color_estado(nivel), fg=est.COLORES["texto_claro"], padx=4
                 ).pack(side="left", padx=3)

    # --- T56: barra de acciones (mismas acciones que Sprint 3) ---
    botones = tk.Frame(marco, bg=est.COLORES["fondo"])
    botones.pack(fill="x", pady=4)
    est.crear_boton(botones, "Registrar salida", lambda: formulario_salida(app, tabla, actualizar),
                    "primario", ancho=16).pack(side="left", padx=3, expand=True, fill="x")
    est.crear_boton(botones, "Historial", lambda: ver_historial(app),
                    "secundario", ancho=12).pack(side="left", padx=3, expand=True, fill="x")
    est.crear_boton(botones, "Actualizar", lambda: actualizar(),
                    "info", ancho=12).pack(side="left", padx=3, expand=True, fill="x")
    est.crear_boton(botones, "Órdenes de compra", lambda: mostrar_ordenes_compra(app),
                    "exito", ancho=16).pack(side="left", padx=3, expand=True, fill="x")

    # --- T42 + T57: alertas bajo mínimo ---
    panel_alertas = est.crear_panel(marco)
    panel_alertas.pack(fill="x", pady=4)
    tk.Label(panel_alertas, text="⚠ Ingredientes bajo mínimo", font=est.FUENTES["subtitulo"],
             fg=est.COLORES["peligro"], bg=est.COLORES["panel"]).pack(anchor="w")
    alertas = ttk.Treeview(panel_alertas, columns=("existencia", "minimo", "faltante"),
                           show="tree headings", height=4)
    alertas.heading("#0", text="Insumo"); alertas.heading("existencia", text="Existencia")
    alertas.heading("minimo", text="Mínimo"); alertas.heading("faltante", text="Falta")
    alertas.column("#0", width=170)
    for col in ("existencia", "minimo", "faltante"):
        alertas.column(col, width=113, anchor="center")
    est.configurar_tags_estado(alertas)
    alertas.pack(fill="x", pady=2)
    aviso = tk.StringVar()
    tk.Label(panel_alertas, textvariable=aviso, wraplength=560, font=est.FUENTES["pequena"],
             bg=est.COLORES["panel"], fg=est.COLORES["texto"]).pack(anchor="w")

    def actualizar():
        # T40: siempre consulta SQLite, nunca variables guardadas en memoria.
        for fila in tabla.get_children(): tabla.delete(fila)
        for fila in alertas.get_children(): alertas.delete(fila)
        bajos = listar_bajo_minimo()
        existencias = listar_existencias()
        en_minimo = 0
        for insumo_id, nombre, existencia, unidad, minimo in existencias:
            nivel = est.nivel_stock(existencia, minimo)     # T57: solo lee, no modifica
            if nivel == "minimo":
                en_minimo += 1
            tabla.insert("", "end", iid=str(insumo_id), text=nombre,
                         values=(f"{_formato(existencia)} {unidad}", f"{_formato(minimo)} {unidad}",
                                 TEXTO_NIVEL[nivel]),
                         tags=(est.tag_estado(nivel),))
        for insumo_id, nombre, existencia, minimo, unidad, faltante in bajos:
            alertas.insert("", "end", text=nombre, values=(
                f"{_formato(existencia)} {unidad}", f"{_formato(minimo)} {unidad}",
                f"{_formato(faltante)} {unidad}"), tags=(est.tag_estado("bajo"),))

        lbl_total.config(text=f"Insumos: {len(existencias)}")
        lbl_minimo.config(text=f"En mínimo: {en_minimo}")
        lbl_bajo.config(text=f"Bajo mínimo: {len(bajos)}")
        if not existencias:
            aviso.set("No hay insumos registrados (los registra Said en T35/T36).")
        elif not bajos:
            aviso.set("Todo en orden: ningún insumo está por debajo de su mínimo.")
        else:
            aviso.set("Crea una orden de compra para los insumos en rojo.")

    app.refrescar_existencias = actualizar  # Gancho para T38 (Said) y T44 (Aarón).

    est.crear_boton(marco, "Volver al menú", app.mostrar_menu, "secundario").pack(fill="x", pady=4)
    actualizar()


# ================================================================
# SPRINT 3 - TAREA 39  (Sprint 4: solo estilos)
# Nombre: Registrar salidas por uso o desperdicio
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Formulario: insumo, cantidad y motivo. Al guardar llama a
#            registrar_salida() y refresca existencias y alertas (T40/T42).
# ================================================================
def formulario_salida(app, tabla, al_guardar):
    insumos = listar_existencias()
    if not insumos:
        messagebox.showinfo("Salidas", "No hay insumos registrados.")
        return
    w = tk.Toplevel(app.ventana); w.title("Registrar salida"); w.geometry("380x310")
    w.configure(bg=est.COLORES["fondo"])
    f = est.crear_panel(w); f.pack(fill="both", expand=True, padx=est.MARGEN, pady=est.MARGEN)
    est.crear_titulo(f, "Registrar salida", subtitulo=True).pack(anchor="w", pady=(0, 4))
    est.crear_etiqueta(f, "Insumo").pack(anchor="w")
    cb = ttk.Combobox(f, state="readonly", values=[
        f"{n} (hay {_formato(e)} {u})" for _, n, e, u, _ in insumos])
    cb.pack(fill="x", pady=3)
    # Si había un insumo seleccionado en la tabla, se elige ese mismo.
    seleccion = tabla.selection()
    ids = [str(i[0]) for i in insumos]
    cb.current(ids.index(seleccion[0]) if seleccion and seleccion[0] in ids else 0)
    unidad = est.crear_etiqueta(f, "")
    est.crear_etiqueta(f, "Cantidad que sale").pack(anchor="w")
    cantidad = tk.Entry(f, font=est.FUENTES["normal"]); cantidad.pack(fill="x", pady=3)
    unidad.pack(anchor="w")
    def mostrar_unidad(event=None):
        unidad.config(text=f"Unidad: {insumos[cb.current()][3]}")
    cb.bind("<<ComboboxSelected>>", mostrar_unidad); mostrar_unidad()
    est.crear_etiqueta(f, "Motivo").pack(anchor="w")
    motivo = ttk.Combobox(f, state="readonly", values=list(MOTIVOS_SALIDA))
    motivo.pack(fill="x", pady=3); motivo.current(0)

    def guardar():
        ok, msg = registrar_salida(insumos[cb.current()][0], cantidad.get(), motivo.get())
        if ok:
            messagebox.showinfo("Salida", msg, parent=w)
            w.destroy()
            al_guardar()  # T40: el saldo nuevo aparece sin reiniciar.
        else:
            messagebox.showwarning("Salida", msg, parent=w)
    est.crear_boton(f, "Guardar salida", guardar, "exito").pack(fill="x", pady=8)
    cantidad.focus_set()


def ver_historial(app):
    """Evidencia de T39: muestra los últimos movimientos con su motivo."""
    w = tk.Toplevel(app.ventana); w.title("Historial de movimientos"); w.geometry("640x380")
    w.configure(bg=est.COLORES["fondo"])
    est.crear_titulo(w, "Historial de movimientos", subtitulo=True).pack(anchor="w", padx=10, pady=(8, 0))
    tabla = ttk.Treeview(w, columns=("tipo", "cantidad", "motivo", "fecha"), show="tree headings")
    tabla.heading("#0", text="Insumo"); tabla.heading("tipo", text="Tipo")
    tabla.heading("cantidad", text="Cantidad"); tabla.heading("motivo", text="Motivo")
    tabla.heading("fecha", text="Fecha")
    tabla.column("#0", width=140); tabla.column("tipo", width=70, anchor="center")
    tabla.column("cantidad", width=90, anchor="center")
    tabla.column("motivo", width=110, anchor="center"); tabla.column("fecha", width=150, anchor="center")
    # Entradas en verde y salidas en naranja para leerlas más rápido.
    tabla.tag_configure("Entrada", background=est.FONDOS_FILA["exito"])
    tabla.tag_configure("Salida", background=est.FONDOS_FILA["advertencia"])
    tabla.pack(fill="both", expand=True, padx=10, pady=10)
    movimientos = listar_movimientos()
    for _, nombre, tipo, cant, unidad, motivo, fecha in movimientos:
        tabla.insert("", "end", text=nombre, values=(tipo, f"{_formato(cant)} {unidad}", motivo or "—", fecha),
                     tags=(tipo,))
    if not movimientos:
        est.crear_etiqueta(w, "Todavía no hay movimientos.").pack()
    est.crear_boton(w, "Cerrar", w.destroy, "secundario").pack(fill="x", padx=10, pady=5)


# ================================================================
# SPRINT 3 - TAREA 43  |  SPRINT 4 - TAREA 58
# Nombre: Órdenes de compra
# Responsable: Patricio Cosaín Torres
# ¿QUÉ HACE? Crear órdenes (proveedor de Javier T41 + varios insumos) y
#            consultar las guardadas.
#   T58: la ventana se dividió en dos columnas: «Nueva orden» y «Órdenes
#        guardadas». Cada orden se pinta por estado (Pendiente naranja,
#        Solicitada azul, Recibida verde), hay filtro por estado y contador.
#   NO se cambió la transición Pendiente→Solicitada→Recibida ni se suman
#   existencias aquí: crear la orden no toca el inventario; recibirla es
#   T44 de Aarón. Así no se puede sumar dos veces desde esta pantalla.
# ================================================================
def mostrar_ordenes_compra(app):
    proveedores = listar_proveedores_activos()
    insumos = listar_existencias()
    w = tk.Toplevel(app.ventana); w.title("Órdenes de compra"); w.geometry("980x560")
    est.aplicar_estilos(w)
    est.crear_titulo(w, "Órdenes de compra").pack(pady=(est.MARGEN, 4))

    cuerpo = tk.Frame(w, bg=est.COLORES["fondo"])
    cuerpo.pack(fill="both", expand=True, padx=est.MARGEN, pady=4)
    cuerpo.columnconfigure(0, weight=1); cuerpo.columnconfigure(1, weight=2)
    cuerpo.rowconfigure(0, weight=1)

    # ---------------- Columna izquierda: nueva orden ----------------
    f = est.crear_panel(cuerpo)
    f.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
    est.crear_titulo(f, "Nueva orden", subtitulo=True).pack(anchor="w")

    est.crear_etiqueta(f, "Proveedor").pack(anchor="w")
    cb_prov = ttk.Combobox(f, state="readonly", values=[f"{p[0]} - {p[1]}" for p in proveedores])
    cb_prov.pack(fill="x", pady=2)
    if not proveedores:
        tk.Label(f, text="No hay proveedores. Regístralos en «Administrar proveedores» (T41).",
                 fg=est.COLORES["peligro"], bg=est.COLORES["panel"], wraplength=280,
                 justify="left").pack(anchor="w")

    est.crear_etiqueta(f, "Ingrediente").pack(anchor="w")
    cb_ins = ttk.Combobox(f, state="readonly", values=[f"{i[1]} ({i[3]})" for i in insumos])
    cb_ins.pack(fill="x", pady=2)
    if insumos: cb_ins.current(0)
    est.crear_etiqueta(f, "Cantidad a pedir").pack(anchor="w")
    cantidad = tk.Entry(f, font=est.FUENTES["normal"]); cantidad.pack(fill="x", pady=2)

    renglones = []  # Lista temporal de (insumo_id, nombre, unidad, cantidad_texto).
    lista = tk.Listbox(f, height=6, exportselection=False, font=est.FUENTES["normal"])

    def redibujar():
        lista.delete(0, tk.END)
        for _, nombre, unidad, cant in renglones:
            lista.insert(tk.END, f"{cant} {unidad} de {nombre}")

    def agregar():
        if not insumos:
            messagebox.showwarning("Orden", "No hay ingredientes registrados.", parent=w); return
        texto = cantidad.get().strip()
        try:
            if float(texto.replace(",", ".")) <= 0: raise ValueError
        except ValueError:
            messagebox.showwarning("Orden", "La cantidad debe ser un número mayor que cero.", parent=w); return
        i = insumos[cb_ins.current()]
        renglones.append((i[0], i[1], i[3], texto))
        cantidad.delete(0, tk.END); redibujar()

    def quitar():
        sel = lista.curselection()
        if not sel:
            messagebox.showwarning("Orden", "Selecciona un renglón de la lista.", parent=w); return
        renglones.pop(sel[0]); redibujar()

    def guardar():
        proveedor_id = proveedores[cb_prov.current()][0] if cb_prov.current() >= 0 else None
        ok, msg, folio = crear_orden_compra(proveedor_id, [(r[0], r[3]) for r in renglones])
        if ok:
            messagebox.showinfo("Orden de compra", msg, parent=w)
            renglones.clear(); redibujar(); refrescar_ordenes()
        else:
            messagebox.showwarning("Orden de compra", msg, parent=w)

    est.crear_boton(f, "Agregar ingrediente", agregar, "info").pack(fill="x", pady=3)
    est.crear_etiqueta(f, "Ingredientes de esta orden:").pack(anchor="w")
    lista.pack(fill="x", pady=2)
    est.crear_boton(f, "Quitar renglón", quitar, "peligro").pack(fill="x", pady=2)
    est.crear_boton(f, "Guardar orden de compra", guardar, "exito").pack(fill="x", pady=(6, 2))

    # ---------------- Columna derecha: órdenes guardadas ----------------
    d = est.crear_panel(cuerpo)
    d.grid(row=0, column=1, sticky="nsew")
    encabezado = tk.Frame(d, bg=est.COLORES["panel"]); encabezado.pack(fill="x")
    est.crear_titulo(encabezado, "Órdenes guardadas", subtitulo=True).pack(side="left")
    filtro = ttk.Combobox(encabezado, state="readonly", width=12,
                          values=["Todas", "Pendiente", "Solicitada", "Recibida"])
    filtro.current(0); filtro.pack(side="right")
    est.crear_etiqueta(encabezado, "Filtrar:").pack(side="right", padx=4)

    contenedor = tk.Frame(d, bg=est.COLORES["panel"]); contenedor.pack(fill="both", expand=True, pady=4)
    tabla = ttk.Treeview(contenedor, columns=("proveedor", "fecha", "renglones", "estado"),
                         show="tree headings", height=12, selectmode="browse")
    barra = ttk.Scrollbar(contenedor, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.heading("#0", text="Folio"); tabla.heading("proveedor", text="Proveedor")
    tabla.heading("fecha", text="Fecha"); tabla.heading("renglones", text="Insumos")
    tabla.heading("estado", text="Estado")
    tabla.column("#0", width=60, anchor="center"); tabla.column("proveedor", width=160)
    tabla.column("fecha", width=150, anchor="center"); tabla.column("renglones", width=70, anchor="center")
    tabla.column("estado", width=100, anchor="center")
    est.configurar_tags_estado(tabla)                       # T58: color por estado
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")

    leyenda = tk.Frame(d, bg=est.COLORES["panel"]); leyenda.pack(anchor="w")
    for estado in ("Pendiente", "Solicitada", "Recibida"):
        est.crear_insignia(leyenda, estado).pack(side="left", padx=3)
    contador = tk.StringVar()
    tk.Label(d, textvariable=contador, font=est.FUENTES["pequena"], bg=est.COLORES["panel"],
             fg=est.COLORES["texto"]).pack(anchor="w", pady=(4, 0))

    def refrescar_ordenes(event=None):
        for fila in tabla.get_children(): tabla.delete(fila)
        ordenes = listar_ordenes_compra()
        elegido = filtro.get()
        conteo = {"Pendiente": 0, "Solicitada": 0, "Recibida": 0}
        for folio, proveedor, fecha, estado, num_renglones in ordenes:
            if estado in conteo:
                conteo[estado] += 1
            if elegido != "Todas" and estado != elegido:
                continue
            tabla.insert("", "end", iid=str(folio), text=f"#{folio}",
                         values=(proveedor, fecha, num_renglones, estado),
                         tags=(est.tag_estado(estado),))
        contador.set(f"Total: {len(ordenes)}  |  Pendientes: {conteo['Pendiente']}  |  "
                     f"Solicitadas: {conteo['Solicitada']}  |  Recibidas: {conteo['Recibida']}")

    filtro.bind("<<ComboboxSelected>>", refrescar_ordenes)

    def ver_orden(event=None):
        sel = tabla.selection()
        if not sel:
            messagebox.showinfo("Orden", "Selecciona una orden guardada.", parent=w); return
        cabecera, detalle = obtener_orden_compra(int(sel[0]))
        if cabecera is None:
            messagebox.showwarning("Orden", "Esa orden ya no existe.", parent=w); return
        folio, proveedor, fecha, estado = cabecera
        texto = [f"Orden #{folio}", f"Proveedor: {proveedor}", f"Fecha: {fecha}", f"Estado: {estado}", ""]
        texto += [f"• {_formato(cant)} {unidad} de {nombre}" for nombre, cant, unidad in detalle]
        messagebox.showinfo(f"Orden #{folio}", "\n".join(texto), parent=w)

    tabla.bind("<Double-1>", ver_orden)
    acciones = tk.Frame(d, bg=est.COLORES["panel"]); acciones.pack(fill="x", pady=4)
    est.crear_boton(acciones, "Ver orden", ver_orden, "primario", ancho=12).pack(side="left", padx=3)
    est.crear_boton(acciones, "Actualizar", refrescar_ordenes, "info", ancho=12).pack(side="left", padx=3)
    est.crear_boton(acciones, "Cerrar", w.destroy, "secundario", ancho=12).pack(side="right", padx=3)
    refrescar_ordenes()
