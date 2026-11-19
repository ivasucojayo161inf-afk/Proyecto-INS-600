import cv2
import mediapipe as mp

class DetectorRostro:

    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh

        self.detector = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detectar(self, fotograma):

        rgb = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)
        resultado = self.detector.process(rgb)

        rostros = []

        if resultado.multi_face_landmarks:

            for rostro in resultado.multi_face_landmarks:
                puntos = []

                for punto in rostro.landmark:
                    alto, ancho, _ = fotograma.shape

                    x = punto.x * ancho
                    y = punto.y * alto

                    puntos.append((x, y))

                rostros.append(puntos)

        return rostros

    def cerrar(self):
        self.detector.close()
