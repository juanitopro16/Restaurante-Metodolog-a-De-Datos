# ================================================================
# RESPONSABILIDAD / MÓDULO: Juan Antonio y equipo | Sprints 1 y 4 | autorizaciones por rol
# Las funciones conservan sus comentarios de tarea cuando existen.
# ================================================================
# ================================================================
# SPRINT 1 - TAREA 5
# Nombre: Definir los permisos de mesero, cocina, caja, almacén y gerente
# Responsable: Juan Antonio Ibarra Hernández
# ¿QUÉ HACE? Define las opciones que aparecen según el puesto del usuario.
# ================================================================

roles_permisos = {
    "gerente": ["Administrar empleados", "Consultar y administrar productos", "Consultar mesas", "Administrar proveedores", "Consultar consumos y cerrar mesas", "Catálogo y entradas de insumos", "Recepción de órdenes de compra"],  # Javier T41
    "mesero": ["Consultar mesas", "Crear pedidos", "Pedidos listos para entregar"],
    "cocina": ["Consultar comandas pendientes", "Pedidos en preparación / Listos"],
    "caja": ["Consultar cuentas", "Consultar consumos y cerrar mesas"],
    "almacen": ["Consultar existencias", "Administrar proveedores", "Catálogo y entradas de insumos", "Recepción de órdenes de compra"],  # Javier T41
}

def obtener_roles():
    # Devuelve los puestos disponibles para asignarlos a un empleado.
    return list(roles_permisos.keys())

def obtener_permisos(rol):
    # Si el puesto no existe, no se le concede ninguna opción.
    return roles_permisos.get(rol.lower().strip(), [])

# ================================================================
# SPRINT 4 — Said Jesús T49/T50; Javier T47/T55.
# Permisos añadidos sin abrir acceso a meseros, cocina ni almacén.
# ================================================================
for _rol in ("gerente", "caja"):
    for _opcion in ("Consultar historial de pedidos", "Reportes de ventas"):
        if _opcion not in roles_permisos[_rol]:
            roles_permisos[_rol].append(_opcion)
