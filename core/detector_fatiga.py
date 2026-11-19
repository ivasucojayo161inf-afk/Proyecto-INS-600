
import math
import time


class DetectorFatiga:

    def __init__(self, umbral_ear=0.21, tiempo_cierre=2.0):
        self.umbral_ear = umbral_ear
        self.tiempo_cierre = tiempo_cierre
        self.inicio_cierre = None

        self.ojo_izquierdo = [33, 160, 158, 133, 153, 144]
        self.ojo_derecho = [362, 385, 387, 263, 373, 380]

    def calcular_ear(self, puntos, indices):

        p1, p2, p3, p4, p5, p6 = [
            puntos[i] for i in indices
        ]

        vertical_1 = math.dist(p2, p6)
        vertical_2 = math.dist(p3, p5)
        horizontal = math.dist(p1, p4)

        if horizontal < 1:
            return 0.0

        return (vertical_1 + vertical_2) / (2.0 * horizontal)

    def analizar(self, puntos):

        ear_izquierdo = self.calcular_ear(
            puntos, self.ojo_izquierdo
        )

        ear_derecho = self.calcular_ear(
            puntos, self.ojo_derecho
        )

        ear_promedio = (ear_izquierdo + ear_derecho) / 2.0

        ojos_cerrados = ear_promedio < self.umbral_ear

        if ojos_cerrados:
            if self.inicio_cierre is None:
                self.inicio_cierre = time.monotonic()

            duracion = time.monotonic() - self.inicio_cierre
        else:
            self.inicio_cierre = None
            duracion = 0.0

        fatiga = duracion >= self.tiempo_cierre

        return {
            "ear": ear_promedio,
            "ear_izquierdo": ear_izquierdo,
            "ear_derecho": ear_derecho,
            "ojos_cerrados": ojos_cerrados,
            "duracion_cierre": duracion,
            "fatiga": fatiga
        }
