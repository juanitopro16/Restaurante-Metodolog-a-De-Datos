# ================================================================
# RESPONSABILIDAD / MÓDULO: Said Jesús (tareas asignadas) | Sprint 4 T49 T50 T62 T64 | historial, login y empleados; código generado con IA
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Tareas asignadas a Said Jesús, implementadas con ayuda de IA: T49 T50 T62 T64.
Complemento para el Sprint 3 y aaron_sprint4.py. No sustituye base_datos.py.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from base_datos import conectar, listar_empleados, registrar_usuario, modificar_empleado, desactivar_empleado, activar_empleado, validar_credenciales
from permisos import obtener_roles
from aaron_sprint4 import obtener_historial_pedido

AZUL='#183153'; FONDO='#F3F7FC'; VERDE='#147D64'


def buscar_pedidos_t49(fecha=None,mesa=None,folio=None,limite=200):
    """T49: filtra pedidos PAGADOS; fecha corresponde a fecha de pago, no de pedido."""
    if fecha:
        fecha=date.fromisoformat(fecha).isoformat()
    if mesa is not None and str(mesa).strip():
        mesa=int(mesa)
        if mesa<=0: raise ValueError('La mesa debe ser positiva.')
    else: mesa=None
    if folio is not None and str(folio).strip():
        folio=int(folio)
        if folio<=0: raise ValueError('El folio debe ser positivo.')
    else: folio=None
    limite=max(1,min(1000,int(limite)))
    sql='''SELECT p.id,m.numero,pg.fecha,pg.metodo,pg.total,pg.id
        FROM pedidos p JOIN mesas m ON m.id=p.mesa_id
        JOIN pago_pedidos_javier pp ON pp.pedido_id=p.id
        JOIN pagos_javier pg ON pg.id=pp.pago_id WHERE 1=1'''
    args=[]
    if fecha: sql+=' AND substr(pg.fecha,1,10)=?';args.append(fecha)
    if mesa is not None: sql+=' AND m.numero=?';args.append(mesa)
    if folio is not None: sql+=' AND p.id=?';args.append(folio)
    sql+=' ORDER BY pg.fecha DESC,p.id DESC LIMIT ?';args.append(limite)
    with conectar() as c: return c.execute(sql,args).fetchall()


def detalle_historico_t50(folio):
    """T50: devuelve detalle y pago de Aarón; respeta pagos compartidos por varios pedidos."""
    folio=int(folio)
    if folio<=0: raise ValueError('Folio inválido.')
    return obtener_historial_pedido(folio)


def mostrar_historial_said(app):
    """T49/T50: búsqueda visual y vista de detalle, sin modificar ventas ni pedidos."""
    if not app.sesion or app.sesion['rol'] not in ('gerente','caja'):
        messagebox.showerror('Acceso denegado','Historial exclusivo de gerencia y caja.');return
    app.limpiar_pantalla();r=tk.Frame(app.marco,bg=FONDO,padx=12,pady=12);r.pack(fill='both',expand=True)
    tk.Label(r,text='Historial de pedidos cobrados',font=('Arial',17,'bold'),fg=AZUL,bg=FONDO).pack(anchor='w')
    filtros=tk.Frame(r,bg=FONDO);filtros.pack(fill='x',pady=8)
    entradas={}
    for i,(clave,titulo) in enumerate((('fecha','Fecha pago AAAA-MM-DD'),('mesa','Mesa'),('folio','Folio'))):
        tk.Label(filtros,text=titulo,bg=FONDO).grid(row=0,column=i,sticky='w',padx=4)
        e=tk.Entry(filtros,width=20 if i==0 else 10);e.grid(row=1,column=i,padx=4);entradas[clave]=e
    tabla=ttk.Treeview(r,columns=('folio','mesa','fecha','metodo','total','pago'),show='headings',height=10)
    for c,t in (('folio','Folio'),('mesa','Mesa'),('fecha','Fecha pago'),('metodo','Método'),('total','Total cobro'),('pago','Pago ID')):
        tabla.heading(c,text=t);tabla.column(c,width=100)
    tabla.pack(fill='both',expand=True)
    detalle=tk.Text(r,height=12,wrap='word');detalle.pack(fill='both',expand=True,pady=6)
    def buscar():
        try: filas=buscar_pedidos_t49(**{k:e.get().strip() or None for k,e in entradas.items()})
        except (ValueError,TypeError) as error: messagebox.showwarning('Filtro incorrecto',str(error));return
        tabla.delete(*tabla.get_children())
        for f in filas: tabla.insert('','end',values=f)
    def ver(event=None):
        sel=tabla.selection()
        if not sel:return
        folio=tabla.item(sel[0],'values')[0]
        d=detalle_historico_t50(folio)
        detalle.delete('1.0','end')
        if not d: detalle.insert('end','Pedido sin pago asociado.');return
        p=d['pago']
        detalle.insert('end',f"PEDIDO #{d['folio']} | MESA {d['mesa']}\nPago #{p['id']} | {p['fecha']} | {p['metodo']}\nTotal del COBRO: ${p['total']} | Recibido: ${p['recibido']} | Cambio: ${p['cambio']}\n")
        if len(d['pedidos_del_pago'])>1:
            detalle.insert('end',f"AVISO: Este cobro incluye los pedidos {d['pedidos_del_pago']}. El total NO corresponde solo a este pedido.\n")
        detalle.insert('end','\nProductos de este pedido (catálogo actual):\n')
        for cant,nombre,nota in d['productos_pedido']:
            detalle.insert('end',f'  {cant} × {nombre} — {nota}\n')
        detalle.insert('end','\nLíneas originales del cobro (importe congelado):\n')
        for nombre,cant,precio,importe in d['lineas_pago']:
            detalle.insert('end',f'  {cant} × {nombre} a ${precio} = ${importe}\n')
    tabla.bind('<<TreeviewSelect>>',ver)
    tk.Button(filtros,text='Buscar',bg=VERDE,fg='white',command=buscar).grid(row=1,column=3,padx=5)
    tk.Button(r,text='Volver al menú',command=app.mostrar_menu).pack(fill='x')
    buscar()


