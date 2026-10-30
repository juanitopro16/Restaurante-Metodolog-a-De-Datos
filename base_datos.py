"""
base_datos.py - Módulo de persistencia y seguridad (Tareas 2 y 3)
Responsable: Javier Vidaña (JV)
"""

import sqlite3
import hashlib

DB_NAME = "restaurante.db"

def hashear_password(password: str) -> str:
    """Tarea 2 (E1-2): Genera el hash SHA-256 para proteger contraseñas."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def inicializar_base_de_datos():
    """Tarea 2 (E1-2): Crea la tabla de usuarios e inserta cuentas iniciales de prueba."""
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        usuarios_prueba = [
            ("Juan Gerente", "gerente1", hashear_password("admin123"), "gerente"),
            ("Carlos Mesero", "mesero1", hashear_password("mesero123"), "mesero"),
            ("Ana Cocina", "cocina1", hashear_password("cocina123"), "cocina"),
            ("Roberto Caja", "caja1", hashear_password("caja123"), "caja"),
            ("Lucía Almacén", "almacen1", hashear_password("almacen123"), "almacen")
        ]
        cursor.executemany("""
            INSERT INTO usuarios (nombre_completo, usuario, password_hash, rol)
            VALUES (?, ?, ?, ?)
        """, usuarios_prueba)
        conexion.commit()

    conexion.close()

def verificar_credenciales(usuario: str, password_plana: str):
    """
    Tarea 3 (E1-3): Valida usuario y contraseña comparando hashes.
    Retorna diccionario con datos del empleado o None si es inválido.
    """
    conexion = sqlite3.connect(DB_NAME)
    cursor = conexion.cursor()

    hash_ingresado = hashear_password(password_plana)
    cursor.execute("""
        SELECT id, nombre_completo, usuario, rol 
        FROM usuarios 
        WHERE usuario = ? AND password_hash = ?
    """, (usuario.strip(), hash_ingresado))

    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        return {
            "id": resultado[0],
            "nombre": resultado[1],
            "usuario": resultado[2],
            "rol": resultado[3]
        }
    return None

if __name__ == "__main__":
    inicializar_base_de_datos()
    print("Base de datos local inicializada correctamente.")
