# ================================================================
# RESPONSABILIDAD / MÓDULO: Equipo completo | Sprints 1–4 | entrada, permisos y navegación; conexión final asistida por IA
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
import tkinter as tk
from tkinter import messagebox, ttk
from base_datos import (
    inicializar_base_de_datos, registrar_usuario, validar_credenciales,
    listar_empleados, modificar_empleado, desactivar_empleado,
    registrar_producto, listar_productos, modificar_producto,
    cambiar_disponibilidad, registrar_mesa, listar_mesas,
    crear_pedido, agregar_producto_pedido, listar_detalle_pedido,
    modificar_detalle_pedido, quitar_producto_pedido,
    obtener_pedido_borrador_mesa, enviar_pedido_cocina,
    listar_pedidos_pendientes, marcar_pedido_en_preparacion
)
from permisos import obtener_permisos, obtener_roles

# SPRINT 3 / JAVIER TADEO: importar módulos independientes T31, T32, T33 y T41.
# No se han sustituido las pantallas ni funciones creadas por el resto del equipo.
from javier_caja_proveedores import preparar_tablas_javier
from javier_pantallas import mostrar_caja_javier, mostrar_proveedores_javier
# SPRINT 3 / PATRICIO COSAÍN: módulos independientes de almacén y compras (T39, T40, T42, T43).
from pato_almacen import preparar_tablas_pato
from pato_pantallas import mostrar_almacen_pato
from sprint3_pantallas import (mostrar_cocina_listos,mostrar_entregas,mostrar_insumos_said,mostrar_cuentas_juan,mostrar_compras_aaron)


# ================================================================
# INTEGRACIÓN GENERAL — SPRINT 4 — cinco integrantes
# Cada módulo conserva sus tareas y autoría original; los ajustes de
# conexión fueron preparados por asistencia de IA para el equipo.
# ================================================================
import estilos_sprint4 as estilos
from juan_sprint4 import (preparar_ventas_t45, mostrar_menu_juan_t51,
                          mostrar_mesas_juan_t52)
from said_sprint4 import (mostrar_login_said, mostrar_empleados_said,
                          mostrar_historial_said)
from javier_sprint4 import mostrar_caja_t53, mostrar_reportes_t55
from aaron_sprint4 import (asegurar_columna_envio, enviar_pedido_cocina_t61,
                            formulario_pedido_rediseno, mostrar_cocina_tarjetas)

