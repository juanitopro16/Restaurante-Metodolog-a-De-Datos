# ================================================================
# RESPONSABILIDAD / MÓDULO: Javier Tadeo | Sprint 3 | interfaces anteriores de caja y proveedores
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Pantallas exclusivas de Javier Tadeo, Sprint 3 T31/T32/T33/T41.
Se llaman desde main.py sin reemplazar pantallas de otros compañeros.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from javier_caja_proveedores import (
    listar_cuentas_por_cobrar, consultar_cuenta, calcular_cambio,
    registrar_pago, generar_texto_ticket, registrar_proveedor, listar_proveedores,
)


def mostrar_caja_javier(app):
    """T31: permite elegir una cuenta entregada y registrar Efectivo/Tarjeta.
    T32: calcula cambio; T33: genera y muestra el comprobante.
    """
    if not app.sesion or app.sesion['rol']!='caja':
        messagebox.showerror('Acceso denegado','Solo el personal de caja puede cobrar.')
        return
    app.limpiar_pantalla()
    marco=app.marco
    tk.Label(marco,text='Caja: pagos y tickets (T31–T33)',font=('Arial',15,'bold')).pack(pady=6)
    tk.Label(marco,text='Se cobran únicamente pedidos marcados Entregado.').pack()
    tabla=ttk.Treeview(marco,columns=('mesa','total'),show='headings',height=6,selectmode='browse')
    tabla.heading('mesa',text='Mesa');tabla.heading('total',text='Total pendiente')
    tabla.column('mesa',width=120);tabla.column('total',width=180)
    tabla.pack(fill='x',pady=5)
    detalle=tk.Text(marco,height=6,state='disabled',wrap='word')
    detalle.pack(fill='both',expand=True)
    tk.Label(marco,text='Método de pago').pack(anchor='w')
    metodo=tk.StringVar(value='Efectivo')
    ttk.Combobox(marco,textvariable=metodo,values=['Efectivo','Tarjeta'],state='readonly').pack(fill='x')
    tk.Label(marco,text='Dinero recibido (para efectivo)').pack(anchor='w')
    efectivo=tk.Entry(marco); efectivo.pack(fill='x')
    aviso=tk.StringVar(value='Selecciona una mesa con consumo entregado.')
    tk.Label(marco,textvariable=aviso,wraplength=530).pack()

    def seleccionado():
        eleccion=tabla.selection()
        return int(eleccion[0]) if eleccion else None

    def ver_detalle(event=None):
        mesa_id=seleccionado()
        detalle.config(state='normal');detalle.delete('1.0','end')
        if mesa_id is not None:
            cuenta=consultar_cuenta(mesa_id)
            for linea in cuenta['lineas']:
                detalle.insert('end',f"{linea['cantidad']} x {linea['producto']} · ${linea['precio']} = ${linea['importe']}\n")
            detalle.insert('end',f"TOTAL: ${cuenta['total']}\n")
        detalle.config(state='disabled')

    def actualizar():
        for fila in tabla.get_children():tabla.delete(fila)
        for mid,numero,total in listar_cuentas_por_cobrar():
            tabla.insert('','end',iid=str(mid),values=(numero,f'${total}'))
        ver_detalle()
        aviso.set('Selecciona una mesa.' if tabla.get_children() else
                  'No hay pedidos Entregados pendientes. Primero debe completarse T27.')

    def cambio_previo():
        mid=seleccionado()
        if mid is None:
            messagebox.showwarning('Caja','Selecciona una mesa.');return
        total=consultar_cuenta(mid)['total']
        if metodo.get()=='Tarjeta':
            aviso.set(f'Pago con tarjeta: ${total}. No se procesa la tarjeta en línea.')
        else:
            ok,mensaje,cambio=calcular_cambio(total,efectivo.get())
            aviso.set(f'Cambio: ${cambio}' if ok else mensaje)

    def cobrar():
        mid=seleccionado()
        if mid is None:
            messagebox.showwarning('Caja','Selecciona una mesa.');return
        ok,mensaje,folio=registrar_pago(mid,metodo.get(),efectivo.get())
        if not ok:
            messagebox.showwarning('Pago',mensaje);return
        actualizar();aviso.set(f'Pago #{folio} registrado correctamente.')
        messagebox.showinfo('Pago correcto',f'Pago registrado. Folio: {folio}')
        mostrar_ticket_javier(app.ventana,folio)

    tabla.bind('<<TreeviewSelect>>',ver_detalle)
    tk.Button(marco,text='Calcular cambio / consultar importe (T32)',command=cambio_previo).pack(fill='x',pady=2)
    tk.Button(marco,text='Registrar pago y generar ticket (T31/T33)',command=cobrar).pack(fill='x',pady=2)
    tk.Button(marco,text='Actualizar cuentas',command=actualizar).pack(fill='x',pady=2)
    app.volver_menu()
    actualizar()


