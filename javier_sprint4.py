# ================================================================
# RESPONSABILIDAD / MÓDULO: Javier Tadeo (tareas asignadas) | Sprint 4 T47 T53 T54 T55 | caja, ticket y reportes; completado con IA
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Sprint 4 — Javier Tadeo: T47, T53, T54 y T55.

Módulo ADICIONAL: reutiliza la lógica de Sprint 3, la T45 de Juan y
los filtros T47 ya entregados. No reemplaza archivos compartidos.
Implementación asistida por IA, pendiente de integración visual final.
"""
from datetime import date
from decimal import Decimal
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from javier_caja_proveedores import (
    listar_cuentas_por_cobrar, consultar_cuenta, calcular_cambio,
    registrar_pago, obtener_ticket,
)
from javier_t47_fechas import validar_rango_t47
from javier_t47_filtros import crear_filtros_t47
from juan_sprint4 import consultar_ventas_periodo_t45, resumen_diario_t46

AZUL = '#183153'
FONDO = '#F3F7FC'
VERDE = '#147D64'
NARANJA = '#B45309'


def consultar_periodo_t47(fecha_inicio, fecha_fin):
    """T47: validar rango y consultar ventas CERRADAS de T45.

    Retorna {'inicio', 'fin', 'filas', 'cantidad', 'total'}.
    NO usa pedidos.fecha ni fecha del pago: usa fecha_cierre de Juan.
    """
    inicio, fin = validar_rango_t47(fecha_inicio, fecha_fin)
    filas, total = consultar_ventas_periodo_t45(inicio, fin)
    return {'inicio': inicio, 'fin': fin, 'filas': filas,
            'cantidad': len(filas), 'total': total}


def consultar_dia_t55(dia):
    """T55: datos para el botón de resumen diario, usando T46."""
    inicio, _ = validar_rango_t47(dia, dia)
    return resumen_diario_t46(inicio)


def _importe(valor):
    return f'${Decimal(str(valor)):,.2f}'


def texto_ticket_t54(pago_id):
    """T54: ticket mejor presentado con copia histórica de líneas de pago.

    No consulta precios actuales del catálogo ni registra otro cobro.
    """
    ticket = obtener_ticket(pago_id)
    if ticket is None:
        return None
    cabecera, lineas = ticket
    folio, mesa, metodo, total, recibido, cambio, fecha = cabecera
    ancho = 49
    contenido = [
        '=' * ancho,
        'RESTAURANTE - SISTEMA DE COMANDAS'.center(ancho),
        'COMPROBANTE DE PAGO'.center(ancho),
        '=' * ancho,
        f'Folio de pago: {folio}',
        f'Fecha:         {fecha}',
        f'Mesa:          {mesa}',
        '-' * ancho,
        f'{"CANT. PRODUCTO":30}{"IMPORTE":>19}',
        '-' * ancho,
    ]
    for nombre, cantidad, precio, importe in lineas:
        nombre = str(nombre)
        contenido.append(f'{cantidad} x {nombre}'[:30].ljust(30) + f'{_importe(importe):>19}')
        contenido.append(f'    Precio unitario: {_importe(precio)}')
    contenido += [
        '-' * ancho,
        f'{"TOTAL":30}{_importe(total):>19}',
        f'Método de pago: {metodo}',
        f'Recibido: {_importe(recibido)}',
        f'Cambio:   {_importe(cambio)}',
        '=' * ancho,
        'Gracias por su visita'.center(ancho),
    ]
    return '\n'.join(contenido) + '\n'


def mostrar_ticket_t54(ventana, pago_id):
    """T54: ventana de ticket y opción de guardar TXT."""
    texto = texto_ticket_t54(pago_id)
    if texto is None:
        messagebox.showerror('Ticket', 'No existe ese pago.', parent=ventana)
        return
    win = tk.Toplevel(ventana)
    win.title(f'Ticket de pago #{pago_id}')
    win.geometry('630x580')
    tk.Label(win, text=f'Ticket #{pago_id}', font=('Arial', 16, 'bold'), fg=AZUL).pack(pady=12)
    zona = tk.Text(win, font=('Consolas', 10), wrap='none', padx=12, pady=12)
    zona.pack(fill='both', expand=True, padx=14)
    zona.insert('1.0', texto)
    zona.config(state='disabled')

    def guardar():
        ruta = filedialog.asksaveasfilename(parent=win, defaultextension='.txt',
            initialfile=f'ticket_{pago_id}.txt', filetypes=[('Texto', '*.txt')])
        if not ruta:
            return
        try:
            with open(ruta, 'w', encoding='utf-8') as archivo:
                archivo.write(texto)
        except OSError as error:
            messagebox.showerror('No se pudo guardar', str(error), parent=win)
        else:
            messagebox.showinfo('Ticket', 'Comprobante guardado.', parent=win)
    tk.Button(win, text='Guardar comprobante (.txt)', command=guardar,
              bg=VERDE, fg='white', pady=8).pack(fill='x', padx=14, pady=12)
    return win


def mostrar_caja_t53(app):
    """T53: rediseño de caja. Conserva registrar_pago de Sprint 3."""
    if not app.sesion or app.sesion.get('rol') != 'caja':
        messagebox.showerror('Acceso denegado', 'Solo el personal de caja puede cobrar.')
        return
    app.limpiar_pantalla()
    raiz = tk.Frame(app.marco, bg=FONDO, padx=14, pady=10)
    raiz.pack(fill='both', expand=True)
    tk.Label(raiz, text='Caja y cobros', font=('Arial', 20, 'bold'),
             bg=FONDO, fg=AZUL).pack(anchor='w', pady=(0, 8))
    tk.Label(raiz, text='Selecciona una mesa con pedidos entregados pendientes de pago.',
             bg=FONDO).pack(anchor='w')

    tabla = ttk.Treeview(raiz, columns=('mesa', 'total'), show='headings',
                         height=6, selectmode='browse')
    tabla.heading('mesa', text='Mesa')
    tabla.heading('total', text='Pendiente')
    tabla.column('mesa', width=140)
    tabla.column('total', width=180, anchor='e')
    tabla.pack(fill='x', pady=8)

    tk.Label(raiz, text='Productos de la cuenta', font=('Arial', 11, 'bold'),
             bg=FONDO).pack(anchor='w')
    detalle = tk.Text(raiz, height=9, state='disabled', font=('Consolas', 10))
    detalle.pack(fill='both', expand=True)
    total_var = tk.StringVar(value='Total: $0.00')
    tk.Label(raiz, textvariable=total_var, font=('Arial', 15, 'bold'),
             bg=FONDO, fg=AZUL).pack(anchor='e', pady=5)

    fila = tk.Frame(raiz, bg=FONDO)
    fila.pack(fill='x', pady=4)
    tk.Label(fila, text='Método:', bg=FONDO).grid(row=0, column=0, sticky='w')
    metodo = tk.StringVar(value='Efectivo')
    ttk.Combobox(fila, textvariable=metodo, values=('Efectivo', 'Tarjeta'),
                 state='readonly', width=16).grid(row=1, column=0, padx=(0, 12))
    tk.Label(fila, text='Recibido (efectivo):', bg=FONDO).grid(row=0, column=1, sticky='w')
    recibido = ttk.Entry(fila, width=20)
    recibido.grid(row=1, column=1)
    aviso = tk.StringVar(value='Selecciona una mesa para consultar su cuenta.')
    tk.Label(raiz, textvariable=aviso, bg=FONDO, fg=AZUL,
             wraplength=600).pack(anchor='w', pady=7)

    def mesa_seleccionada():
        sel = tabla.selection()
        return int(sel[0]) if sel else None

    def mostrar_detalle(event=None):
        mid = mesa_seleccionada()
        detalle.config(state='normal')
        detalle.delete('1.0', 'end')
        total_var.set('Total: $0.00')
        if mid is not None:
            cuenta = consultar_cuenta(mid)
            for linea in cuenta['lineas']:
                detalle.insert('end', f"{linea['cantidad']} x {linea['producto']} "
                    f"({_importe(linea['precio'])}) = {_importe(linea['importe'])}\n")
            total_var.set('Total: ' + _importe(cuenta['total']))
        detalle.config(state='disabled')

    def actualizar():
        tabla.delete(*tabla.get_children())
        for mid, numero, total in listar_cuentas_por_cobrar():
            tabla.insert('', 'end', iid=str(mid), values=(numero, _importe(total)))
        mostrar_detalle()
        aviso.set('Cuentas actualizadas.' if tabla.get_children() else 'Sin cuentas pendientes de cobro.')

    def vista_cambio():
        mid = mesa_seleccionada()
        if mid is None:
            messagebox.showwarning('Caja', 'Selecciona una mesa.')
            return
        total = consultar_cuenta(mid)['total']
        if metodo.get() == 'Tarjeta':
            aviso.set('Pago con tarjeta: ' + _importe(total) + '. No procesa tarjetas en línea.')
        else:
            ok, mensaje, cambio = calcular_cambio(total, recibido.get())
            aviso.set('Cambio: ' + _importe(cambio) if ok else mensaje)

    def cobrar():
        mid = mesa_seleccionada()
        if mid is None:
            messagebox.showwarning('Caja', 'Selecciona una mesa.')
            return
        ok, mensaje, folio = registrar_pago(mid, metodo.get(), recibido.get())
        if not ok:
            messagebox.showwarning('Cobro', mensaje)
            return
        actualizar()
        aviso.set(f'Pago #{folio} registrado correctamente.')
        messagebox.showinfo('Cobro', f'Pago #{folio} registrado correctamente.')
        mostrar_ticket_t54(app.ventana, folio)

    tabla.bind('<<TreeviewSelect>>', mostrar_detalle)
    tk.Button(raiz, text='Calcular cambio / ver importe', command=vista_cambio).pack(fill='x', pady=3)
    tk.Button(raiz, text='Registrar pago y generar ticket', command=cobrar,
              bg=VERDE, fg='white', pady=7).pack(fill='x', pady=3)
    tk.Button(raiz, text='Actualizar cuentas', command=actualizar).pack(fill='x', pady=3)
    tk.Button(raiz, text='Volver al menú', command=app.mostrar_menu).pack(fill='x', pady=3)
    actualizar()


def mostrar_reportes_t55(app):
    """T55: pantalla de reportes diarios y por periodo; utiliza T45/T46/T47."""
    if not app.sesion or app.sesion.get('rol') not in ('gerente', 'caja'):
        messagebox.showerror('Acceso denegado', 'Reportes disponibles para gerencia y caja.')
        return
    app.limpiar_pantalla()
    raiz = tk.Frame(app.marco, bg=FONDO, padx=14, pady=10)
    raiz.pack(fill='both', expand=True)
    tk.Label(raiz, text='Reportes de ventas cerradas', font=('Arial', 18, 'bold'),
             bg=FONDO, fg=AZUL).pack(anchor='w')
    tk.Label(raiz, text='Se usa la fecha de CIERRE de cuenta (T45), no la del pedido.',
             bg=FONDO).pack(anchor='w', pady=(3, 10))
    barra = tk.Frame(raiz, bg=FONDO)
    barra.pack(fill='x')
    dia_var = tk.StringVar(value=date.today().isoformat())
    tk.Label(barra, text='Resumen diario (AAAA-MM-DD)', bg=FONDO).pack(side='left')
    ttk.Entry(barra, textvariable=dia_var, width=15).pack(side='left', padx=7)
    resumen_var = tk.StringVar(value='Sin consulta')
    tabla = ttk.Treeview(raiz,
        columns=('id', 'fecha', 'mesa', 'pago', 'metodo', 'importe'), show='headings', height=13)
    for col, titulo, ancho in (
        ('id', 'Venta', 65), ('fecha', 'Fecha de cierre', 155), ('mesa', 'Mesa', 65),
        ('pago', 'Pago', 65), ('metodo', 'Método', 100), ('importe', 'Importe', 110)):
        tabla.heading(col, text=titulo)
        tabla.column(col, width=ancho, anchor='e' if col == 'importe' else 'w')
    resumen = tk.Label(raiz, textvariable=resumen_var, font=('Arial', 12, 'bold'),
                       bg=FONDO, fg=AZUL)

    def pintar(filas, total, titulo):
        tabla.delete(*tabla.get_children())
        for venta_id, fecha, mesa, pago, metodo, importe in filas:
            tabla.insert('', 'end', values=(venta_id, fecha, mesa, pago, metodo, _importe(importe)))
        resumen_var.set(f'{titulo}  |  Ventas: {len(filas)}  |  Total: {_importe(total)}')

    def consultar_dia():
        try:
            datos = consultar_dia_t55(dia_var.get())
        except (ValueError, TypeError) as error:
            messagebox.showwarning('Fecha inválida', str(error))
            return
        pintar(datos['ventas'], datos['total'], f"Día {datos['fecha']}")

    def consultar_rango(inicio, fin):
        try:
            datos = consultar_periodo_t47(inicio, fin)
        except (ValueError, TypeError) as error:
            messagebox.showwarning('Consulta inválida', str(error))
            return
        pintar(datos['filas'], datos['total'], f'Periodo {inicio} a {fin}')

    ttk.Button(barra, text='Consultar día', command=consultar_dia).pack(side='left')
    crear_filtros_t47(raiz, consultar_rango)
    tabla.pack(fill='both', expand=True, pady=(8, 4))
    resumen.pack(anchor='w', pady=7)
    tk.Button(raiz, text='Volver al menú', command=app.mostrar_menu).pack(fill='x', pady=5)
    consultar_dia()
