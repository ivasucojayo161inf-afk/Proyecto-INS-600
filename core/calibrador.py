
import time
import statistics


class Calibrador:

    def __init__(self, duracion=5, muestras_minimas=15):

        self.duracion = duracion
        self.muestras_minimas = muestras_minimas

        self.inicio = None

        self.muestras_ear = []
        self.muestras_yaw = []
        self.muestras_pitch = []

        self.calibrado = False

    def iniciar(self):

        self.inicio = time.monotonic()

        self.muestras_ear = []
        self.muestras_yaw = []
        self.muestras_pitch = []

        self.calibrado = False

    def agregar_muestra(self, ear, yaw, pitch):

        if self.inicio is None or self.calibrado:
            return False

        self.muestras_ear.append(ear)
        self.muestras_yaw.append(yaw)
        self.muestras_pitch.append(pitch)

        return True

    def finalizar(self):

        if len(self.muestras_ear) < self.muestras_minimas:
            return None

        ear_referencia = statistics.mean(self.muestras_ear)
        yaw_referencia = statistics.mean(self.muestras_yaw)
        pitch_referencia = statistics.mean(self.muestras_pitch)

        resultado = {
            "ear_referencia": ear_referencia,
            "umbral_ear": ear_referencia * 0.70,
            "yaw_referencia": yaw_referencia,
            "pitch_referencia": pitch_referencia
        }

        self.calibrado = True

        return resultado

    def obtener_progreso(self):

        if self.inicio is None:
            return 0

        transcurrido = time.monotonic() - self.inicio

        progreso = (transcurrido / self.duracion) * 100

        return min(progreso, 100)

    def tiempo_completado(self):

        if self.inicio is None:
            return False

        return (
            time.monotonic() - self.inicio
        ) >= self.duracion
