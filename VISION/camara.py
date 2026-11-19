import cv2
class Camara:
    def __init__(self, indice=0, ancho=640, alto=480):
        self.indice = indice
        self.ancho = ancho
        self.alto = alto
        self.captura = None
    def iniciar(self):
        self.captura = cv2.VideoCapture(self.indice)
        if not self.captura.isOpened():
            print("Error: no se pudo abrir la cámara")
            return False
        self.captura.set(cv2.CAP_PROP_FRAME_WIDTH, self.ancho)
        self.captura.set(cv2.CAP_PROP_FRAME_HEIGHT, self.alto)
        print("Cámara iniciada correctamente")
        return True
    def leer(self):
        if self.captura is None:
            return False, None
        return self.captura.read()
    def cerrar(self):
        if self.captura is not None:
            self.captura.release()
            self.captura = None
        cv2.destroyAllWindows()
        print("Cámara cerrada")
