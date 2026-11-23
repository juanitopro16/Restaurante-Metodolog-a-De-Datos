# ================================================================
# RESPONSABILIDAD / MÓDULO: Juan Antonio | Sprint 4 T45 T46 T51 T52 | ventas y pantallas de menú/mesas; código generado con IA
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
"""Juan Antonio — Sprint 4: T45, T46, T51, T52.
Módulo adicional para la estructura verificada de Sprint 3. No sobrescribe otros archivos.
"""
from datetime import date, datetime
from decimal import Decimal
import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import conectar, listar_mesas
from permisos import obtener_permisos

AZUL='#183153'; FONDO='#F3F7FC'; VERDE='#147D64'; ROJO='#B42318'


def preparar_ventas_t45():
    """T45: historial inmutable de pagos asociados a cierres; no altera tablas anteriores."""
    with conectar() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS ventas_cierre_s4 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pago_id INTEGER NOT NULL UNIQUE REFERENCES pagos_javier(id),
            mesa_id INTEGER NOT NULL REFERENCES mesas(id),
            fecha_cierre TEXT NOT NULL,
            total TEXT NOT NULL,
            metodo TEXT NOT NULL)''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_ventas_cierre_fecha ON ventas_cierre_s4(fecha_cierre)')


def cerrar_mesa_t45(mesa_id):
    """T45: cierra la mesa y registra cada pago sin duplicarlo, en UNA transacción.
    Conserva las reglas del cierre Sprint 3; se debe llamar desde el botón de cierre.
    """
    preparar_ventas_t45()
    c=conectar()
    try:
        c.execute('BEGIN IMMEDIATE')
        mesa=c.execute('SELECT estado FROM mesas WHERE id=?',(mesa_id,)).fetchone()
        if not mesa or mesa[0]!='Ocupada':
            return False,'La mesa no está ocupada.'
        pendientes=c.execute('''SELECT COUNT(*) FROM pedidos p WHERE p.mesa_id=? AND
            (p.estado!='Entregado' OR NOT EXISTS
            (SELECT 1 FROM pago_pedidos_javier pp WHERE pp.pedido_id=p.id))''',(mesa_id,)).fetchone()[0]
        if pendientes:
            return False,'Hay pedidos sin entregar o sin cobrar.'
        pagos=c.execute('''SELECT DISTINCT pg.id,pg.total,pg.metodo FROM pagos_javier pg
            JOIN pago_pedidos_javier pp ON pp.pago_id=pg.id
            JOIN pedidos p ON p.id=pp.pedido_id
            WHERE p.mesa_id=? AND pg.id NOT IN (SELECT pago_id FROM ventas_cierre_s4)''',(mesa_id,)).fetchall()
        if not pagos:
            return False,'No hay pagos nuevos para cerrar esta cuenta.'
        instante=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for pago_id,total,metodo in pagos:
            c.execute('INSERT INTO ventas_cierre_s4(pago_id,mesa_id,fecha_cierre,total,metodo) VALUES(?,?,?,?,?)',
                      (pago_id,mesa_id,instante,total,metodo))
        c.execute("UPDATE mesas SET estado='Libre' WHERE id=? AND estado='Ocupada'",(mesa_id,))
        c.commit()
        return True,f'Cuenta cerrada. {len(pagos)} pago(s) guardados como ventas.'
    finally:
        c.close()


def consultar_ventas_periodo_t45(inicio, fin):
    """Contrato compartido con T47 y T55: devuelve (filas, total Decimal).
    Fechas AAAA-MM-DD inclusivas; cada fila (venta_id, fecha, mesa, pago, método, importe).
    """
    inicio=date.fromisoformat(inicio).isoformat()
    fin=date.fromisoformat(fin).isoformat()
    if inicio>fin: raise ValueError('La fecha inicial no puede ser posterior a la final.')
    preparar_ventas_t45()
    with conectar() as c:
        filas=c.execute('''SELECT v.id,v.fecha_cierre,m.numero,v.pago_id,v.metodo,v.total
            FROM ventas_cierre_s4 v JOIN mesas m ON m.id=v.mesa_id
            WHERE v.fecha_cierre >= ? AND v.fecha_cierre < date(?, '+1 day')
            ORDER BY v.fecha_cierre,v.id''',(inicio,fin)).fetchall()
    total=sum((Decimal(str(f[5])) for f in filas),Decimal('0.00'))
    return filas,total