def mostrar_login_said(app):
    """T62: rediseño de login; delega validación a app.iniciar_sesion existente."""
    app.limpiar_pantalla();app.sesion=None
    r=tk.Frame(app.marco,bg=FONDO,padx=35,pady=35);r.pack(fill='both',expand=True)
    tk.Label(r,text='Bienvenido',font=('Arial',24,'bold'),fg=AZUL,bg=FONDO).pack(pady=(30,6))
    tk.Label(r,text='Sistema de Comandas · Acceso de empleados',bg=FONDO).pack(pady=(0,24))
    tk.Label(r,text='Usuario',bg=FONDO).pack(anchor='w')
    app.entrada_usuario=tk.Entry(r,font=('Arial',13));app.entrada_usuario.pack(fill='x',pady=(4,15))
    tk.Label(r,text='Contraseña',bg=FONDO).pack(anchor='w')
    app.entrada_password=tk.Entry(r,show='*',font=('Arial',13));app.entrada_password.pack(fill='x',pady=(4,15))
    app.entrada_password.bind('<Return>',app.iniciar_sesion)
    tk.Button(r,text='Iniciar sesión',bg=VERDE,fg='white',font=('Arial',12,'bold'),pady=9,command=app.iniciar_sesion).pack(fill='x')
    tk.Label(r,text='Usa las credenciales asignadas por el administrador.',bg=FONDO).pack(pady=18)
    app.entrada_usuario.focus_set()


