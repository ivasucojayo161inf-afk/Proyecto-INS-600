
import cv2
import numpy as np
import time


class DetectorDistraccion:

    def __init__(self, umbral_yaw=20, umbral_pitch=20,
                 tiempo_distraccion=2.0):

        self.umbral_yaw = umbral_yaw
        self.umbral_pitch = umbral_pitch
        self.tiempo_distraccion = tiempo_distraccion
        self.yaw_referencia = 0.0
        self.pitch_referencia = 0.0
        self.inicio_distraccion = None

        # Modelo 3D aproximado del rostro
        self.modelo_3d = np.array([
            (0.0, 0.0, 0.0),          # Nariz
            (0.0, -63.6, -12.5),      # Mentón
            (-43.3, 32.7, -26.0),     # Ojo izquierdo
            (43.3, 32.7, -26.0),      # Ojo derecho
            (-28.9, -28.9, -24.1),   # Boca izquierda
            (28.9, -28.9, -24.1)     # Boca derecha
        ], dtype=np.float64)

        self.indices = [1, 152, 33, 263, 61, 291]

    def analizar(self, puntos, ancho, alto):

        puntos_2d = np.array(
            [puntos[i] for i in self.indices],
            dtype=np.float64
        )

        focal = ancho

        camara = np.array([
            [focal, 0, ancho / 2],
            [0, focal, alto / 2],
            [0, 0, 1]
        ], dtype=np.float64)

        distorsion = np.zeros((4, 1))

        correcto, rotacion, traslacion = cv2.solvePnP(
            self.modelo_3d,
            puntos_2d,
            camara,
            distorsion,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not correcto:
            return None

        matriz_rotacion, _ = cv2.Rodrigues(rotacion)

        angulos = cv2.RQDecomp3x3(matriz_rotacion)[0]

        pitch = angulos[0]
        yaw = angulos[1]

        yaw_relativo = yaw - self.yaw_referencia
        pitch_relativo = pitch - self.pitch_referencia

        desviacion = (
            abs(yaw_relativo) > self.umbral_yaw or
            abs(pitch_relativo) > self.umbral_pitch
        )

        if desviacion:

            if self.inicio_distraccion is None:
                self.inicio_distraccion = time.monotonic()

            duracion = time.monotonic() - self.inicio_distraccion

        else:
            self.inicio_distraccion = None
            duracion = 0

        distraido = duracion >= self.tiempo_distraccion

        return {
            "yaw": yaw,
            "pitch": pitch,
            "desviacion": desviacion,
            "duracion": duracion,
            "distraido": distraido
        }

    def reiniciar(self):
        self.inicio_distraccion = None
