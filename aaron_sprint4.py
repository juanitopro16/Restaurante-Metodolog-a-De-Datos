# ================================================================
# RESPONSABILIDAD / MÓDULO: Aarón Mendoza | Sprint 4 T48 T59 T60 T61 | historial, editor de pedido, cocina y tiempos
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
# ================================================================
# SPRINT 4 - Aarón Mendoza Rodríguez
# Tareas: T48 (historial de pedidos y pagos), T59 (pantalla de pedidos),
#         T60 (comandas de cocina por tarjetas) y T61 (tiempo de espera).
#
# Este archivo es NUEVO: no reemplaza ni modifica base_datos.py,
# sprint3_nuevo.py ni javier_caja_proveedores.py. Solo los USA.
# Los pocos cambios que hacen falta en main.py están en CAMBIOS_AARON.txt.
#
# AUTORÍA: código escrito con ayuda de IA (Claude) y asignado a Aarón
# Mendoza Rodríguez. Debe revisarse y probarse antes de integrarse.
# ================================================================
from datetime import datetime

from base_datos import (
    conectar,
    listar_productos,
    listar_detalle_pedido,
    agregar_producto_pedido,
    modificar_detalle_pedido,
    quitar_producto_pedido,
    marcar_pedido_en_preparacion,
)
from sprint3_nuevo import marcar_listo

ESTADOS_COCINA = ("Pendiente", "En preparación", "Listo")
UMBRAL_ALERTA_MIN = 15      # a partir de cuántos minutos se resalta la espera
INTERVALO_REFRESCO_MS = 30000  # la pantalla de cocina se actualiza cada 30 s


# ================================================================
# T61 - Marca de tiempo del envío a cocina (migración pequeña)
# ================================================================
def asegurar_columna_envio():
    """Agrega pedidos.fecha_hora_envio si todavía no existe.

    Es una migración compatible: solo añade una columna, no borra ni
    cambia datos. Se puede ejecutar muchas veces. Los pedidos que ya se
    habían enviado antes quedan con NULL (sin dato) y se muestran con '—'.
    """
    c = conectar()
    try:
        columnas = [f[1] for f in c.execute("PRAGMA table_info(pedidos)")]
        if "fecha_hora_envio" not in columnas:
            c.execute("ALTER TABLE pedidos ADD COLUMN fecha_hora_envio TEXT")
            c.commit()
    finally:
        c.close()


def enviar_pedido_cocina_t61(pedido_id):
    """Igual que enviar_pedido_cocina (T21) pero guarda la hora del envío.

    Mantiene las mismas reglas: solo Borrador, no vacío, una sola vez.
    El cambio de estado y la hora se guardan en una sola sentencia, así
    que no puede quedar un pedido Pendiente sin su hora de envío.
    Devuelve (correcto, mensaje).
    """
    asegurar_columna_envio()
    c = conectar()
    try:
        with c:
            fila = c.execute("SELECT estado FROM pedidos WHERE id=?",
                             (pedido_id,)).fetchone()
            if fila is None:
                return False, "El pedido no existe."
            if fila[0] != "Borrador":
                return False, (f"Este pedido ya no está en borrador "
                               f"(estado actual: {fila[0]}).")
            total = c.execute("SELECT COUNT(*) FROM detalle_pedido WHERE pedido_id=?",
                              (pedido_id,)).fetchone()[0]
            if total == 0:
                return False, ("El pedido está vacío. Agrega al menos un "
                               "producto antes de enviarlo.")
            cambio = c.execute(
                """UPDATE pedidos
                   SET estado='Pendiente', fecha_hora_envio=datetime('now','localtime')
                   WHERE id=? AND estado='Borrador'""", (pedido_id,))
            if cambio.rowcount != 1:
                return False, "El pedido ya fue enviado."
        return True, "Pedido enviado a cocina. Estado: Pendiente."
    finally:
        c.close()