def mostrar_ticket_javier(ventana,pago_id):
    """T33: abre ventana con el ticket y deja guardarlo como TXT."""
    contenido=generar_texto_ticket(pago_id)
    if contenido is None:
        messagebox.showerror('Ticket','No se encontró el pago.');return
    win=tk.Toplevel(ventana)
    win.title(f'Ticket T33 - Pago {pago_id}')
    win.geometry('520x470')
    area=tk.Text(win,wrap='word',font=('Courier New',10))
    area.pack(fill='both',expand=True,padx=10,pady=10)
    area.insert('1.0',contenido);area.config(state='disabled')
    def guardar():
        ruta=filedialog.asksaveasfilename(parent=win,defaultextension='.txt',initialfile=f'ticket_{pago_id}.txt',
                                         filetypes=[('Archivo de texto','*.txt')])
        if ruta:
            try:
                with open(ruta,'w',encoding='utf-8') as f:f.write(contenido)
                messagebox.showinfo('Ticket','Archivo guardado correctamente.',parent=win)
            except OSError as e:
                messagebox.showerror('Ticket',str(e),parent=win)
    tk.Button(win,text='Guardar ticket TXT',command=guardar).pack(fill='x',padx=10,pady=5)


def mostrar_proveedores_javier(app):
    """T41: captura y consulta proveedores para T43 (órdenes futuras de Pato)."""
    if not app.sesion or app.sesion['rol'] not in ('almacen','gerente'):
        messagebox.showerror('Acceso denegado','Esta opción es de almacén o gerencia.')
        return
    app.limpiar_pantalla()
    marco=app.marco
    tk.Label(marco,text='Catálogo de proveedores (T41)',font=('Arial',16,'bold')).pack(pady=8)
    datos={}
    for campo in ('Nombre','Teléfono','Correo'):
        tk.Label(marco,text=campo).pack(anchor='w')
        entrada=tk.Entry(marco);entrada.pack(fill='x',pady=2)
        datos[campo]=entrada
    tabla=ttk.Treeview(marco,columns=('id','nombre','telefono','correo'),show='headings',height=8)
    for col,titulo in [('id','ID'),('nombre','Nombre'),('telefono','Teléfono'),('correo','Correo')]:
        tabla.heading(col,text=titulo)
        tabla.column(col,width=45 if col=='id' else 140)
    tabla.pack(fill='both',expand=True,pady=10)
    def actualizar():
        for item in tabla.get_children():tabla.delete(item)
        for fila in listar_proveedores():tabla.insert('','end',values=fila)
    def guardar():
        ok,mensaje=registrar_proveedor(datos['Nombre'].get(),datos['Teléfono'].get(),datos['Correo'].get())
        if not ok:
            messagebox.showwarning('Proveedor',mensaje);return
        for entrada in datos.values():entrada.delete(0,'end')
        actualizar();messagebox.showinfo('Proveedor',mensaje)
    tk.Button(marco,text='Guardar proveedor',command=guardar).pack(fill='x',pady=3)
    tk.Button(marco,text='Actualizar proveedores',command=actualizar).pack(fill='x',pady=3)
    app.volver_menu();actualizar()
