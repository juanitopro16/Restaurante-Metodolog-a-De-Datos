# ================================================================
# RESPONSABILIDAD / MÓDULO: Equipo Sprint 3 y Juan Antonio | Sprints 3–4 | insumos, cierre, entregas y compras
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
# Juan Antonio — Sprint 4 T45: registrar ventas al cerrar cuenta, además de liberar mesa.
from juan_sprint4 import cerrar_mesa_t45
"""Pantallas nuevas del Sprint 3; conservan pantallas originales de Javier y Pato."""
import tkinter as tk
from tkinter import ttk,messagebox
from sprint3_nuevo import (marcar_listo,listar_listos,marcar_entregado,registrar_insumo,
                           modificar_minimo,registrar_entrada,cuenta_mesa,cuentas_pendientes,
                           cerrar_mesa,cambiar_estado_compra)
from pato_almacen import listar_existencias,listar_ordenes_compra
from base_datos import listar_mesas,listar_detalle_pedido


def _encabezado(app,titulo):
    app.limpiar_pantalla()
    tk.Label(app.marco,text=titulo,font=('Arial',15,'bold')).pack(pady=7)

def _boton(app,text,func):
    tk.Button(app.marco,text=text,command=func).pack(fill='x',pady=3)

def _mensaje(resultado):
    ok,msg=resultado
    (messagebox.showinfo if ok else messagebox.showwarning)('Sistema',msg)

# Aarón T25: transición de preparación a listo.
def mostrar_cocina_listos(app):
    if not app.sesion or app.sesion['rol']!='cocina': return
    _encabezado(app,'Cocina · pedidos en preparación (T25)')
    tabla=ttk.Treeview(app.marco,columns=('mesa',),show='tree headings',height=12)
    tabla.heading('#0',text='Folio');tabla.heading('mesa',text='Mesa');tabla.pack(fill='both',expand=True)
    def actualizar():
        for x in tabla.get_children():tabla.delete(x)
        from base_datos import conectar
        with conectar() as c:
            for folio,mesa in c.execute("SELECT p.id,m.numero FROM pedidos p JOIN mesas m ON m.id=p.mesa_id WHERE p.estado='En preparación' ORDER BY p.id"):
                tabla.insert('', 'end',iid=str(folio),text=str(folio),values=(mesa,))
    def listo():
        if not tabla.selection():messagebox.showwarning('Cocina','Selecciona un pedido.');return
        _mensaje(marcar_listo(int(tabla.selection()[0])));actualizar()
    _boton(app,'Marcar pedido Listo (T25)',listo);_boton(app,'Actualizar',actualizar)
    app.volver_menu();actualizar()

# Aarón T26/T27: bandeja de avisos para mesero, con actualización manual.
def mostrar_entregas(app):
    if not app.sesion or app.sesion['rol']!='mesero':return
    _encabezado(app,'Mesero · pedidos listos (T26–T27)')
    tk.Label(app.marco,text='Avisos de cocina. Pulsa Actualizar para ver pedidos nuevos.').pack()
    tabla=ttk.Treeview(app.marco,columns=('mesa',),show='tree headings',height=10)
    tabla.heading('#0',text='Folio');tabla.heading('mesa',text='Mesa');tabla.pack(fill='both',expand=True)
    detalle=tk.Text(app.marco,height=6);detalle.pack(fill='both',expand=True)
    def actualizar():
        for x in tabla.get_children():tabla.delete(x)
        for folio,mesa in listar_listos():tabla.insert('','end',iid=str(folio),text=str(folio),values=(mesa,))
        detalle.delete('1.0','end')
    def ver(event=None):
        detalle.delete('1.0','end')
        if tabla.selection():
            for _,nombre,cantidad,_,nota in listar_detalle_pedido(int(tabla.selection()[0])):
                detalle.insert('end',f'{cantidad} x {nombre} {nota}\n')
    def entregar():
        if not tabla.selection():messagebox.showwarning('Mesero','Selecciona un pedido.');return
        _mensaje(marcar_entregado(int(tabla.selection()[0])));actualizar()
    tabla.bind('<<TreeviewSelect>>',ver)
    _boton(app,'Marcar Entregado (T27)',entregar);_boton(app,'Actualizar avisos (T26)',actualizar)
    app.volver_menu();actualizar()