class SistemaRestaurante:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Comandas")
        self.ventana.geometry("850x820")
        self.ventana.resizable(False, False)
        self.sesion = None
        inicializar_base_de_datos()
        # Javier: agrega solo las tablas nuevas de pagos, tickets y proveedores.
        preparar_tablas_javier()
        # Pato: agrega solo las tablas de insumos, movimientos y órdenes de compra si faltan.
        preparar_tablas_pato()
        # Juan Antonio — Sprint 4 T45: crea el registro de ventas cerradas.
        preparar_ventas_t45()
        # Aarón Mendoza — Sprint 4 T61: agrega columna de hora de envío si falta.
        asegurar_columna_envio()
        # Patricio Cosaín — Sprint 4 T63: estilo común en todas las pantallas.
        estilos.aplicar_estilos(self.ventana)
        self.marco = tk.Frame(ventana, padx=22, pady=18)
        self.marco.pack(fill="both", expand=True)
        self.mostrar_login()

    def limpiar_pantalla(self):
        # Destruye los controles anteriores antes de dibujar otra pantalla.
        for control in self.marco.winfo_children():
            control.destroy()

    # ================================================================
    # SPRINT 1 - TAREA 1
    # Nombre: Diseñar la pantalla de inicio de sesión
    # Responsable: Juan Antonio Ibarra Hernández
    # ¿QUÉ HACE? Presenta los campos de usuario y contraseña.
    # ================================================================
    def mostrar_login(self):
        """Sprint 4: conecta el módulo visual de Said Jesús."""
        return mostrar_login_said(self)

    # ================================================================
    # SPRINT 1 - TAREA 3
    # Nombre: Validar el usuario y la contraseña al ingresar
    # Responsable: Patricio Cosaín Torres
    # ¿QUÉ HACE? Comprueba credenciales y permite entrar al menú.
    # ================================================================
    def iniciar_sesion(self, evento=None):
        usuario, password = self.entrada_usuario.get().strip(), self.entrada_password.get()
        if not usuario or not password:
            messagebox.showwarning("Datos incompletos", "Escribe usuario y contraseña.")
            return
        datos = validar_credenciales(usuario, password)
        if datos is None:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")
            self.entrada_password.delete(0, tk.END)
            return
        self.sesion = datos
        self.mostrar_menu()

    # ================================================================
    # SPRINT 1 - TAREA 6
    # Nombre: Crear un menú principal diferente para cada puesto
    # Responsable: Aarón Mendoza Rodríguez
    # ¿QUÉ HACE? Dibuja botones de acuerdo con los permisos del rol.
    # ================================================================
    def mostrar_menu(self):
        """Sprint 4: conecta el módulo visual de Juan Antonio."""
        return mostrar_menu_juan_t51(self)

    # ================================================================
    # SPRINT 1 - TAREA 7
    # Nombre: Bloquear las funciones que no correspondan al puesto
    # Responsable: Patricio Cosaín Torres
    # ¿QUÉ HACE? Comprueba el permiso antes de abrir una pantalla.
    # ================================================================
    def ejecutar_opcion(self, opcion):
        if self.sesion is None or opcion not in obtener_permisos(self.sesion["rol"]):
            messagebox.showerror("Acceso denegado", "No tienes permiso.")
            return
        if opcion == "Administrar empleados":
            self.mostrar_empleados()
        elif opcion == "Consultar y administrar productos":
            self.mostrar_productos()
        elif opcion == "Consultar mesas":
            # Juan Antonio — Sprint 4 T52: vista rediseñada de mesas.
            mostrar_mesas_juan_t52(self)
        elif opcion == "Crear pedidos":
            self.mostrar_mesas()
        elif opcion == "Consultar comandas pendientes":
            self.mostrar_cocina()
        # SPRINT 3 - T31/T32/T33, Javier: conecta el menú ya existente de caja.
        elif opcion == "Consultar cuentas":
            # Javier Tadeo — Sprint 4 T53/T54: caja y ticket nuevos.
            mostrar_caja_t53(self)
        # SPRINT 3 - T41, Javier: pantalla independiente del catálogo de proveedores.
        elif opcion == "Administrar proveedores":
            mostrar_proveedores_javier(self)
        # SPRINT 3 - T39/T40/T42/T43, Pato: conecta el menú ya existente de almacén.
        elif opcion == "Consultar existencias":
            mostrar_almacen_pato(self)
        elif opcion == "Pedidos en preparación / Listos":
            mostrar_cocina_listos(self)
        elif opcion == "Pedidos listos para entregar":
            mostrar_entregas(self)
        elif opcion == "Catálogo y entradas de insumos":
            mostrar_insumos_said(self)
        elif opcion == "Consultar consumos y cerrar mesas":
            mostrar_cuentas_juan(self)
        elif opcion == "Recepción de órdenes de compra":
            mostrar_compras_aaron(self)
        elif opcion == "Consultar historial de pedidos":
            # Said Jesús — Sprint 4 T49/T50: buscar y ver pedidos cobrados.
            mostrar_historial_said(self)
        elif opcion == "Reportes de ventas":
            # Javier Tadeo — Sprint 4 T47/T55, con ventas T45/T46 de Juan.
            mostrar_reportes_t55(self)
        else:
            messagebox.showinfo("Pendiente", "Opción no disponible.")

    # ================================================================
    # SPRINT 2 - TAREAS 22 Y 23
    # Nombre: Mostrar pedidos pendientes y consultar sus productos y notas
    # ================================================================
    def mostrar_cocina(self):
        """Sprint 4: conecta el módulo visual de Aarón Mendoza."""
        return mostrar_cocina_tarjetas(self)

    def volver_menu(self):
        tk.Button(self.marco, text="Volver al menú", command=self.mostrar_menu).pack(fill="x", pady=10)

    # ================================================================
    # SPRINT 1 - TAREA 8
    # Nombre: Crear el formulario para dar de alta a empleados
    # Responsable: Said Jesús Echeverría Alcocer
    # ¿QUÉ HACE? Captura nombre, usuario, contraseña y puesto.
    # ================================================================
    def formulario_alta(self):
        w = tk.Toplevel(self.ventana); w.title("Registrar empleado"); w.geometry("350x360")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        entradas = {}
        for texto, key, oculto in [("Nombre completo", "nombre", False),
                                    ("Usuario", "usuario", False),
                                    ("Contraseña", "password", True)]:
            tk.Label(f, text=texto).pack(anchor="w")
            entradas[key] = tk.Entry(f, show="*" if oculto else "")
            entradas[key].pack(fill="x", pady=4)
        tk.Label(f, text="Puesto").pack(anchor="w")
        rol = ttk.Combobox(f, values=[r.capitalize() for r in obtener_roles()], state="readonly")
        rol.pack(fill="x", pady=4); rol.set("Mesero")
        def guardar():
            ok, msg = registrar_usuario(entradas["nombre"].get(), entradas["usuario"].get(),
                                         entradas["password"].get(), rol.get().lower())
            if ok:
                messagebox.showinfo("Registro", msg, parent=w); w.destroy(); self.mostrar_empleados()
            else: messagebox.showwarning("Registro", msg, parent=w)
        tk.Button(f, text="Guardar empleado", command=guardar).pack(fill="x", pady=8)

    # ================================================================
    # SPRINT 2 - TAREA 9
    # Nombre: Permitir modificar los datos y el puesto de un empleado
    # Responsable: Juan Antonio Ibarra Hernández
    # ¿QUÉ HACE? Selecciona un empleado activo y actualiza su nombre y rol.
    # ================================================================
    def formulario_editar_empleado(self):
        filas = [e for e in listar_empleados() if e[4] == 1]
        if not filas: messagebox.showinfo("Empleados", "No hay empleados activos."); return
        w = tk.Toplevel(self.ventana); w.title("Modificar empleado"); w.geometry("360x280")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        cb = ttk.Combobox(f, values=[f"{e[0]} - {e[1]}" for e in filas], state="readonly")
        cb.pack(fill="x"); cb.current(0)
        tk.Label(f, text="Nombre").pack(anchor="w")
        nombre = tk.Entry(f); nombre.pack(fill="x")
        tk.Label(f, text="Puesto").pack(anchor="w")
        rol = ttk.Combobox(f, values=[r.capitalize() for r in obtener_roles()], state="readonly")
        rol.pack(fill="x")
        def cargar(event=None):
            e = filas[cb.current()]; nombre.delete(0, tk.END); nombre.insert(0, e[1]); rol.set(e[3].capitalize())
        cb.bind("<<ComboboxSelected>>", cargar); cargar()
        def guardar():
            ok, msg = modificar_empleado(filas[cb.current()][0], nombre.get(), rol.get())
            if ok: messagebox.showinfo("Empleado", msg, parent=w); w.destroy(); self.mostrar_empleados()
            else: messagebox.showwarning("Empleado", msg, parent=w)
        tk.Button(f, text="Guardar cambios", command=guardar).pack(fill="x", pady=8)

    # ================================================================
    # SPRINT 2 - TAREA 10
    # Nombre: Permitir desactivar el acceso de empleados que ya no trabajen
    # Responsable: Juan Antonio Ibarra Hernández
    # ¿QUÉ HACE? Desactiva la cuenta; no elimina el registro histórico.
    # ================================================================
    def desactivar_cuenta(self):
        filas = [e for e in listar_empleados() if e[4] == 1 and e[0] != self.sesion["id"]]
        if not filas: messagebox.showinfo("Empleados", "No hay otras cuentas activas."); return
        w = tk.Toplevel(self.ventana); w.title("Desactivar acceso"); w.geometry("360x170")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        cb = ttk.Combobox(f, values=[f"{e[0]} - {e[1]}" for e in filas], state="readonly")
        cb.pack(fill="x"); cb.current(0)
        def desactivar():
            eid = filas[cb.current()][0]
            if messagebox.askyesno("Confirmar", "¿Desactivar esta cuenta?", parent=w):
                desactivar_empleado(eid); w.destroy(); self.mostrar_empleados()
        tk.Button(f, text="Desactivar cuenta", command=desactivar).pack(fill="x", pady=12)

    def mostrar_empleados(self):
        """Sprint 4: conecta el módulo visual de Said Jesús."""
        return mostrar_empleados_said(self)

    # ================================================================
    # SPRINT 2 - TAREA 11
    # Nombre: Crear la pantalla de platillos y bebidas
    # Responsable: Javier Tadeo Jasso Vidaña
    # ¿QUÉ HACE? Muestra los productos y los controles del catálogo.
    # ================================================================
    def mostrar_productos(self):
        self.limpiar_pantalla()
        tk.Label(self.marco, text="Platillos y bebidas", font=("Arial", 16, "bold")).pack(pady=8)
        tabla = ttk.Treeview(self.marco, columns=("categoria", "precio", "estado"), show="tree headings", height=10)
        tabla.heading("#0", text="Producto"); tabla.heading("categoria", text="Categoría")
        tabla.heading("precio", text="Precio"); tabla.heading("estado", text="Estado")
        tabla.pack(fill="both", expand=True)
        for p in listar_productos():
            tabla.insert("", "end", text=p[1], values=(p[2], f"${p[4]:.2f}", "Disponible" if p[5] else "Agotado"))
        tk.Button(self.marco, text="Registrar producto (T12)", command=self.formulario_producto).pack(fill="x", pady=3)
        tk.Button(self.marco, text="Modificar producto (T13)", command=self.formulario_editar_producto).pack(fill="x", pady=3)
        tk.Button(self.marco, text="Cambiar disponibilidad (T14)", command=self.cambiar_estado_producto).pack(fill="x", pady=3)
        self.volver_menu()

    # ================================================================
    # SPRINT 2 - TAREA 12
    # Nombre: Registrar productos con nombre, categoría y precio
    # Responsable: Javier Tadeo Jasso Vidaña
    # ¿QUÉ HACE? Captura datos y los envía a la función de base de datos.
    # ================================================================
    def formulario_producto(self):
        w = tk.Toplevel(self.ventana); w.title("Registrar producto"); w.geometry("350x300")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        campos = {}
        for etiqueta, key in [("Nombre", "nombre"), ("Categoría", "categoria"),
                              ("Descripción", "descripcion"), ("Precio", "precio")]:
            tk.Label(f, text=etiqueta).pack(anchor="w")
            campos[key] = tk.Entry(f); campos[key].pack(fill="x", pady=3)
        def guardar():
            ok, msg = registrar_producto(campos["nombre"].get(), campos["categoria"].get(),
                                         campos["descripcion"].get(), campos["precio"].get())
            if ok: messagebox.showinfo("Producto", msg, parent=w); w.destroy(); self.mostrar_productos()
            else: messagebox.showwarning("Producto", msg, parent=w)
        tk.Button(f, text="Guardar", command=guardar).pack(fill="x", pady=8)

    # ================================================================
    # SPRINT 2 - TAREA 13
    # Nombre: Permitir cambiar el nombre, descripción y precio de los productos
    # Responsable: Aarón Mendoza Rodríguez
    # ¿QUÉ HACE? Permite elegir un producto y actualizar sus datos.
    # ================================================================
    def formulario_editar_producto(self):
        filas = listar_productos()
        if not filas: messagebox.showinfo("Productos", "Primero registra productos."); return
        w = tk.Toplevel(self.ventana); w.title("Modificar producto"); w.geometry("360x290")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        cb = ttk.Combobox(f, values=[f"{p[0]} - {p[1]}" for p in filas], state="readonly")
        cb.pack(fill="x"); cb.current(0)
        campos = {}
        for etiqueta, key in [("Nombre", "nombre"), ("Descripción", "descripcion"), ("Precio", "precio")]:
            tk.Label(f, text=etiqueta).pack(anchor="w")
            campos[key] = tk.Entry(f); campos[key].pack(fill="x", pady=3)
        def cargar(event=None):
            p = filas[cb.current()]
            for key, valor in [("nombre", p[1]), ("descripcion", p[3]), ("precio", p[4])]:
                campos[key].delete(0, tk.END); campos[key].insert(0, str(valor))
        cb.bind("<<ComboboxSelected>>", cargar); cargar()
        def guardar():
            ok, msg = modificar_producto(filas[cb.current()][0], campos["nombre"].get(),
                                         campos["descripcion"].get(), campos["precio"].get())
            if ok: messagebox.showinfo("Producto", msg, parent=w); w.destroy(); self.mostrar_productos()
            else: messagebox.showwarning("Producto", msg, parent=w)
        tk.Button(f, text="Guardar cambios", command=guardar).pack(fill="x", pady=8)

    # ================================================================
    # SPRINT 2 - TAREA 14
    # Nombre: Marcar los productos como disponibles o agotados
    # Responsable: Javier Tadeo Jasso Vidaña
    # ¿QUÉ HACE? Alterna el estado del producto seleccionado.
    # ================================================================
    def cambiar_estado_producto(self):
        filas = listar_productos()
        if not filas: messagebox.showinfo("Productos", "No hay productos."); return
        w = tk.Toplevel(self.ventana); w.title("Disponibilidad"); w.geometry("360x160")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        cb = ttk.Combobox(f, values=[f"{p[0]} - {p[1]} ({'Disponible' if p[5] else 'Agotado'})" for p in filas],
                          state="readonly")
        cb.pack(fill="x"); cb.current(0)
        def cambiar():
            p = filas[cb.current()]; cambiar_disponibilidad(p[0], not bool(p[5]))
            w.destroy(); self.mostrar_productos()
        tk.Button(f, text="Cambiar estado", command=cambiar).pack(fill="x", pady=10)

    # ================================================================
    # SPRINT 2 - TAREA 15
    # Nombre: Diseñar la pantalla donde se muestran las mesas
    # Responsable: Juan Antonio Ibarra Hernández
    # ¿QUÉ HACE? Presenta las mesas registradas y su estado visual.
    # ================================================================
    def mostrar_mesas(self):
        self.limpiar_pantalla()
        tk.Label(self.marco, text="Mesas del restaurante", font=("Arial", 16, "bold")).pack(pady=8)
        tabla = ttk.Treeview(self.marco, columns=("estado",), show="tree headings", height=13)
        tabla.heading("#0", text="Mesa"); tabla.heading("estado", text="Estado")
        tabla.pack(fill="both", expand=True, pady=8)
        for m in listar_mesas():
            # iid = id de la mesa, para saber cuál seleccionó el mesero (T20).
            tabla.insert("", "end", iid=str(m[0]), text=f"Mesa {m[1]}", values=(m[2],))
        if self.sesion["rol"] == "gerente":
            tk.Button(self.marco, text="Registrar mesa (T16)", command=self.formulario_mesa).pack(fill="x")
        if self.sesion["rol"] == "mesero":
            tk.Button(self.marco, text="Crear pedido (T18)", command=self.nuevo_pedido).pack(fill="x")
            tk.Button(self.marco, text="Editar pedido en borrador (T20)",
                      command=lambda: self.editar_pedido_borrador(tabla)).pack(fill="x", pady=3)
        self.volver_menu()

    # ================================================================
    # SPRINT 2 - TAREA 20
    # Nombre: Permitir corregir o quitar productos antes de enviarlos
    # Responsable: Aarón Mendoza Rodríguez
    # ¿QUÉ HACE? Reabre la ventana del pedido en Borrador de la mesa seleccionada.
    # ================================================================
    def editar_pedido_borrador(self, tabla):
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showinfo("Pedidos", "Primero selecciona una mesa de la tabla.")
            return
        pedido_id = obtener_pedido_borrador_mesa(int(seleccion[0]))
        if pedido_id is None:
            messagebox.showinfo("Pedidos", "Esa mesa no tiene un pedido en borrador.")
            return
        self.formulario_agregar_productos(pedido_id)

    # ================================================================
    # SPRINT 2 - TAREA 16
    # Nombre: Registrar las mesas con su número correspondiente
    # Responsable: Patricio Cosaín Torres
    # ¿QUÉ HACE? Registra una mesa con número único y estado inicial libre.
    # ================================================================
    def formulario_mesa(self):
        w = tk.Toplevel(self.ventana); w.title("Registrar mesa"); w.geometry("300x150")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        tk.Label(f, text="Número de mesa").pack(anchor="w")
        entrada = tk.Entry(f); entrada.pack(fill="x", pady=5)
        def guardar():
            ok, msg = registrar_mesa(entrada.get())
            if ok: messagebox.showinfo("Mesa", msg, parent=w); w.destroy(); self.mostrar_mesas()
            else: messagebox.showwarning("Mesa", msg, parent=w)
        tk.Button(f, text="Guardar mesa", command=guardar).pack(fill="x")

    # ================================================================
    # SPRINT 2 - TAREA 17
    # Nombre: Indicar cuáles mesas están libres y cuáles ocupadas
    # Responsable: Patricio Cosaín Torres
    # ¿QUÉ HACE? Muestra el estado de cada mesa; T18 cambia a ocupada.
    # ================================================================

    # ================================================================
    # SPRINT 2 - TAREA 18
    # Nombre: Crear un pedido nuevo y relacionarlo con una mesa
    # Responsable: Patricio Cosaín Torres
    # ¿QUÉ HACE? Crea un pedido borrador asociado a una mesa libre.
    # ================================================================
    def nuevo_pedido(self):
        libres = [m for m in listar_mesas() if m[2] == "Libre"]
        if not libres: messagebox.showinfo("Pedidos", "No hay mesas libres."); return
        w = tk.Toplevel(self.ventana); w.title("Nuevo pedido"); w.geometry("330x160")
        f = tk.Frame(w, padx=18, pady=15); f.pack(fill="both", expand=True)
        cb = ttk.Combobox(f, values=[f"Mesa {m[1]}" for m in libres], state="readonly")
        cb.pack(fill="x"); cb.current(0)
        def crear():
            ok, msg, pid = crear_pedido(libres[cb.current()][0])
            if ok:
                messagebox.showinfo("Pedido", f"{msg} Folio: {pid}", parent=w)
                w.destroy(); self.formulario_agregar_productos(pid)
            else: messagebox.showwarning("Pedido", msg, parent=w)
        tk.Button(f, text="Crear pedido", command=crear).pack(fill="x", pady=10)

    # ================================================================
    # SPRINT 2 - TAREA 19
    # Nombre: Elegir platillos y bebidas con sus cantidades
    # Responsable: Aarón Mendoza Rodríguez
    # ¿QUÉ HACE? Agrega productos disponibles y cantidades al pedido.
    #
    # SPRINT 2 - TAREA 20
    # Nombre: Permitir corregir o quitar productos antes de enviarlos
    # Responsable: Aarón Mendoza Rodríguez
    # ¿QUÉ HACE? Muestra los productos del pedido (cantidad, precio y nota) y
    #            permite modificarlos o quitarlos mientras esté en Borrador.
    #
    # SPRINT 2 - TAREA 21
    # Nombre: Guardar el pedido y enviarlo a la sección de cocina
    # Responsable: Aarón Mendoza Rodríguez
    # ¿QUÉ HACE? El botón de enviar cambia el pedido de Borrador a Pendiente
    #            y cierra esta ventana para impedir más cambios.
    # ================================================================
    def formulario_agregar_productos(self, pedido_id):
        """Sprint 4: conecta el módulo visual de Aarón Mendoza."""
        return formulario_pedido_rediseno(self, pedido_id)

    # ================================================================
    # SPRINT 1 - TAREA 4
    # Nombre: Permitir cerrar sesión y volver al acceso
    # Responsable: Said Jesús Echeverría Alcocer
    # ¿QUÉ HACE? Limpia la sesión actual y regresa a la pantalla de acceso.
    # ================================================================
    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", "¿Quieres cerrar tu sesión?"):
            self.sesion = None
            self.mostrar_login()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = SistemaRestaurante(ventana)
    ventana.mainloop()
