import time
import statistics


class Calibrador:
    """Calibracion guiada en tres fases usando las metricas del proyecto."""

    PASOS = [
        {"nombre": "POSICION NORMAL", "instruccion": "Mira al frente con los ojos abiertos", "duracion": 4},
        {"nombre": "CIERRE DE OJOS", "instruccion": "Cierra los ojos suavemente", "duracion": 3},
        {"nombre": "MOVIMIENTO DE CABEZA", "instruccion": "Gira a ambos lados y mueve ligeramente la cabeza arriba y abajo", "duracion": 5},
    ]

    def __init__(self, duracion=5, muestras_minimas=15):
        self.duracion = duracion
        self.muestras_minimas = muestras_minimas
        self.inicio = None
        self.paso = 0
        self.muestras = {"normal": [], "cerrado": [], "movimiento": []}
        self.calibrado = False
        self.terminado = False

    def iniciar(self):
        self.inicio = time.monotonic()
        self.paso = 0
        self.muestras = {"normal": [], "cerrado": [], "movimiento": []}
        self.calibrado = False
        self.terminado = False

    def cancelar(self):
        self.inicio = None
        self.terminado = True

    def agregar_muestra(self, ear, yaw, pitch):
        if self.inicio is None or self.terminado:
            return False
        claves = ("normal", "cerrado", "movimiento")
        self.muestras[claves[self.paso]].append((float(ear), float(yaw), float(pitch)))
        return True

    def obtener_fase(self):
        return self.PASOS[self.paso]

    def obtener_progreso(self):
        if self.inicio is None:
            return 0
        transcurrido = time.monotonic() - self.inicio
        duracion_total = sum(p["duracion"] for p in self.PASOS)
        completado = sum(p["duracion"] for p in self.PASOS[:self.paso])
        actual = min(transcurrido, self.PASOS[self.paso]["duracion"])
        return min(100, int(((completado + actual) / duracion_total) * 100))

    def tiempo_completado(self):
        if self.inicio is None or self.terminado:
            return False
        return time.monotonic() - self.inicio >= self.PASOS[self.paso]["duracion"]

    def avanzar(self):
        """Avanza de fase. Devuelve None hasta terminar; al final devuelve resultado."""
        if not self.tiempo_completado():
            return None

        claves = ("normal", "cerrado", "movimiento")
        if len(self.muestras[claves[self.paso]]) < self.muestras_minimas:
            self.terminado = True
            return {"correcto": False, "mensaje": "No se capturaron suficientes muestras. Mantén el rostro visible e inténtalo otra vez."}

        if self.paso < len(self.PASOS) - 1:
            self.paso += 1
            self.inicio = time.monotonic()
            return {"siguiente": True}

        return self.finalizar()

    def finalizar(self):
        normal = self.muestras["normal"]
        cerrado = self.muestras["cerrado"]
        movimiento = self.muestras["movimiento"]

        ear_abierto = statistics.median(m[0] for m in normal)
        ear_cerrado = statistics.median(m[0] for m in cerrado)
        yaw_referencia = statistics.median(m[1] for m in normal)
        pitch_referencia = statistics.median(m[2] for m in normal)

        diferencia = ear_abierto - ear_cerrado
        if diferencia < 0.025:
            self.terminado = True
            return {"correcto": False, "mensaje": "No se distinguió correctamente entre ojos abiertos y cerrados. Repite la calibración."}

        desviacion_yaw = max(abs(m[1] - yaw_referencia) for m in movimiento)
        desviacion_pitch = max(abs(m[2] - pitch_referencia) for m in movimiento)

        resultado = {
            "ear_referencia": ear_abierto,
            "umbral_ear": ear_cerrado + 0.45 * diferencia,
            "yaw_referencia": yaw_referencia,
            "pitch_referencia": pitch_referencia,
            "umbral_yaw": max(8.0, min(25.0, desviacion_yaw * 0.45)),
            "umbral_pitch": max(8.0, min(25.0, desviacion_pitch * 0.45)),
        }
        self.calibrado = True
        self.terminado = True
        return {"correcto": True, "resultado": resultado, "mensaje": "Calibración exitosa. Parámetros ajustados automáticamente."}