def resumen_diario_t46(dia=None):
    """T46: fecha, número de ventas y suma de ventas cerradas."""
    dia=dia or date.today().isoformat()
    filas,total=consultar_ventas_periodo_t45(dia,dia)
    return {'fecha':dia,'cantidad':len(filas),'total':total,'ventas':filas}


def mostrar_menu_juan_t51(app):
    """T51: interfaz de menú conservando la lista original de permisos por rol."""
    if not app.sesion: return
    app.limpiar_pantalla()
    marco=tk.Frame(app.marco,bg=FONDO,padx=20,pady=16);marco.pack(fill='both',expand=True)
    tk.Label(marco,text='SISTEMA DE COMANDAS',font=('Arial',21,'bold'),fg=AZUL,bg=FONDO).pack(anchor='w')
    tk.Label(marco,text=f"{app.sesion['nombre']}  ·  {app.sesion['rol'].capitalize()}",bg=FONDO).pack(anchor='w',pady=(2,16))
    opciones=obtener_permisos(app.sesion['rol'])
    for opcion in opciones:
        tk.Button(marco,text=opcion,anchor='w',font=('Arial',11),bg='white',fg=AZUL,
                  padx=14,pady=8,relief='groove',command=lambda o=opcion:app.ejecutar_opcion(o)).pack(fill='x',pady=3)
    tk.Button(marco,text='Cerrar sesión',bg=ROJO,fg='white',pady=8,command=app.cerrar_sesion).pack(fill='x',pady=(16,0))


def mostrar_mesas_juan_t52(app):
    """T52: consulta visual de mesas; para operaciones utiliza el método original."""
    if not app.sesion or 'Consultar mesas' not in obtener_permisos(app.sesion['rol']) and 'Crear pedidos' not in obtener_permisos(app.sesion['rol']):
        messagebox.showerror('Acceso denegado','Tu puesto no tiene acceso a mesas.');return
    app.limpiar_pantalla()
    marco=tk.Frame(app.marco,bg=FONDO,padx=16,pady=12);marco.pack(fill='both',expand=True)
    tk.Label(marco,text='Estado de las mesas',font=('Arial',18,'bold'),bg=FONDO,fg=AZUL).pack(anchor='w',pady=8)
    tabla=ttk.Treeview(marco,columns=('numero','estado'),show='headings',height=12)
    tabla.heading('numero',text='Mesa');tabla.heading('estado',text='Estado')
    tabla.column('numero',width=130);tabla.column('estado',width=220)
    tabla.tag_configure('Libre',background='#D8F5E5');tabla.tag_configure('Ocupada',background='#FFE4CC')
    tabla.pack(fill='both',expand=True)
    def refrescar():
        tabla.delete(*tabla.get_children())
        for m in listar_mesas():
            tabla.insert('','end',values=(m[1],m[2]),tags=(m[2],))
    refrescar()
    tk.Button(marco,text='Actualizar estados',command=refrescar,bg=VERDE,fg='white').pack(fill='x',pady=7)
    tk.Label(marco,text='Para abrir o editar pedidos, utiliza la pantalla original de mesas.',bg=FONDO).pack(anchor='w')
    tk.Button(marco,text='Abrir gestión original de mesas',command=app.mostrar_mesas).pack(fill='x',pady=5)
    tk.Button(marco,text='Volver al menú',command=app.mostrar_menu).pack(fill='x')
