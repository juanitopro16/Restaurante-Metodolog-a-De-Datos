"""
main.py - Interfaz principal del Sistema de Comandas (Sprint 1)
Integra el Login (Tarea 1), Validación (Tarea 3), Cierre de sesión (Tarea 4)
y la vinculación con Roles/Permisos (Tarea 5).
"""

import tkinter as tk
from tkinter import messagebox
from base_datos import inicializar_base_de_datos, verificar_credenciales
from permisos import obtener_permisos_rol

class SistemaRestauranteApp:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Restaurante - Control de Acceso")
        self.ventana.geometry("460x450")
        self.ventana.resizable(False, False)

        self.sesion_activa = None
        inicializar_base_de_datos()

        self.marco_principal = tk.Frame(self.ventana, padx=25, pady=20)
        self.marco_principal.pack(fill="both", expand=True)

        self.mostrar_login()

    def limpiar_interfaz(self):
        for widget in self.marco_principal.winfo_children():
            widget.destroy()

    # Tarea 1 (E1-1): Pantalla de inicio de sesión
    def mostrar_login(self):
        self.limpiar_interfaz()
        self.sesion_activa = None

        tk.Label(
            self.marco_principal,
            text="Sistema de Comandas",
            font=("Arial", 16, "bold"),
            fg="#1A365D"
        ).pack(pady=(5, 2))

        tk.Label(
            self.marco_principal,
            text="Control de acceso para personal del restaurante",
            font=("Arial", 9),
            fg="#4A5568"
        ).pack(pady=(0, 20))

        tk.Label(self.marco_principal, text="Usuario:", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        self.entry_user = tk.Entry(self.marco_principal, font=("Arial", 11))
        self.entry_user.pack(fill="x", pady=(2, 14))
        self.entry_user.focus()

        tk.Label(self.marco_principal, text="Contraseña:", font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
        self.entry_pass = tk.Entry(self.marco_principal, font=("Arial", 11), show="*")
        self.entry_pass.pack(fill="x", pady=(2, 20))
        self.entry_pass.bind("<Return>", lambda event: self.ejecutar_login())

        btn_ingresar = tk.Button(
            self.marco_principal,
            text="Iniciar Sesión",
            font=("Arial", 11, "bold"),
            bg="#2B6CB0",
            fg="white",
            cursor="hand2",
            pady=7,
            command=self.ejecutar_login
        )
        btn_ingresar.pack(fill="x", pady=6)

        marco_guia = tk.LabelFrame(
            self.marco_principal,
            text=" Cuentas de demostración ",
            font=("Arial", 8, "bold"),
            fg="#718096",
            padx=10,
            pady=6
        )
        marco_guia.pack(fill="x", pady=(15, 0))

        guia_texto = (
            "• Gerente:  usuario: gerente1  |  clave: admin123\n"
            "• Mesero:   usuario: mesero1   |  clave: mesero123\n"
            "• Cocina:   usuario: cocina1   |  clave: cocina123\n"
            "• Caja:     usuario: caja1     |  clave: caja123\n"
            "• Almacén:  usuario: almacen1  |  clave: almacen123"
        )
        tk.Label(marco_guia, text=guia_texto, font=("Courier", 8), justify="left", fg="#2D3748").pack(anchor="w")

    # Tarea 3 (E1-3): Validación de credenciales
    def ejecutar_login(self):
        usuario = self.entry_user.get().strip()
        clave = self.entry_pass.get().strip()

        if not usuario or not clave:
            messagebox.showwarning("Atención", "Por favor ingrese usuario y contraseña.")
            return

        usuario_autenticado = verificar_credenciales(usuario, clave)

        if usuario_autenticado:
            self.sesion_activa = usuario_autenticado
            messagebox.showinfo(
                "Acceso Correcto",
                f"Bienvenido/a {usuario_autenticado['nombre_completo']}\nPuesto: {usuario_autenticado['rol'].upper()}"
            )
            self.mostrar_panel_sesion()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            self.entry_pass.delete(0, tk.END)

    # Tarea 4 (E1-4) y Tarea 5 (E1-5): Sesión activa y permisos
    def mostrar_panel_sesion(self):
        self.limpiar_interfaz()

        rol = self.sesion_activa["rol"]
        nombre = self.sesion_activa["nombre_completo"]
        permisos = obtener_permisos_rol(rol)

        tk.Label(self.marco_principal, text=f"Sesión iniciada: {nombre}", font=("Arial", 13, "bold")).pack(pady=(4, 2))
        tk.Label(self.marco_principal, text=f"Rol asignado: [{rol.upper()}]", font=("Arial", 10, "bold"), fg="#2B6CB0").pack(pady=(0, 10))

        tk.Label(self.marco_principal, text="Permisos autorizados:", font=("Arial", 9, "bold"), anchor="w").pack(fill="x", pady=(0, 4))

        marco_lista = tk.Frame(self.marco_principal, bg="#EDF2F7", bd=1, relief="solid", padx=10, pady=8)
        marco_lista.pack(fill="both", expand=True, pady=(0, 15))

        for p in permisos:
            tk.Label(marco_lista, text=f"✓  {p}", font=("Arial", 9), bg="#EDF2F7", fg="#2D3748", anchor="w").pack(fill="x", pady=2)

        btn_cerrar_sesion = tk.Button(
            self.marco_principal,
            text="Cerrar Sesión",
            font=("Arial", 10, "bold"),
            bg="#E53E3E",
            fg="white",
            cursor="hand2",
            pady=6,
            command=self.ejecutar_logout
        )
        btn_cerrar_sesion.pack(fill="x")

    def ejecutar_logout(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Desea salir del sistema?"):
            self.sesion_activa = None
            self.mostrar_login()

if __name__ == "__main__":
    ventana = tk.Tk()
    app = SistemaRestauranteApp(ventana)
    ventana.mainloop()
