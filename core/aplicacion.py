
import cv2
import threading
import time

from INTERFACES.servidor import iniciar_servidor
from VISION.camara import Camara
from VISION.detector_rostro import DetectorRostro
from CONFIGURACIÓN.configuracion import Configuracion
from core.base_datos import BaseDatos
from core.detector_distraccion import DetectorDistraccion
from core.detector_fatiga import DetectorFatiga
from core.calibrador import Calibrador


def dibujar_guia_calibracion(fotograma, puntos=None):

    alto, ancho = fotograma.shape[:2]

    centro_x = ancho // 2
    centro_y = int(alto * 0.47)

    eje_x = int(ancho * 0.23)
    eje_y = int(alto * 0.40)

    color = (0, 165, 255)
    dentro = False

    if puntos is not None and len(puntos) > 0:

        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        rostro_x = (x_min + x_max) / 2
        rostro_y = (y_min + y_max) / 2

        posicion = (
            ((rostro_x - centro_x) / eje_x) ** 2
            + ((rostro_y - centro_y) / eje_y) ** 2
        )

        dentro = posicion <= 0.55

        if dentro:
            color = (0, 255, 0)

    overlay = fotograma.copy()

    cv2.ellipse(
        overlay,
        (centro_x, centro_y),
        (eje_x, eje_y),
        0, 0, 360,
        (255, 255, 255),
        2
    )

    cv2.addWeighted(
        overlay, 0.25,
        fotograma, 0.75,
        0, fotograma
    )

    cv2.ellipse(
        fotograma,
        (centro_x, centro_y),
        (eje_x, eje_y),
        0, 0, 360,
        color,
        3
    )

    if puntos is None:
        mensaje = "COLOCA TU ROSTRO DENTRO DEL OVALO"
    elif dentro:
        mensaje = "ROSTRO CORRECTAMENTE COLOCADO"
    else:
        mensaje = "CENTRA TU ROSTRO DENTRO DEL OVALO"

    cv2.putText(
        fotograma,
        mensaje,
        (20, alto - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        color,
        2
    )

    return dentro


class Aplicacion:

    def __init__(self):

        self.config = Configuracion()

        self.camara = Camara(
            indice=self.config.CAMARA_INDICE,
            ancho=self.config.CAMARA_ANCHO,
            alto=self.config.CAMARA_ALTO
        )

        # Inicializar base de datos
        self.base_datos = BaseDatos()

        # Control de alertas anteriores para evitar duplicados
        self.alertas_anteriores = {
            "fatiga": False,
            "distraccion": False
        }

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

        self.modo_calibracion = False

        self.web_lock = threading.Lock()
        self.frame_jpeg = None
        self.solicitar_calibracion = False

        self.estado_web = {
            "estado": "Iniciando sistema",
            "ear": "--",
            "yaw": "--",
            "pitch": "--",
            "sistema": "Inicializando",

            "alerta_fatiga": False,
            "alerta_distraccion": False,

            "calibracion_activa": False,
            "calibracion_fase": "",
            "calibracion_instruccion": "",
            "calibracion_progreso": 0,
            "calibracion_muestras": 0
        }

        print("Aplicación inicializada correctamente.")

    def aplicar_calibracion(self, resultado):

        if resultado is None:
            print("No se pudo completar la calibracion")
            return False

        self.fatiga.umbral_ear = resultado["umbral_ear"]

        self.distraccion.yaw_referencia = resultado["yaw_referencia"]
        self.distraccion.pitch_referencia = resultado["pitch_referencia"]
        self.distraccion.umbral_yaw = resultado["umbral_yaw"]
        self.distraccion.umbral_pitch = resultado["umbral_pitch"]

        self.fatiga.inicio_cierre = None
        self.distraccion.reiniciar()

        print("\n========== CALIBRACION ==========")
        print(f"EAR referencia: {resultado['ear_referencia']:.3f}")
        print(f"Umbral EAR: {resultado['umbral_ear']:.3f}")
        print(f"Yaw referencia: {resultado['yaw_referencia']:.2f}")
        print(f"Pitch referencia: {resultado['pitch_referencia']:.2f}")
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

        dentro_ovalo = dibujar_guia_calibracion(
            fotograma, puntos
        )

        resultado_distraccion = self.distraccion.analizar(
            puntos, ancho, alto
        )

        resultado_fatiga = self.fatiga.analizar(puntos)

        if resultado_distraccion is not None and dentro_ovalo:

            self.calibrador.agregar_muestra(
                resultado_fatiga["ear"],
                resultado_distraccion["yaw"],
                resultado_distraccion["pitch"]
            )

        fase = self.calibrador.obtener_fase()
        progreso = self.calibrador.obtener_progreso()

        claves = ("normal", "cerrado", "movimiento")

        muestras = len(
            self.calibrador.muestras[claves[self.calibrador.paso]]
        )

        overlay = fotograma.copy()

        cv2.rectangle(
            overlay,
            (10, alto - 145),
            (ancho - 10, alto - 35),
            (15, 20, 28),
            -1
        )

        cv2.addWeighted(
            overlay, 0.85,
            fotograma, 0.15,
            0, fotograma
        )

        cv2.putText(
            fotograma,
            f"CALIBRACION {self.calibrador.paso + 1}/3",
            (25, alto - 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 200, 255),
            2
        )

        cv2.putText(
            fotograma,
            fase["nombre"],
            (25, alto - 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            fotograma,
            fase["instruccion"],
            (25, alto - 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (220, 220, 220),
            1
        )

        barra_x = 25
        barra_y = alto - 47
        barra_ancho = ancho - 50

        cv2.rectangle(
            fotograma,
            (barra_x, barra_y),
            (barra_x + barra_ancho, barra_y + 8),
            (60, 60, 60),
            -1
        )

        cv2.rectangle(
            fotograma,
            (barra_x, barra_y),
            (
                barra_x + int(barra_ancho * progreso / 100),
                barra_y + 8
            ),
            (0, 220, 120),
            -1
        )

        self.actualizar_estado({
            "estado": "CALIBRANDO",
            "ear": round(resultado_fatiga["ear"], 3),

            "yaw": round(resultado_distraccion["yaw"], 1)
                if resultado_distraccion else "--",

            "pitch": round(resultado_distraccion["pitch"], 1)
                if resultado_distraccion else "--",

            "sistema": "Calibración en proceso",
            "alerta_fatiga": False,
            "alerta_distraccion": False,

            "calibracion_activa": True,

            "calibracion_fase": (
                f"Fase {self.calibrador.paso + 1}/3: {fase['nombre']}"
            ),

            "calibracion_instruccion": fase["instruccion"],
            "calibracion_progreso": progreso,
            "calibracion_muestras": muestras
        })

        resultado = self.calibrador.avanzar()

        if resultado is not None and not resultado.get("siguiente"):

            if resultado.get("correcto") and self.aplicar_calibracion(
                resultado["resultado"]
            ):

                self.modo_calibracion = False
                mensaje = resultado["mensaje"]
                sistema = "Monitoreando"

            else:

                mensaje = resultado.get(
                    "mensaje",
                    "No se pudo completar la calibración."
                )

                self.modo_calibracion = False
                self.calibrador.inicio = None
                sistema = "Monitoreando con parámetros anteriores"

            self.actualizar_estado({
                "estado": mensaje,
                "sistema": sistema,
                "alerta_fatiga": False,
                "alerta_distraccion": False,
                "calibracion_activa": False,
                "calibracion_fase": "",
                "calibracion_instruccion": "",
                "calibracion_progreso": (
                    100 if resultado.get("correcto") else 0
                ),
                "calibracion_muestras": 0
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

        yaw = "--"
        pitch = "--"

        distraido = False

        if resultado_distraccion is not None:

            yaw = resultado_distraccion["yaw"]
            pitch = resultado_distraccion["pitch"]
            distraido = resultado_distraccion["distraido"]

            if distraido:

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

        # ==========================================
        # REGISTRO DE EVENTOS EN LA BASE DE DATOS
        # ==========================================

        if fatiga and not self.alertas_anteriores["fatiga"]:

            self.base_datos.registrar_evento(
                tipo_evento="FATIGA",
                ear=ear,
                yaw=yaw if isinstance(yaw, (int, float)) else None,
                pitch=pitch if isinstance(pitch, (int, float)) else None
            )

        if distraido and not self.alertas_anteriores["distraccion"]:

            self.base_datos.registrar_evento(
                tipo_evento="DISTRACCION",
                ear=ear,
                yaw=yaw if isinstance(yaw, (int, float)) else None,
                pitch=pitch if isinstance(pitch, (int, float)) else None
            )

        # Guardar el estado actual para evitar registros duplicados
        self.alertas_anteriores["fatiga"] = bool(fatiga)
        self.alertas_anteriores["distraccion"] = bool(distraido)

        # ==========================================

        if fatiga and distraido:

            estado = "ALERTA: FATIGA Y DISTRACCION"
            color = (0, 0, 255)

        elif fatiga:

            estado = "ALERTA: POSIBLE FATIGA"
            color = (0, 0, 255)

        elif distraido:

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

        # Publicar ambas alertas en la interfaz web
        self.actualizar_estado({
            "estado": estado,
            "ear": round(ear, 3),
            "yaw": round(yaw, 1) if resultado_distraccion is not None else "--",
            "pitch": round(pitch, 1) if resultado_distraccion is not None else "--",
            "sistema": "Monitoreando",

            "alerta_fatiga": bool(fatiga),
            "alerta_distraccion": bool(distraido)
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
        fps = 0

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

                    # Reiniciar estados de alertas
                    self.alertas_anteriores = {
                        "fatiga": False,
                        "distraccion": False
                    }

                    self.actualizar_estado({
                        "alerta_fatiga": False,
                        "alerta_distraccion": False
                    })

                if rostros:

                    puntos = rostros[0]

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

                    # Reiniciar estados cuando no hay rostro
                    self.alertas_anteriores = {
                        "fatiga": False,
                        "distraccion": False
                    }

                    self.actualizar_estado({
                        "alerta_fatiga": False,
                        "alerta_distraccion": False
                    })

                    if self.modo_calibracion:

                        dibujar_guia_calibracion(
                            fotograma, None
                        )

                        fase = (
                            self.calibrador.obtener_fase()
                            if self.calibrador.inicio is not None
                            else {
                                "nombre": "PREPARACIÓN",
                                "instruccion": "Coloca tu rostro frente a la cámara"
                            }
                        )

                        self.actualizar_estado({
                            "estado": "No se detecta el rostro",
                            "sistema": "Calibración en proceso",
                            "alerta_fatiga": False,
                            "alerta_distraccion": False,
                            "calibracion_activa": True,
                            "calibracion_fase": fase["nombre"],
                            "calibracion_instruccion": (
                                "Coloca tu rostro frente a la cámara"
                            ),
                            "calibracion_progreso": (
                                self.calibrador.obtener_progreso()
                            ),
                            "calibracion_muestras": 0
                        })

                    cv2.putText(
                        fotograma,
                        "SIN ROSTRO",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

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

                color_fps = (
                    (0, 255, 0) if fps >= 8 else (0, 0, 255)
                )

                cv2.putText(
                    fotograma,
                    f"FPS: {fps:.2f}",
                    (20, 155),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color_fps,
                    2
                )

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
