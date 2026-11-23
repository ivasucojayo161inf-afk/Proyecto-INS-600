
import sqlite3
from pathlib import Path
from datetime import datetime


class BaseDatos:

    def __init__(self):

        # Crear la carpeta de almacenamiento si no existe
        ruta_proyecto = Path(__file__).resolve().parent.parent
        carpeta_datos = ruta_proyecto / "datos"

        carpeta_datos.mkdir(exist_ok=True)

        self.ruta = carpeta_datos / "eventos.db"

        self.crear_tabla()

    def conectar(self):

        return sqlite3.connect(
            self.ruta,
            timeout=10
        )

    def crear_tabla(self):

        conexion = self.conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora TEXT NOT NULL,
                    tipo_evento TEXT NOT NULL,
                    ear REAL,
                    yaw REAL,
                    pitch REAL
                )
            """)

            conexion.commit()

        finally:

            conexion.close()

        print("Base de datos inicializada correctamente.")

    def registrar_evento(
        self,
        tipo_evento,
        ear=None,
        yaw=None,
        pitch=None
    ):

        fecha_hora = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )

        conexion = self.conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO eventos (
                    fecha_hora,
                    tipo_evento,
                    ear,
                    yaw,
                    pitch
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                fecha_hora,
                tipo_evento,
                ear,
                yaw,
                pitch
            ))

            conexion.commit()

            print(
                f"[HISTORIAL] {tipo_evento} registrado: "
                f"{fecha_hora}"
            )

            return True

        except sqlite3.Error as error:

            print(f"[ERROR BD] No se pudo registrar el evento: {error}")
            return False

        finally:

            conexion.close()

    def obtener_eventos(self, limite=100):

        conexion = self.conectar()

        try:

            cursor = conexion.cursor()

            cursor.execute("""
                SELECT
                    id,
                    fecha_hora,
                    tipo_evento,
                    ear,
                    yaw,
                    pitch
                FROM eventos
                ORDER BY id DESC
                LIMIT ?
            """, (limite,))

            return cursor.fetchall()

        finally:

            conexion.close()
