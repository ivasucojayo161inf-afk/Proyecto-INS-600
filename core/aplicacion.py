import cv2
import threading
import time
from INTERFACES.servidor import iniciar_servidor
from VISION.camara import Camara
from VISION.detector_rostro import DetectorRostro
from CONFIGURACIÓN.configuracion import Configuracion
from core.detector_distraccion import DetectorDistraccion
from core.detector_fatiga import DetectorFatiga
from core.calibrador import Calibrador

inicio_intervalo = time.perf_counter()
fotogramas_intervalo = 0
fps = 0

class Aplicacion:
    
    def __init__(self):

        self.config = Configuracion()
        self.camara = Camara(
            indice=self.config.CAMARA_INDICE,
            ancho=self.config.CAMARA_ANCHO,
            alto=self.config.CAMARA_ALTO
        )

        self.detector = DetectorRostro()

        self.fatiga = DetectorFatiga(
            umbral_ear=self.config.UMBRAL_EAR,
            tiempo_cierre=self.config.TIEMPO_CIERRE
        )

        self.distraccion = DetectorDistraccion(
            umbral_yaw=self.config.UMBRAL_YAW,
            umbral_pitch=self.config.UMBRAL_PITCH,
            tiempo_distraccion=self.config.TIEMPO_DISTRACCION
        )

        self.calibrador = Calibrador(
            duracion=self.config.DURACION_CALIBRACION,
            muestras_minimas=self.config.MUESTRAS_MINIMAS
        )
        self.modo_calibracion = True
        self.web_lock = threading.Lock()
        self.frame_jpeg = None
        self.solicitar_calibracion = False
        self.estado_web = {
            "estado": "Iniciando sistema",
            "ear": "--",
            "yaw": "--",
            "pitch": "--",
            "sistema": "Inicializando"
        }
        


    def aplicar_calibracion(self, resultado):

        if resultado is None:
            print("No se pudo completar la calibracion")
            return False

        self.fatiga.umbral_ear = resultado["umbral_ear"]

        self.distraccion.yaw_referencia = resultado["yaw_referencia"]
        self.distraccion.pitch_referencia = resultado["pitch_referencia"]

        # Reiniciar temporizadores
        self.fatiga.inicio_cierre = None
        self.distraccion.reiniciar()

        print("\n========== CALIBRACION ==========")

        print(
            f"EAR referencia: {resultado['ear_referencia']:.3f}"
        )

        print(
            f"Umbral EAR: {resultado['umbral_ear']:.3f}"
        )

        print(
            f"Yaw referencia: {resultado['yaw_referencia']:.2f}"
        )

        print(
            f"Pitch referencia: {resultado['pitch_referencia']:.2f}"
        )

        print("Calibracion completada")
        print("================================\n")

        return True

    def actualizar_estado(self, datos):

        with self.web_lock:
            self.estado_web.update(datos)

    def publicar_fotograma(self, fotograma):

        correcto, buffer = cv2.imencode(
            ".jpg",
            fotograma,
            [cv2.IMWRITE_JPEG_QUALITY, 75]
        )

        if correcto:

            with self.web_lock:
                self.frame_jpeg = buffer.tobytes()

    def procesar_calibracion(self, fotograma, puntos, ancho, alto):

        if self.calibrador.inicio is None:
            self.calibrador.iniciar()
            self.distraccion.reiniciar()

        resultado_distraccion = self.distraccion.analizar(
            puntos, ancho, alto
        )

        if resultado_distraccion is not None:

            resultado_fatiga = self.fatiga.analizar(puntos)

            if not resultado_fatiga["ojos_cerrados"]:

                self.calibrador.agregar_muestra(
                    resultado_fatiga["ear"],
                    resultado_distraccion["yaw"],
                    resultado_distraccion["pitch"]
                )

        progreso = self.calibrador.obtener_progreso()

        cv2.putText(
            fotograma,
            f"CALIBRANDO: {progreso:.0f}%",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.putText(
            fotograma,
            f"MUESTRAS: {len(self.calibrador.muestras_ear)}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        if self.calibrador.tiempo_completado():

            resultado = self.calibrador.finalizar()

            if resultado is not None:

                if self.aplicar_calibracion(resultado):
                    self.modo_calibracion = False

            else:

                print(
                    "Muestras insuficientes. "
                    "Reiniciando calibracion..."
                )

                self.calibrador.iniciar()
                self.actualizar_estado({
                    "estado": "CALIBRANDO",
                    "ear": "--",
                    "yaw": "--",
                    "pitch": "--",
                    "sistema": f"{progreso:.0f}%"
                })

        return fotograma

    def procesar_monitoreo(self, fotograma, puntos, ancho, alto):

        resultado_fatiga = self.fatiga.analizar(puntos)

        resultado_distraccion = self.distraccion.analizar(
            puntos, ancho, alto
        )

        ear = resultado_fatiga["ear"]
        cerrados = resultado_fatiga["ojos_cerrados"]
        fatiga = resultado_fatiga["fatiga"]

        if resultado_distraccion is not None:

            yaw = resultado_distraccion["yaw"]
            pitch = resultado_distraccion["pitch"]

            if resultado_distraccion["distraido"]:
                estado_distraccion = "ALERTA: DISTRACCION"
                color_distraccion = (0, 0, 255)

            elif resultado_distraccion["desviacion"]:
                estado_distraccion = "ATENCION DESVIADA"
                color_distraccion = (0, 165, 255)

            else:
                estado_distraccion = "ATENCION AL FRENTE"
                color_distraccion = (0, 255, 0)

            cv2.putText(
                fotograma,
                estado_distraccion,
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color_distraccion,
                2
            )

            cv2.putText(
                fotograma,
                f"Yaw: {yaw:.1f} | Pitch: {pitch:.1f}",
                (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )

        if (
            fatiga
            and resultado_distraccion is not None
            and resultado_distraccion["distraido"]
        ):

            estado = "ALERTA: FATIGA Y DISTRACCION"
            color = (0, 0, 255)

        elif fatiga:

            estado = "ALERTA: POSIBLE FATIGA"
            color = (0, 0, 255)

        elif (
            resultado_distraccion is not None
            and resultado_distraccion["distraido"]
        ):

            estado = "ALERTA: DISTRACCION"
            color = (0, 0, 255)

        elif cerrados:

            estado = "OJOS CERRADOS"
            color = (0, 165, 255)

        else:

            estado = "CONDUCTOR ATENTO"
            color = (0, 255, 0)

        cv2.putText(
            fotograma,
            estado,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2
        )

        cv2.putText(
            fotograma,
            f"EAR: {ear:.3f}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )
        self.actualizar_estado({
            "estado": estado,
            "ear": round(ear, 3),
            "yaw": round(yaw, 1) if resultado_distraccion is not None else "--",
            "pitch": round(pitch, 1) if resultado_distraccion is not None else "--",
            "sistema": "Monitoreando"
        })

        return fotograma

    def ejecutar(self):

        iniciar_servidor(self)
        if not self.camara.iniciar():
            self.detector.cerrar()
            return

        inicio_prueba = time.perf_counter()
        inicio_intervalo = inicio_prueba
        total_fotogramas = 0
        fotogramas_intervalo = 0
        fps= 0
        

        try:
            while True:
                correcto, fotograma = self.camara.leer()
                if not correcto:
                    break
                alto, ancho, _ = fotograma.shape
                rostros = self.detector.detectar(fotograma)
                if self.solicitar_calibracion:
                    self.solicitar_calibracion = False
                    self.modo_calibracion = True
                    self.calibrador.iniciar()
                    self.fatiga.inicio_cierre = None
                    self.distraccion.reiniciar()
                if rostros:

                    puntos = rostros[0]

                    # Dibujar puntos faciales
                    for x, y in puntos:

                        cv2.circle(
                            fotograma,
                            (int(x), int(y)),
                            1,
                            (0, 255, 0),
                            -1
                        )

                    if self.modo_calibracion:

                        fotograma = self.procesar_calibracion(
                            fotograma,
                            puntos,
                            ancho,
                            alto
                        )

                    else:

                        fotograma = self.procesar_monitoreo(
                            fotograma,
                            puntos,
                            ancho,
                            alto
                        )

                else:

                    self.fatiga.inicio_cierre = None
                    self.distraccion.reiniciar()

                    if self.modo_calibracion:
                        self.calibrador.iniciar()

                    cv2.putText(
                        fotograma,
                        "SIN ROSTRO",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )
                fotogramas_intervalo += 1
                # Calcular FPS
                total_fotogramas += 1
                fotogramas_intervalo += 1

                tiempo_actual = time.perf_counter()
                tiempo_transcurrido = tiempo_actual - inicio_intervalo

                if tiempo_transcurrido >= 1:

                    fps = fotogramas_intervalo / tiempo_transcurrido

                    print(f"FPS actuales: {fps:.2f}")

                    fotogramas_intervalo = 0
                    inicio_intervalo = tiempo_actual

                # Color según el rendimiento
                if fps >= 8:
                    color_fps = (0, 255, 0)
                else:
                    color_fps = (0, 0, 255)

                # Mostrar FPS en pantalla
                cv2.putText(
                    fotograma,
                    f"FPS: {fps:.2f}",
                    (20, 155),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color_fps,
                    2
                )

                # Publicar imagen con FPS incluidos
                self.publicar_fotograma(fotograma)

                cv2.imshow("Proyecto", fotograma)

                if cv2.waitKey(1) == 27:
                    break

        finally:
            duracion = time.perf_counter() - inicio_prueba

            if duracion > 0:

                fps_promedio = total_fotogramas / duracion

                print("\n========== RESULTADO DE RENDIMIENTO ==========")
                print(f"Duración: {duracion:.2f} segundos")
                print(f"Fotogramas procesados: {total_fotogramas}")
                print(f"FPS promedio: {fps_promedio:.2f}")
                print("==============================================\n")

            self.camara.cerrar()
            self.detector.cerrar()
