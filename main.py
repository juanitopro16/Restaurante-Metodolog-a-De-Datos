import tkinter as tk
from tkinter import messagebox, ttk

from base_datos import inicializar_base_de_datos, registrar_usuario, validar_credenciales
from permisos import obtener_permisos, obtener_roles


class SistemaRestaurante:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Comandas")
        self.ventana.geometry("500x590")
        self.ventana.resizable(False, False)
        self.sesion = None

        inicializar_base_de_datos()

        self.marco = tk.Frame(ventana, padx=25, pady=20)
        self.marco.pack(fill="both", expand=True)
        self.mostrar_login()

    # Borra los controles de la pantalla anterior.
    def limpiar_pantalla(self):
        for control in self.marco.winfo_children():
            control.destroy()

    # ================================================================
    # SPRINT 1 - TAREA E1-1
    # Nombre: Diseñar la pantalla de inicio de sesión
    # Responsable: Juan Antonio Ibarra Hernández
    # ================================================================
    def mostrar_login(self):
        self.limpiar_pantalla()
        self.sesion = None

        tk.Label(self.marco, text="Sistema de Comandas",
                 font=("Arial", 17, "bold"), fg="#1A365D").pack(pady=(10, 5))
        tk.Label(self.marco, text="Acceso para empleados del restaurante").pack(pady=(0, 22))

        # El empleado escribe aquí su usuario y contraseña.
        tk.Label(self.marco, text="Usuario:", anchor="w").pack(fill="x")
        self.entrada_usuario = tk.Entry(self.marco, font=("Arial", 11))
        self.entrada_usuario.pack(fill="x", pady=(3, 14))

        tk.Label(self.marco, text="Contraseña:", anchor="w").pack(fill="x")
        self.entrada_password = tk.Entry(self.marco, show="*", font=("Arial", 11))
        self.entrada_password.pack(fill="x", pady=(3, 18))
        self.entrada_password.bind("<Return>", self.iniciar_sesion)

        tk.Button(self.marco, text="Iniciar sesión", bg="#2B6CB0",
                  fg="white", command=self.iniciar_sesion).pack(fill="x")

        # Cuentas que usamos para probar cada puesto.
        cuentas = (
            "Cuentas de prueba:\n"
            "Gerente: gerente1 / admin123\n"
            "Mesero: mesero1 / mesero123\n"
            "Cocina: cocina1 / cocina123\n"
            "Caja: caja1 / caja123\n"
            "Almacén: almacen1 / almacen123"
        )
        tk.Label(self.marco, text=cuentas, justify="left",
                 font=("Arial", 9)).pack(anchor="w", pady=20)
        self.entrada_usuario.focus_set()

    # ================================================================
    # SPRINT 1 - TAREA E1-3
    # Nombre: Validar el usuario y la contraseña al ingresar
    # Responsable: Patricio Cosaín Torres
    # ================================================================
    def iniciar_sesion(self, evento=None):
        usuario = self.entrada_usuario.get().strip()
        password = self.entrada_password.get()

        if usuario == "" or password == "":
            messagebox.showwarning("Datos incompletos", "Escribe tu usuario y contraseña.")
            return

        datos = validar_credenciales(usuario, password)
        if datos is None:
            messagebox.showerror("Acceso denegado", "El usuario o la contraseña son incorrectos.")
            self.entrada_password.delete(0, tk.END)
            self.entrada_password.focus_set()
            return

        self.sesion = datos
        self.mostrar_menu()

    # ================================================================
    # SPRINT 2 - TAREA E1-6
    # Nombre: Crear un menú principal diferente para cada puesto
    # Responsable: Aaron Mendoza Rodríguez
    # ================================================================
    def mostrar_menu(self):
        self.limpiar_pantalla()
        rol = self.sesion["rol"]

        tk.Label(self.marco, text="Menú principal", font=("Arial", 17, "bold"),
                 fg="#1A365D").pack(pady=(5, 8))
        tk.Label(self.marco, text=self.sesion["nombre"],
                 font=("Arial", 12, "bold")).pack()
        tk.Label(self.marco, text="Puesto: " + rol.capitalize(),
                 fg="#2B6CB0").pack(pady=(3, 15))
        tk.Label(self.marco, text="Opciones disponibles:",
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))

        # Las opciones salen de la lista del puesto que inició sesión.
        for opcion in obtener_permisos(rol):
            tk.Button(
                self.marco,
                text=opcion,
                anchor="w",
                command=lambda texto=opcion: self.ejecutar_opcion(texto),
            ).pack(fill="x", pady=3)

        # TAREA E1-4 - Permitir cerrar sesión y volver al acceso.
        # Responsable: Said Jesús Echeverría Alcocer
        tk.Button(self.marco, text="Cerrar sesión", bg="#C53030", fg="white",
                  command=self.cerrar_sesion).pack(fill="x", pady=(18, 5))

    # ================================================================
    # SPRINT 2 - TAREA E1-7
    # Nombre: Bloquear las funciones que no correspondan al puesto
    # Responsable: Patricio Cosaín Torres
    # ================================================================
    def ejecutar_opcion(self, opcion):
        if self.sesion is None:
            messagebox.showerror("Acceso denegado", "Primero debes iniciar sesión.")
            return

        # Antes de abrir una opción se comprueba que el puesto tenga permiso.
        permisos = obtener_permisos(self.sesion["rol"])
        if opcion not in permisos:
            messagebox.showerror("Acceso denegado", "Tu puesto no tiene permiso para esta función.")
            return

        if opcion == "Administrar empleados":
            self.mostrar_formulario_empleado()
        else:
            messagebox.showinfo(
                "Opción seleccionada",
                "La opción '" + opcion + "' está disponible para el puesto de "
                + self.sesion["rol"] + ".\n"
                "Su funcionamiento completo se puede agregar en otras tareas del backlog.",
            )

    # ================================================================
    # SPRINT 2 - TAREA E1-8
    # Nombre: Crear el formulario para dar de alta a empleados
    # Responsable: Said Jesús Echeverría Alcocer
    # ================================================================
    def mostrar_formulario_empleado(self):
        # Solo se permite abrirlo si el gerente tiene el permiso correspondiente.
        if self.sesion is None or "Administrar empleados" not in obtener_permisos(self.sesion["rol"]):
            messagebox.showerror("Acceso denegado", "No tienes permiso para registrar empleados.")
            return

        formulario = tk.Toplevel(self.ventana)
        formulario.title("Dar de alta a un empleado")
        formulario.geometry("360x390")
        formulario.resizable(False, False)
        formulario.transient(self.ventana)
        formulario.grab_set()

        marco = tk.Frame(formulario, padx=22, pady=18)
        marco.pack(fill="both", expand=True)
        tk.Label(marco, text="Registrar empleado", font=("Arial", 15, "bold"),
                 fg="#1A365D").pack(pady=(0, 15))

        tk.Label(marco, text="Nombre completo:", anchor="w").pack(fill="x")
        entrada_nombre = tk.Entry(marco)
        entrada_nombre.pack(fill="x", pady=(3, 10))

        tk.Label(marco, text="Nombre de usuario:", anchor="w").pack(fill="x")
        entrada_usuario = tk.Entry(marco)
        entrada_usuario.pack(fill="x", pady=(3, 10))

        tk.Label(marco, text="Contraseña:", anchor="w").pack(fill="x")
        entrada_password = tk.Entry(marco, show="*")
        entrada_password.pack(fill="x", pady=(3, 10))

        tk.Label(marco, text="Puesto:", anchor="w").pack(fill="x")
        seleccion_rol = ttk.Combobox(
            marco, values=[rol.capitalize() for rol in obtener_roles()], state="readonly"
        )
        seleccion_rol.pack(fill="x", pady=(3, 15))
        seleccion_rol.set("Mesero")

        # Los datos del formulario se guardan con la función de base_datos.py.
        def guardar_empleado():
            correcto, mensaje = registrar_usuario(
                entrada_nombre.get(),
                entrada_usuario.get(),
                entrada_password.get(),
                seleccion_rol.get().lower(),
            )

            if correcto:
                messagebox.showinfo("Registro", mensaje, parent=formulario)
                formulario.destroy()
            else:
                messagebox.showwarning("No se pudo registrar", mensaje, parent=formulario)

        tk.Button(marco, text="Guardar empleado", bg="#2B6CB0", fg="white",
                  command=guardar_empleado).pack(fill="x", pady=(5, 0))

    # ================================================================
    # SPRINT 1 - TAREA E1-4
    # Nombre: Permitir cerrar sesión y volver al acceso
    # Responsable: Said Jesús Echeverría Alcocer
    # ================================================================
    def cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar sesión", "¿Quieres cerrar tu sesión?")
        if confirmar:
            self.sesion = None
            self.mostrar_login()


if __name__ == "__main__":
    ventana = tk.Tk()
    app = SistemaRestaurante(ventana)
    ventana.mainloop()