def minutos_transcurridos(fecha_hora_envio, ahora=None):
    """Minutos enteros desde el envío a cocina; None si no hay fecha válida."""
    if not fecha_hora_envio:
        return None
    try:
        inicio = datetime.strptime(str(fecha_hora_envio)[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    ahora = ahora or datetime.now()
    return max(0, int((ahora - inicio).total_seconds() // 60))


# ================================================================
# T60 / T61 - Datos de las comandas de cocina
# ================================================================
def listar_comandas_cocina(ahora=None):
    """Comandas Pendiente / En preparación / Listo, de la más antigua a la más nueva.

    Cada comanda es un diccionario:
      folio, mesa, estado, fecha_hora_envio, minutos (None si no hay dato),
      productos = [(cantidad, nombre, nota), ...]
    """
    asegurar_columna_envio()
    c = conectar()
    try:
        marcas = ",".join("?" * len(ESTADOS_COCINA))
        filas = c.execute(
            f"""SELECT p.id, m.numero, p.estado, p.fecha_hora_envio
                FROM pedidos p JOIN mesas m ON m.id = p.mesa_id
                WHERE p.estado IN ({marcas})
                ORDER BY (p.fecha_hora_envio IS NULL), p.fecha_hora_envio, p.id""",
            ESTADOS_COCINA).fetchall()
        comandas = []
        for folio, mesa, estado, envio in filas:
            productos = c.execute(
                """SELECT dp.cantidad, pr.nombre, COALESCE(dp.notas, '')
                   FROM detalle_pedido dp JOIN productos pr ON pr.id = dp.producto_id
                   WHERE dp.pedido_id=? ORDER BY dp.id""", (folio,)).fetchall()
            comandas.append({
                "folio": folio, "mesa": mesa, "estado": estado,
                "fecha_hora_envio": envio,
                "minutos": minutos_transcurridos(envio, ahora),
                "productos": productos,
            })
        return comandas
    finally:
        c.close()


# ================================================================
# T48 - Historial de pedidos y pagos realizados
# Usa las tablas que YA existen (Javier): pagos_javier,
# pago_pedidos_javier y pago_lineas_javier. No crea tablas nuevas
# ni borra nada, así que cerrar la mesa no afecta el historial.
# ================================================================
def listar_historial_pedidos(limite=200):
    """Pedidos cobrados, del más reciente al más antiguo.

    Cada fila es un diccionario: folio, mesa, estado, fecha_pedido,
    pago_id, metodo, total_pago, fecha_pago.
    OJO: 'total_pago' es el total del PAGO completo; si un mismo cobro
    incluyó varios pedidos de la mesa, el total es el de todos juntos.
    """
    c = conectar()
    try:
        filas = c.execute(
            """SELECT pe.id, m.numero, pe.estado, pe.fecha,
                      pg.id, pg.metodo, pg.total, pg.fecha
               FROM pedidos pe
               JOIN mesas m ON m.id = pe.mesa_id
               JOIN pago_pedidos_javier pp ON pp.pedido_id = pe.id
               JOIN pagos_javier pg ON pg.id = pp.pago_id
               ORDER BY pg.fecha DESC, pe.id DESC
               LIMIT ?""", (int(limite),)).fetchall()
        return [{"folio": f[0], "mesa": f[1], "estado": f[2], "fecha_pedido": f[3],
                 "pago_id": f[4], "metodo": f[5], "total_pago": f[6],
                 "fecha_pago": f[7]} for f in filas]
    finally:
        c.close()


def obtener_historial_pedido(pedido_id):
    """Detalle de un pedido cobrado, o None si no existe o no tiene pago.

    Devuelve: folio, mesa, estado, fecha_pedido, fecha_hora_envio,
    productos_pedido = [(cantidad, nombre, nota)], pago (dict con id, metodo,
    total, recibido, cambio, fecha), pedidos_del_pago = [folios] y
    lineas_pago = [(producto, cantidad, precio_unitario, importe)].
    'lineas_pago' es la copia que se guardó al cobrar: NO cambia aunque
    después se edite el nombre o el precio del producto en el catálogo.
    """
    asegurar_columna_envio()
    c = conectar()
    try:
        cab = c.execute(
            """SELECT pe.id, m.numero, pe.estado, pe.fecha, pe.fecha_hora_envio,
                      pg.id, pg.metodo, pg.total, pg.recibido, pg.cambio, pg.fecha
               FROM pedidos pe
               JOIN mesas m ON m.id = pe.mesa_id
               JOIN pago_pedidos_javier pp ON pp.pedido_id = pe.id
               JOIN pagos_javier pg ON pg.id = pp.pago_id
               WHERE pe.id=?""", (pedido_id,)).fetchone()
        if cab is None:
            return None
        productos = c.execute(
            """SELECT dp.cantidad, pr.nombre, COALESCE(dp.notas, '')
               FROM detalle_pedido dp JOIN productos pr ON pr.id = dp.producto_id
               WHERE dp.pedido_id=? ORDER BY dp.id""", (pedido_id,)).fetchall()
        lineas = c.execute(
            """SELECT producto, cantidad, precio_unitario, importe
               FROM pago_lineas_javier WHERE pago_id=? ORDER BY id""",
            (cab[5],)).fetchall()
        del_pago = [x[0] for x in c.execute(
            "SELECT pedido_id FROM pago_pedidos_javier WHERE pago_id=? ORDER BY pedido_id",
            (cab[5],))]
        return {
            "folio": cab[0], "mesa": cab[1], "estado": cab[2],
            "fecha_pedido": cab[3], "fecha_hora_envio": cab[4],
            "productos_pedido": productos,
            "pago": {"id": cab[5], "metodo": cab[6], "total": cab[7],
                     "recibido": cab[8], "cambio": cab[9], "fecha": cab[10]},
            "pedidos_del_pago": del_pago,
            "lineas_pago": lineas,
        }
    finally:
        c.close()


# ================================================================
# Utilidades de pantalla
# ================================================================
def _dinero(valor):
    return f"${float(valor):,.2f}"


def _info_pedido(pedido_id):
    """(estado, número de mesa) del pedido, o (None, None)."""
    c = conectar()
    try:
        fila = c.execute(
            """SELECT pe.estado, m.numero FROM pedidos pe
               JOIN mesas m ON m.id = pe.mesa_id WHERE pe.id=?""",
            (pedido_id,)).fetchone()
        return (None, None) if fila is None else (fila[0], fila[1])
    finally:
        c.close()


# ================================================================
# T59 - Pantalla rediseñada para crear y editar pedidos
# Conserva la lógica: Borrador -> (agregar / modificar / quitar) -> enviar.
# Las reglas (no editar pedidos enviados) siguen validándose en
# base_datos.py; aquí además se bloquean los botones.
# ================================================================
def formulario_pedido_rediseno(app, pedido_id):
    import tkinter as tk
    from tkinter import ttk, messagebox

    if not app.sesion or app.sesion["rol"] != "mesero":
        messagebox.showerror("Acceso denegado", "Esta pantalla es exclusiva del mesero.")
        return
    estado_pedido, mesa = _info_pedido(pedido_id)
    if estado_pedido is None:
        messagebox.showerror("Pedido", "El pedido no existe.")
        return

    w = tk.Toplevel(app.ventana)
    w.title(f"Pedido #{pedido_id}")
    w.geometry("900x600")
    w.minsize(820, 520)
    raiz = tk.Frame(w, padx=14, pady=10)
    raiz.pack(fill="both", expand=True)

    # ----- Encabezado -----
    enc = tk.Frame(raiz)
    enc.pack(fill="x")
    tk.Label(enc, text=f"Pedido #{pedido_id}  ·  Mesa {mesa}",
             font=("Arial", 15, "bold")).pack(side="left")
    etiqueta_estado = tk.Label(enc, text="", font=("Arial", 10, "bold"), padx=8)
    etiqueta_estado.pack(side="right")

    cuerpo = tk.Frame(raiz)
    cuerpo.pack(fill="both", expand=True, pady=8)
    cuerpo.columnconfigure(0, weight=1)
    cuerpo.columnconfigure(1, weight=1)
    cuerpo.rowconfigure(0, weight=1)

    # ----- Izquierda: menú de productos -----
    izq = tk.LabelFrame(cuerpo, text=" Menú ", padx=8, pady=6)
    izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
    tk.Label(izq, text="Buscar producto").pack(anchor="w")
    busqueda = tk.Entry(izq)
    busqueda.pack(fill="x", pady=(0, 4))
    tabla_menu = ttk.Treeview(izq, columns=("categoria", "precio"),
                              show="tree headings", height=10, selectmode="browse")
    tabla_menu.heading("#0", text="Producto")
    tabla_menu.heading("categoria", text="Categoría")
    tabla_menu.heading("precio", text="Precio")
    tabla_menu.column("#0", width=170)
    tabla_menu.column("categoria", width=90)
    tabla_menu.column("precio", width=70, anchor="e")
    tabla_menu.pack(fill="both", expand=True)

    fila_cant = tk.Frame(izq)
    fila_cant.pack(fill="x", pady=(6, 0))
    tk.Label(fila_cant, text="Cantidad").pack(side="left")
    cantidad = tk.Spinbox(fila_cant, from_=1, to=99, width=5)
    cantidad.pack(side="left", padx=6)
    tk.Label(izq, text="Nota opcional (ej. sin cebolla)").pack(anchor="w", pady=(6, 0))
    nota = tk.Entry(izq)
    nota.pack(fill="x")
    boton_agregar = tk.Button(izq, text="Agregar al pedido", bg="#2B6CB0", fg="white")
    boton_agregar.pack(fill="x", pady=(8, 0))

    # ----- Derecha: productos del pedido -----
    der = tk.LabelFrame(cuerpo, text=" Productos del pedido ", padx=8, pady=6)
    der.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
    tabla_ped = ttk.Treeview(der, columns=("cant", "nota", "subtotal"),
                             show="tree headings", height=10, selectmode="browse")
    tabla_ped.heading("#0", text="Producto")
    tabla_ped.heading("cant", text="Cant.")
    tabla_ped.heading("nota", text="Nota")
    tabla_ped.heading("subtotal", text="Subtotal")
    tabla_ped.column("#0", width=150)
    tabla_ped.column("cant", width=45, anchor="center")
    tabla_ped.column("nota", width=110)
    tabla_ped.column("subtotal", width=75, anchor="e")
    tabla_ped.pack(fill="both", expand=True)
    total_var = tk.StringVar(value="Total: $0.00")
    tk.Label(der, textvariable=total_var, font=("Arial", 12, "bold"),
             anchor="e").pack(fill="x", pady=(4, 0))

    fila_edit = tk.Frame(der)
    fila_edit.pack(fill="x", pady=(6, 0))
    tk.Label(fila_edit, text="Cantidad").pack(side="left")
    nueva_cantidad = tk.Spinbox(fila_edit, from_=1, to=99, width=5)
    nueva_cantidad.pack(side="left", padx=6)
    tk.Label(fila_edit, text="Nota").pack(side="left")
    nueva_nota = tk.Entry(fila_edit)
    nueva_nota.pack(side="left", fill="x", expand=True, padx=6)
    fila_btn = tk.Frame(der)
    fila_btn.pack(fill="x", pady=(6, 0))
    boton_guardar = tk.Button(fila_btn, text="Guardar cambios")
    boton_guardar.pack(side="left", expand=True, fill="x", padx=(0, 3))
    boton_quitar = tk.Button(fila_btn, text="Quitar producto")
    boton_quitar.pack(side="left", expand=True, fill="x", padx=(3, 0))

    # ----- Pie -----
    pie = tk.Frame(raiz)
    pie.pack(fill="x")
    boton_enviar = tk.Button(pie, text="Confirmar y enviar a cocina",
                             bg="#2F855A", fg="white", font=("Arial", 10, "bold"))
    boton_enviar.pack(side="left", fill="x", expand=True, padx=(0, 4))
    tk.Button(pie, text="Cerrar", command=w.destroy).pack(side="left", fill="x",
                                                          expand=True, padx=(4, 0))

    productos = {}   # iid del menú -> fila de producto

    def poner_estado_botones():
        editable = _info_pedido(pedido_id)[0] == "Borrador"
        etiqueta_estado.config(
            text="Borrador (editable)" if editable else "Enviado: solo lectura",
            bg="#C6F6D5" if editable else "#FED7D7")
        modo = "normal" if editable else "disabled"
        for b in (boton_agregar, boton_guardar, boton_quitar, boton_enviar):
            b.config(state=modo)

    def llenar_menu(event=None):
        texto = busqueda.get().strip().lower()
        for fila in tabla_menu.get_children():
            tabla_menu.delete(fila)
        productos.clear()
        for p in listar_productos(solo_disponibles=True):
            if texto and texto not in p[1].lower() and texto not in p[2].lower():
                continue
            iid = str(p[0])
            productos[iid] = p
            tabla_menu.insert("", "end", iid=iid, text=p[1],
                              values=(p[2], _dinero(p[4])))

    def refrescar():
        for fila in tabla_ped.get_children():
            tabla_ped.delete(fila)
        total = 0.0
        for det_id, nombre, cant, precio, nota_txt in listar_detalle_pedido(pedido_id):
            subtotal = cant * precio
            total += subtotal
            tabla_ped.insert("", "end", iid=str(det_id), text=nombre,
                             values=(cant, nota_txt, _dinero(subtotal)))
        total_var.set(f"Total: {_dinero(total)}")
        nueva_cantidad.delete(0, tk.END)
        nueva_cantidad.insert(0, "1")
        nueva_nota.delete(0, tk.END)
        poner_estado_botones()

    def avisar(ok, mensaje):
        if not ok:
            messagebox.showwarning("Pedido", mensaje, parent=w)

    def agregar():
        sel = tabla_menu.selection()
        if not sel:
            messagebox.showwarning("Pedido", "Selecciona un producto del menú.", parent=w)
            return
        ok, msg = agregar_producto_pedido(pedido_id, int(sel[0]), cantidad.get(), nota.get())
        avisar(ok, msg)
        if ok:
            cantidad.delete(0, tk.END)
            cantidad.insert(0, "1")
            nota.delete(0, tk.END)
        refrescar()

    def cargar_seleccion(event=None):
        sel = tabla_ped.selection()
        if not sel:
            return
        valores = tabla_ped.item(sel[0], "values")
        nueva_cantidad.delete(0, tk.END)
        nueva_cantidad.insert(0, str(valores[0]))
        nueva_nota.delete(0, tk.END)
        nueva_nota.insert(0, valores[1])

    def guardar_cambios():
        sel = tabla_ped.selection()
        if not sel:
            messagebox.showwarning("Pedido", "Selecciona un producto del pedido.", parent=w)
            return
        ok, msg = modificar_detalle_pedido(int(sel[0]), nueva_cantidad.get(), nueva_nota.get())
        avisar(ok, msg)
        refrescar()

    def quitar():
        sel = tabla_ped.selection()
        if not sel:
            messagebox.showwarning("Pedido", "Selecciona un producto del pedido.", parent=w)
            return
        if not messagebox.askyesno("Quitar producto",
                                   "¿Quitar este producto del pedido?", parent=w):
            return
        ok, msg = quitar_producto_pedido(int(sel[0]))
        avisar(ok, msg)
        refrescar()

    def enviar():
        if not messagebox.askyesno(
                "Enviar a cocina",
                f"¿Enviar el pedido #{pedido_id} a cocina? Después ya no podrás modificarlo.",
                parent=w):
            return
        ok, msg = enviar_pedido_cocina_t61(pedido_id)
        if ok:
            messagebox.showinfo("Pedido", msg, parent=w)
            w.destroy()
            app.mostrar_mesas()
        else:
            messagebox.showwarning("Pedido", msg, parent=w)
            refrescar()

    busqueda.bind("<KeyRelease>", llenar_menu)
    tabla_ped.bind("<<TreeviewSelect>>", cargar_seleccion)
    boton_agregar.config(command=agregar)
    boton_guardar.config(command=guardar_cambios)
    boton_quitar.config(command=quitar)
    boton_enviar.config(command=enviar)

    llenar_menu()
    refrescar()


# ================================================================
# T60 + T61 - Pantalla de cocina por tarjetas con tiempo de espera
# Transiciones que se conservan:
#   Pendiente -> En preparación : marcar_pedido_en_preparacion (base_datos.py)
#   En preparación -> Listo     : marcar_listo (sprint3_nuevo.py)
# Se actualiza sola cada 30 s y también con el botón "Actualizar".
# ================================================================
COLORES_ESTADO = {
    "Pendiente": "#FEFCBF",
    "En preparación": "#FEEBC8",
    "Listo": "#C6F6D5",
}


def mostrar_cocina_tarjetas(app):
    import tkinter as tk
    from tkinter import messagebox

    if not app.sesion or app.sesion["rol"] != "cocina":
        messagebox.showerror("Acceso denegado", "Esta pantalla es exclusiva de cocina.")
        return

    app.limpiar_pantalla()
    tk.Label(app.marco, text="Comandas de cocina",
             font=("Arial", 16, "bold")).pack(pady=(6, 2))
    barra = tk.Frame(app.marco)
    barra.pack(fill="x", padx=6)
    texto_estado = tk.StringVar(value="")
    tk.Label(barra, textvariable=texto_estado, anchor="w").pack(side="left")
    zona = tk.Frame(app.marco)
    zona.pack(fill="both", expand=True, padx=6, pady=6)
    for i in range(len(ESTADOS_COCINA)):
        zona.columnconfigure(i, weight=1, uniform="col")
    zona.rowconfigure(0, weight=1)

    interiores = {}
    for i, est in enumerate(ESTADOS_COCINA):
        columna = tk.Frame(zona, bd=1, relief="solid")
        columna.grid(row=0, column=i, sticky="nsew", padx=3)
        titulo = tk.Label(columna, text=est, font=("Arial", 11, "bold"),
                          bg=COLORES_ESTADO[est])
        titulo.pack(fill="x")
        lienzo = tk.Canvas(columna, highlightthickness=0)
        barra_v = tk.Scrollbar(columna, orient="vertical", command=lienzo.yview)
        interior = tk.Frame(lienzo)
        interior.bind("<Configure>",
                      lambda e, l=lienzo: l.configure(scrollregion=l.bbox("all")))
        ventana_interior = lienzo.create_window((0, 0), window=interior, anchor="nw")
        lienzo.bind("<Configure>",
                    lambda e, l=lienzo, v=ventana_interior: l.itemconfigure(v, width=e.width))
        lienzo.configure(yscrollcommand=barra_v.set)
        lienzo.pack(side="left", fill="both", expand=True)
        barra_v.pack(side="right", fill="y")
        interiores[est] = (interior, titulo)

    def accion(folio, estado):
        # Los permisos también se validan en la acción, no solo al abrir.
        if not app.sesion or app.sesion["rol"] != "cocina":
            messagebox.showerror("Acceso denegado", "Esta acción es exclusiva de cocina.")
            return
        if estado == "Pendiente":
            ok, msg = marcar_pedido_en_preparacion(folio)
        elif estado == "En preparación":
            ok, msg = marcar_listo(folio)
        else:
            return
        dibujar()
        texto_estado.set(msg)
        if not ok:
            messagebox.showwarning("Cocina", msg)

    def tarjeta(padre, c):
        color = COLORES_ESTADO[c["estado"]]
        t = tk.Frame(padre, bg=color, bd=1, relief="groove", padx=8, pady=6)
        t.pack(fill="x", padx=4, pady=4)
        tk.Label(t, text=f"Folio #{c['folio']}  ·  Mesa {c['mesa']}", bg=color,
                 font=("Arial", 11, "bold")).pack(anchor="w")
        if c["estado"] == "Listo":
            tk.Label(t, text="Esperando al mesero", bg=color,
                     font=("Arial", 9, "italic")).pack(anchor="w")
        elif c["minutos"] is None:
            tk.Label(t, text="Espera: — (sin hora de envío)", bg=color,
                     font=("Arial", 9)).pack(anchor="w")
        else:
            urgente = c["minutos"] >= UMBRAL_ALERTA_MIN
            tk.Label(t, text=f"Espera: {c['minutos']} min", bg=color,
                     fg="#C53030" if urgente else "black",
                     font=("Arial", 10, "bold" if urgente else "normal")).pack(anchor="w")
        for cant, nombre, nota in c["productos"]:
            tk.Label(t, text=f"{cant} x {nombre}", bg=color, anchor="w",
                     justify="left").pack(fill="x")
            if nota:
                tk.Label(t, text=f"    Nota: {nota}", bg=color, anchor="w",
                         justify="left", font=("Arial", 9, "italic"),
                         wraplength=220).pack(fill="x")
        if c["estado"] == "Pendiente":
            tk.Button(t, text="Iniciar preparación",
                      command=lambda f=c["folio"]: accion(f, "Pendiente")
                      ).pack(fill="x", pady=(6, 0))
        elif c["estado"] == "En preparación":
            tk.Button(t, text="Marcar Listo", bg="#2F855A", fg="white",
                      command=lambda f=c["folio"]: accion(f, "En preparación")
                      ).pack(fill="x", pady=(6, 0))

    def dibujar():
        comandas = listar_comandas_cocina()
        for est, (interior, titulo) in interiores.items():
            for hijo in interior.winfo_children():
                hijo.destroy()
            propias = [c for c in comandas if c["estado"] == est]
            titulo.config(text=f"{est} ({len(propias)})")
            for c in propias:
                tarjeta(interior, c)
        texto_estado.set(f"Actualizado {datetime.now().strftime('%H:%M:%S')}"
                         if comandas else "Sin comandas por atender.")

    def pantalla_viva():
        try:
            return bool(zona.winfo_exists())
        except tk.TclError:
            return False

    def refresco_automatico():
        # Se detiene solo cuando se sale de esta pantalla; no bloquea la interfaz.
        if not pantalla_viva():
            return
        dibujar()
        app.ventana.after(INTERVALO_REFRESCO_MS, refresco_automatico)

    tk.Button(barra, text="Actualizar", command=dibujar).pack(side="right")
    app.volver_menu()
    dibujar()
    app.ventana.after(INTERVALO_REFRESCO_MS, refresco_automatico)
