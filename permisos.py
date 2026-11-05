# ================================================================
# SPRINT 1 - TAREA E1-5
# Nombre: Definir los permisos de mesero, cocina, caja, almacén y gerente
# Responsable: Juan Antonio Ibarra Hernández
# ================================================================

# Aquí se guardan las opciones que puede utilizar cada puesto.
# Los mismos permisos se usan para mostrar los menús y revisar los accesos.

roles_permisos = {
    "gerente": [
        "Consultar el estado general del restaurante",
        "Administrar empleados",
        "Modificar productos y precios",
        "Consultar reportes de ventas",
    ],
    "mesero": [
        "Consultar mesas",
        "Registrar comandas",
        "Agregar productos a los pedidos",
        "Solicitar la cuenta",
    ],
    "cocina": [
        "Consultar comandas pendientes",
        "Marcar pedidos en preparación",
        "Marcar pedidos como listos",
    ],
    "caja": [
        "Consultar cuentas",
        "Registrar pagos",
        "Generar tickets",
    ],
    "almacen": [
        "Consultar existencias",
        "Registrar entradas de productos",
        "Avisar cuando falten insumos",
    ],
}


# Devuelve los puestos que se pueden asignar a un empleado.
def obtener_roles():
    return list(roles_permisos.keys())


# Busca las opciones de un puesto. Si no existe, devuelve una lista vacía.
def obtener_permisos(rol):
    return roles_permisos.get(rol.lower().strip(), [])
