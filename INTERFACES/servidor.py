
from flask import Flask, render_template, Response, jsonify, request
import threading
import time
import cv2


app_web = Flask(__name__)


def iniciar_servidor(aplicacion):

    @app_web.route("/")
    def inicio():
        return render_template("index.html")

    @app_web.route("/video_feed")
    def video_feed():

        def generar():

            while True:

                with aplicacion.web_lock:
                    imagen = aplicacion.frame_jpeg

                if imagen is not None:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + imagen
                        + b"\r\n"
                    )

                time.sleep(0.04)

        return Response(
            generar(),
            mimetype="multipart/x-mixed-replace; boundary=frame"
        )

    @app_web.route("/api/estado")
    def obtener_estado():

        with aplicacion.web_lock:
            datos = aplicacion.estado_web.copy()

        return jsonify(datos)

    @app_web.route("/api/configuracion", methods=["POST"])
    def cambiar_configuracion():

        datos = request.get_json(silent=True) or {}

        try:
            umbral_ear = float(datos.get("umbral_ear", aplicacion.fatiga.umbral_ear))
            umbral_yaw = float(datos.get("umbral_yaw", aplicacion.distraccion.umbral_yaw))
            umbral_pitch = float(datos.get("umbral_pitch", aplicacion.distraccion.umbral_pitch))
            tiempo_cierre = float(datos.get("tiempo_cierre", aplicacion.fatiga.tiempo_cierre))
            tiempo_distraccion = float(datos.get("tiempo_distraccion", aplicacion.distraccion.tiempo_distraccion))

            if not 0.05 <= umbral_ear <= 0.50:
                raise ValueError("Umbral EAR fuera de rango")

            if not 5 <= umbral_yaw <= 90:
                raise ValueError("Umbral Yaw fuera de rango")

            if not 5 <= umbral_pitch <= 90:
                raise ValueError("Umbral Pitch fuera de rango")

            if not 0.5 <= tiempo_cierre <= 10:
                raise ValueError("Tiempo de cierre fuera de rango")

            if not 0.5 <= tiempo_distraccion <= 10:
                raise ValueError("Tiempo de distracción fuera de rango")

            aplicacion.fatiga.umbral_ear = umbral_ear
            aplicacion.fatiga.tiempo_cierre = tiempo_cierre

            aplicacion.distraccion.umbral_yaw = umbral_yaw
            aplicacion.distraccion.umbral_pitch = umbral_pitch
            aplicacion.distraccion.tiempo_distraccion = tiempo_distraccion

            return jsonify({
                "correcto": True,
                "mensaje": "Configuracion actualizada"
            })

        except (ValueError, TypeError) as error:

            return jsonify({
                "correcto": False,
                "mensaje": str(error)
            }), 400

    @app_web.route("/api/calibrar", methods=["POST"])
    def solicitar_calibracion():

        aplicacion.solicitar_calibracion = True
        aplicacion.actualizar_estado({
            "estado": "Preparando calibración guiada...",
            "sistema": "Calibración solicitada",
            "calibracion_activa": True,
            "calibracion_fase": "Preparación",
            "calibracion_instruccion": "Coloca tu rostro frente a la cámara",
            "calibracion_progreso": 0,
            "calibracion_muestras": 0
        })

        return jsonify({
            "correcto": True,
            "mensaje": "Calibración guiada iniciada. Sigue las instrucciones."
        })

    hilo = threading.Thread(
        target=lambda: 
        app_web.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        ),
        daemon=True
    )

    hilo.start()

    print("Dashboard disponible en http://127.0.0.1:5000")