def mostrar_empleados_said(app):
    """T64: altas, cambios y bajas lógicas usando funciones existentes de Sprint 1/2."""
    if not app.sesion or app.sesion['rol']!='gerente':
        messagebox.showerror('Acceso denegado','Solo gerencia administra empleados.');return
    app.limpiar_pantalla();r=tk.Frame(app.marco,bg=FONDO,padx=12,pady=12);r.pack(fill='both',expand=True)
    tk.Label(r,text='Empleados y usuarios',font=('Arial',17,'bold'),bg=FONDO,fg=AZUL).pack(anchor='w',pady=6)
    tabla=ttk.Treeview(r,columns=('id','nombre','usuario','rol','activo'),show='headings',height=10)
    for c in ('id','nombre','usuario','rol','activo'):tabla.heading(c,text=c.capitalize());tabla.column(c,width=110)
    tabla.pack(fill='both',expand=True)
    campos=tk.Frame(r,bg=FONDO);campos.pack(fill='x',pady=10)
    entradas={}
    for i,(campo,titulo) in enumerate((('nombre','Nombre'),('usuario','Usuario (alta)'),('clave','Contraseña (alta)'))):
        tk.Label(campos,text=titulo,bg=FONDO).grid(row=0,column=i,sticky='w',padx=3)
        e=tk.Entry(campos,width=21,show='*' if campo=='clave' else '');e.grid(row=1,column=i,padx=3);entradas[campo]=e
    rol=tk.StringVar(value='mesero')
    ttk.Combobox(campos,textvariable=rol,values=obtener_roles(),state='readonly',width=14).grid(row=1,column=3,padx=3)
    def actualizar():
        tabla.delete(*tabla.get_children())
        for f in listar_empleados():tabla.insert('','end',values=(f[0],f[1],f[2],f[3],'Sí' if f[4] else 'No'))
    def seleccionado():
        s=tabla.selection()
        if not s:messagebox.showwarning('Empleados','Selecciona un empleado.');return None
        return tabla.item(s[0],'values')
    def cargar(event=None):
        f=seleccionado() if tabla.selection() else None
        if f:
            entradas['nombre'].delete(0,'end');entradas['nombre'].insert(0,f[1]);rol.set(f[3])
    def alta():
        ok,msg=registrar_usuario(entradas['nombre'].get(),entradas['usuario'].get(),entradas['clave'].get(),rol.get())
        messagebox.showinfo('Alta',msg) if ok else messagebox.showwarning('Alta',msg)
        actualizar()
    def editar():
        f=seleccionado()
        if not f:return
        ok,msg=modificar_empleado(int(f[0]),entradas['nombre'].get(),rol.get())
        messagebox.showinfo('Editar',msg) if ok else messagebox.showwarning('Editar',msg)
        actualizar()
    # SPRINT 4 - T64 | Said Jesús (responsable de tarea)
    # FUNCIÓN: cambiar acceso sin eliminar historial ni considerar el fin de turno.
    # Integración y corrección con asistencia de IA: botón contextual activar/desactivar.
    def cambiar_acceso():
        f = seleccionado()
        if not f:
            return
        empleado_id = int(f[0])
        activo = f[4] == 'Sí'
        if activo and empleado_id == app.sesion['id']:
            messagebox.showwarning('Empleados', 'No puedes desactivar tu propia sesión.')
            return
        accion = 'Desactivar' if activo else 'Activar'
        if not messagebox.askyesno('Confirmar', f'¿{accion.lower()} la cuenta de {f[1]}?'):
            return
        if activo:
            desactivar_empleado(empleado_id)
            ok, msg = True, 'Empleado desactivado. Ya no puede iniciar sesión.'
        else:
            ok, msg = activar_empleado(empleado_id)
        if ok:
            messagebox.showinfo('Empleados', msg)
        else:
            messagebox.showwarning('Empleados', msg)
        actualizar()
        # Volver a seleccionar el mismo registro tras refrescar la tabla.
        for item in tabla.get_children():
            if int(tabla.item(item, 'values')[0]) == empleado_id:
                tabla.selection_set(item)
                tabla.focus(item)
                tabla.see(item)
                break
        actualizar_boton()

    tabla.bind('<<TreeviewSelect>>', cargar)
    barra = tk.Frame(r, bg=FONDO)
    barra.pack(fill='x')
    tk.Button(barra, text='Crear empleado', command=alta).pack(side='left', padx=3, pady=5)
    tk.Button(barra, text='Guardar nombre y rol', command=editar).pack(side='left', padx=3, pady=5)
    boton_acceso = tk.Button(barra, text='Selecciona un empleado', command=cambiar_acceso, state='disabled')
    boton_acceso.pack(side='left', padx=3, pady=5)
    tk.Button(barra, text='Actualizar', command=actualizar).pack(side='left', padx=3, pady=5)

    def actualizar_boton(event=None):
        seleccion = tabla.selection()
        if not seleccion:
            boton_acceso.configure(text='Selecciona un empleado', state='disabled')
            return
        fila = tabla.item(seleccion[0], 'values')
        boton_acceso.configure(text='Desactivar' if fila[4] == 'Sí' else 'Activar', state='normal')

    tabla.bind('<<TreeviewSelect>>', lambda event: (cargar(event), actualizar_boton(event)))
    tk.Button(r,text='Volver al menú',command=app.mostrar_menu).pack(fill='x',pady=5)
    actualizar()