# Said T35-38: captura real de insumos, mínimos y entradas.
def mostrar_insumos_said(app):
    if not app.sesion or app.sesion['rol'] not in ('almacen','gerente'):return
    _encabezado(app,'Almacén · catálogo y entradas (T35–T38)')
    tabla=ttk.Treeview(app.marco,columns=('unidad','saldo','minimo'),show='tree headings',height=7)
    for col,label in [('#0','Insumo'),('unidad','Unidad'),('saldo','Existencia'),('minimo','Mínimo')]:tabla.heading(col,text=label)
    tabla.column('#0',width=150);tabla.column('unidad',width=65);tabla.column('saldo',width=90);tabla.column('minimo',width=80)
    tabla.pack(fill='both',expand=True)
    formulario=tk.Frame(app.marco);formulario.pack(fill='x')
    campos={}
    for i,(clave,etiqueta) in enumerate([('nombre','Nombre'),('unidad','Unidad (kg/L/pza)'),('existencia','Existencia inicial'),('minimo','Mínimo'),('cantidad','Cantidad entrada')]):
        tk.Label(formulario,text=etiqueta).grid(row=i,column=0,sticky='w')
        e=tk.Entry(formulario);e.grid(row=i,column=1,sticky='ew');campos[clave]=e
    formulario.columnconfigure(1,weight=1)
    campos['existencia'].insert(0,'0');campos['minimo'].insert(0,'0')
    def actualizar():
        for x in tabla.get_children():tabla.delete(x)
        for id_,nombre,existencia,unidad,minimo in listar_existencias():
            tabla.insert('','end',iid=str(id_),text=nombre,values=(unidad,existencia,minimo))
    def id_seleccionado():
        if not tabla.selection():messagebox.showwarning('Almacén','Selecciona un insumo de la tabla.');return None
        return int(tabla.selection()[0])
    def crear():
        _mensaje(registrar_insumo(*(campos[k].get() for k in ('nombre','unidad','existencia','minimo'))));actualizar()
    def minimo():
        id_=id_seleccionado()
        if id_ is not None:_mensaje(modificar_minimo(id_,campos['minimo'].get()));actualizar()
    def entrada():
        id_=id_seleccionado()
        if id_ is not None:_mensaje(registrar_entrada(id_,campos['cantidad'].get()));actualizar()
    _boton(app,'Registrar insumo (T35–T37)',crear)
    _boton(app,'Cambiar mínimo seleccionado (T37)',minimo)
    _boton(app,'Registrar entrada seleccionada (T38)',entrada)
    _boton(app,'Actualizar existencias',actualizar);app.volver_menu();actualizar()

# Juan T28-30,34: desglose y cierre; Javier sigue cobrando en su propia pantalla.
def mostrar_cuentas_juan(app):
    if not app.sesion or app.sesion['rol'] not in ('caja','gerente'):return
    _encabezado(app,'Caja · consumos, cuentas y cierre (T28–T30, T34)')
    tabla=ttk.Treeview(app.marco,columns=('mesa','total'),show='tree headings',height=7)
    for col,t in [('#0','ID mesa'),('mesa','Mesa'),('total','Pendiente $')]:tabla.heading(col,text=t)
    tabla.pack(fill='both',expand=True)
    detalle=tk.Text(app.marco,height=9);detalle.pack(fill='both',expand=True)
    def actualizar():
        for x in tabla.get_children():tabla.delete(x)
        for mid,numero,total in cuentas_pendientes():tabla.insert('','end',iid=str(mid),text=str(mid),values=(numero,total))
        detalle.delete('1.0','end')
    def ver(event=None):
        detalle.delete('1.0','end')
        if tabla.selection():
            cuenta=cuenta_mesa(int(tabla.selection()[0]))
            for l in cuenta['lineas']:
                detalle.insert('end',f"{l['cantidad']} x {l['producto']} · ${l['precio']} = ${l['importe']}\n")
            detalle.insert('end',f"SUBTOTAL/TOTAL: ${cuenta['total']}\n")
    def cerrar():
        # Puede cerrarse después del cobro, cuando ya no aparece en la lista de pendientes.
        from tkinter.simpledialog import askinteger
        numero=askinteger('Cerrar mesa','Número de mesa ya pagada:')
        if numero is None:return
        mesa=next((m for m in listar_mesas() if m[1]==numero),None)
        if mesa is None:messagebox.showwarning('Caja','Mesa inexistente.');return
        _mensaje(cerrar_mesa_t45(mesa[0]));actualizar()
    tabla.bind('<<TreeviewSelect>>',ver)
    _boton(app,'Actualizar cuentas pendientes (T30)',actualizar)
    _boton(app,'Cerrar cuenta pagada y liberar mesa (T34)',cerrar)
    _boton(app,'Abrir cobro de Javier (T31–T33)',lambda: __import__('javier_sprint4').mostrar_caja_t53(app))
    app.volver_menu();actualizar()

# Aarón T44: solicitar y recibir; recepción añade inventario una sola vez.
def mostrar_compras_aaron(app):
    if not app.sesion or app.sesion['rol'] not in ('almacen','gerente'):return
    _encabezado(app,'Compras · solicitar y recibir (T44)')
    tabla=ttk.Treeview(app.marco,columns=('proveedor','fecha','estado'),show='tree headings',height=12)
    for col,t in [('#0','Folio'),('proveedor','Proveedor'),('fecha','Fecha'),('estado','Estado')]:tabla.heading(col,text=t)
    tabla.pack(fill='both',expand=True)
    def actualizar():
        for x in tabla.get_children():tabla.delete(x)
        for folio,proveedor,fecha,estado,_ in listar_ordenes_compra():
            tabla.insert('','end',iid=str(folio),text=str(folio),values=(proveedor,fecha,estado))
    def cambiar(estado):
        if not tabla.selection():messagebox.showwarning('Compras','Selecciona una orden.');return
        if estado=='Recibida' and not messagebox.askyesno('Confirmar','¿Recibiste todos los ingredientes? Se sumarán al inventario una sola vez.'):
            return
        _mensaje(cambiar_estado_compra(int(tabla.selection()[0]),estado));actualizar()
    _boton(app,'Marcar Solicitada',lambda:cambiar('Solicitada'))
    _boton(app,'Marcar Recibida y sumar inventario',lambda:cambiar('Recibida'))
    _boton(app,'Actualizar órdenes',actualizar);app.volver_menu();actualizar()
