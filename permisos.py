"""
permisos.py - Estructura de roles y permisos del restaurante (Tarea 5)
Responsable: Juan Antonio
"""

ROLES_PERMISOS = {
    "gerente": {
        "descripcion": "Acceso total y configuración general",
        "permisos": [
            "Ver panel general de control",
            "Administrar cuentas de empleados",
            "Modificar cartas y precios del menú",
            "Consultar reportes de ventas y finanzas",
            "Monitorear mesas y cocina en tiempo real"
        ]
    },
    "mesero": {
        "descripcion": "Gestión de mesas y comandas",
        "permisos": [
            "Consultar estado de mesas",
            "Crear nueva comanda para mesa",
            "Agregar platillos y bebidas",
            "Consultar estado de pedidos en cocina",
            "Solicitar cuenta a caja"
        ]
    },
    "cocina": {
        "descripcion": "Visualización y preparación de comandas",
        "permisos": [
            "Ver comandas en cola pendientes",
            "Marcar comanda 'En preparación'",
            "Marcar comanda 'Lista para servir'",
            "Reportar insumos agotados"
        ]
    },
    "caja": {
        "descripcion": "Cobros, tickets y corte",
        "permisos": [
            "Consultar cuenta total de mesa",
            "Registrar pagos en efectivo y tarjeta",
            "Generar e imprimir tickets",
            "Realizar corte de caja"
        ]
    },
    "almacen": {
        "descripcion": "Control de insumos e inventario",
        "permisos": [
            "Consultar stock de ingredientes",
            "Registrar entrada de mercancía",
            "Ajustar mermas y productos",
            "Generar alertas de stock mínimo"
        ]
    }
}

def obtener_permisos_rol(rol: str) -> list:
    """Retorna la lista de permisos autorizados según el puesto."""
    return ROLES_PERMISOS.get(rol.lower().strip(), {}).get("permisos", ["Sin permisos"])
