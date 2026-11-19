# Plan de pruebas de software

## 1. Objetivo y alcance

Validar el prototipo de monitoreo de fatiga y distracción del conductor según los requisitos RF-01 a RF-09 y los objetivos de ejecución de la ERS. Se consideran pruebas de caja negra (comportamiento observable) y de caja blanca (decisiones y rutas internas).

**Entorno previsto:** Python 3.9 o superior; cámara compatible o fuente de video de prueba; OpenCV, MediaPipe y NumPy; Raspberry Pi y actuadores reales o simulados. Las pruebas se ejecutarán en entorno controlado, no durante conducción real.

**Estados:** No ejecutado, Aprobado, Reprobado, Bloqueado. Los resultados reales quedan pendientes hasta ejecutar las pruebas en el prototipo.

## 2. Historias de usuario trazables

La ERS compartida no incluye historias de usuario textuales. Para cubrir la actividad, se proponen estas historias derivadas de los RF; deben ajustarse si el equipo ya tiene historias aprobadas.

- **HU-01 (RF-03, RF-08):** Como conductor, quiero recibir una alerta cuando el sistema detecte signos sostenidos de fatiga, para poder tomar una medida segura.
- **HU-02 (RF-04, RF-08):** Como conductor, quiero recibir una alerta si aparto la mirada de la carretera por más de dos segundos, para advertir una posible distracción.
- **HU-03 (RF-05, RF-06, RF-09):** Como administrador/técnico, quiero verificar el estado del sistema y controlar el monitoreo, para confirmar que el prototipo está operativo.

## 3. Caja negra: pruebas funcionales

### Plantilla básica de caso de prueba funcional

**TC-FUN-01 — Captura de video (RF-01)**

- **Descripción:** Verificar que el sistema recibe fotogramas de una cámara disponible.
- **Requisitos previos:** Cámara conectada; aplicación iniciada; fuente de video de prueba disponible.
- **Pasos:** Iniciar captura → mantener la fuente activa durante 30 segundos → revisar estado de cámara y flujo recibido.
- **Resultados esperados:** La cámara figura activa y se reciben fotogramas para procesamiento durante la prueba. Si se desconecta, el estado cambia a inactivo y se informa el error.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-02 — Detección facial (RF-02)**

- **Descripción:** Comprobar la detección de rostro y extracción de puntos faciales.
- **Requisitos previos:** Modelo MediaPipe cargado; conjunto de imágenes de prueba con rostro visible y sin rostro.
- **Pasos:** Procesar una imagen con rostro → verificar detección y puntos de ojos → procesar una imagen sin rostro.
- **Resultados esperados:** Con rostro detectable se informa detección exitosa y coordenadas; sin rostro, la detección es falsa y no se reutilizan puntos anteriores.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-03 — Métricas de fatiga (RF-03)**

- **Descripción:** Verificar EAR, PERCLOS en ventana de dos segundos e indicador de fatiga.
- **Requisitos previos:** Umbral de ojo cerrado y umbral de fatiga configurados; datos sintéticos de puntos o video etiquetado.
- **Pasos:** Procesar ojos abiertos → procesar una ventana de dos segundos con ojos cerrados durante una fracción conocida → comparar resultados con los umbrales configurados.
- **Resultados esperados:** EAR y PERCLOS están en sus rangos definidos (PERCLOS de 0 % a 100 %); el indicador coincide con los umbrales configurados. Los valores exactos de umbral deben documentarse en la configuración del prototipo, pues la ERS no los especifica.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-04 — Detección de distracción (RF-04)**

- **Descripción:** Verificar el tiempo acumulado de mirada desviada y la activación del indicador.
- **Requisitos previos:** Umbral angular configurado; secuencia de prueba con mirada frontal y mirada desviada.
- **Pasos:** Mantener mirada frontal → desviar la mirada por exactamente dos segundos → repetir durante más de dos segundos.
- **Resultados esperados:** No se marca distracción mientras la duración no supere dos segundos; al superar dos segundos consecutivos, se marca distracción y se informa el tiempo acumulado.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-05 — Auto-test de encendido (RF-05)**

- **Descripción:** Verificar la secuencia de autocomprobación y sus indicadores.
- **Requisitos previos:** Cámara, software y actuadores disponibles; posibilidad de simular un componente defectuoso.
- **Pasos:** Encender con todos los componentes operativos → repetir simulando cámara o software no disponible.
- **Resultados esperados:** Con todos los componentes operativos, el auto-test indica sistema listo con LED verde fijo. Ante error de cámara o software, el LED rojo parpadea. La prueba de auto-test tarda menos de 10 segundos.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-06 — Inicio y detención (RF-06)**

- **Descripción:** Verificar que los controles de interfaz inician y detienen el monitoreo de forma controlada.
- **Requisitos previos:** Aplicación abierta; cámara disponible; dashboard accesible.
- **Pasos:** Seleccionar Iniciar → comprobar captura/análisis y estado mostrado → seleccionar Detener → comprobar que el procesamiento finaliza.
- **Resultados esperados:** El estado del dashboard refleja cada cambio; al detener, no se procesan nuevos fotogramas y la aplicación permanece estable.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-07 — Validación de configuración (RF-07)**

- **Descripción:** Verificar aceptación de parámetros válidos y rechazo de valores fuera de rango.
- **Requisitos previos:** Usuario con acceso a la configuración; rangos permitidos definidos por el prototipo.
- **Pasos:** Guardar valores válidos → comprobar confirmación y aplicación → introducir un valor fuera del rango o formato no numérico → guardar.
- **Resultados esperados:** Los valores válidos se aceptan y aplican; los inválidos muestran un mensaje de validación y no alteran la última configuración válida.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-08 — Indicadores de estado (RF-08)**

- **Descripción:** Verificar correspondencia entre estado/evento y LEDs.
- **Requisitos previos:** LEDs o simulador de GPIO disponibles.
- **Pasos:** Activar estados de prueba, monitoreo normal, alerta y error de cámara/software.
- **Resultados esperados:** Prueba: verde parpadeante; sistema OK/monitoreo: verde fijo; alerta: rojo fijo; error: rojo parpadeante.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**TC-FUN-09 — Visualización de estado (RF-09)**

- **Descripción:** Comprobar que la interfaz muestra disponibilidad y errores de los componentes.
- **Requisitos previos:** Dashboard accesible; posibilidad de cambiar estado de cámara y módulo de visión.
- **Pasos:** Abrir Estado del sistema → verificar componentes operativos → desconectar la cámara o simular error del módulo → actualizar la vista.
- **Resultados esperados:** La interfaz muestra el estado actualizado de cámara y módulo, el resultado del auto-test y el mensaje de error correspondiente.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

## 4. Caja negra: inicio de sesión

La ERS no define una pantalla de login ni un mecanismo de cuentas. Sí exige que la red WiFi local/interfaz de configuración esté protegida con contraseña. Estos casos validan ese acceso; completar el mecanismo concreto y las credenciales de prueba según la implementación.

**LOGIN-01 — Acceso autorizado**

- **Descripción:** Acceder a la interfaz de configuración con credenciales válidas.
- **Credenciales de prueba:** Usuario y contraseña de prueba definidos localmente; no incluir credenciales reales en el informe.
- **Pasos:** Conectarse a la WiFi local → abrir la interfaz → ingresar credenciales válidas.
- **Resultados esperados:** Se permite el acceso a la configuración y se muestra el dashboard/estado.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**LOGIN-02 — Contraseña incorrecta**

- **Descripción:** Rechazar credenciales inválidas.
- **Credenciales de prueba:** Usuario de prueba con contraseña incorrecta.
- **Pasos:** Abrir la interfaz → ingresar la contraseña incorrecta → enviar.
- **Resultados esperados:** Se deniega el acceso, se muestra un mensaje genérico y no se revelan datos de configuración.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**LOGIN-03 — Acceso sin autenticación**

- **Descripción:** Comprobar que la configuración no queda expuesta sin autenticación.
- **Credenciales de prueba:** Ninguna.
- **Pasos:** Abrir directamente la URL/ruta de configuración sin iniciar sesión.
- **Resultados esperados:** Se solicita autenticación o se deniega el acceso; no se muestran ni modifican parámetros.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

## 5. Caja negra: aceptación del usuario

**UAT-01 — Alerta de fatiga (HU-01)**

- **Historia de usuario:** Como conductor, quiero recibir una alerta ante signos sostenidos de fatiga.
- **Criterios de aceptación:** La ventana de PERCLOS es de dos segundos; al cumplirse el umbral configurado, se genera la alerta y se refleja en los indicadores.
- **Pasos:** Iniciar monitoreo → reproducir secuencia etiquetada de ojos abiertos → reproducir secuencia que supera el umbral de fatiga.
- **Resultados esperados:** No hay alerta en la secuencia normal; se genera alerta al superar el umbral configurado.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**UAT-02 — Alerta de distracción (HU-02)**

- **Historia de usuario:** Como conductor, quiero recibir una alerta si aparto la mirada por más de dos segundos.
- **Criterios de aceptación:** La desviación se considera distracción solo cuando supera dos segundos consecutivos y la alerta se distingue de mensajes informativos.
- **Pasos:** Iniciar monitoreo → mirar al frente → desviar la mirada durante más de dos segundos en una secuencia controlada.
- **Resultados esperados:** El sistema genera alerta visual/sonora según la configuración y muestra la condición detectada.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**UAT-03 — Estado y control para técnico (HU-03)**

- **Historia de usuario:** Como administrador/técnico, quiero verificar el estado y controlar el monitoreo.
- **Criterios de aceptación:** La interfaz informa cámara/módulo/errores y permite iniciar y detener el monitoreo actualizando el dashboard.
- **Pasos:** Abrir la interfaz → revisar estado → iniciar monitoreo → detener monitoreo.
- **Resultados esperados:** El técnico identifica el estado de cada componente y observa confirmación de inicio y detención.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

## 6. Caja negra: integración

**INT-01 — Cámara a alerta**

- **Sistemas involucrados:** Cámara/OpenCV, MediaPipe, cálculo EAR/PERCLOS, lógica de alerta, GPIO/actuadores.
- **Punto de integración:** El análisis de fotogramas produce un evento que activa la alerta configurada.
- **Pasos:** Ingresar video de prueba → verificar detección facial y métricas → presentar una secuencia que supere el umbral → observar LED/buzzer simulado.
- **Resultados esperados:** El evento y el actuador corresponden a la condición detectada; sin condición no se activa la alarma.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**INT-02 — Auto-test a indicadores/interfaz**

- **Sistemas involucrados:** Auto-test, cámara, software de visión, actuadores, GPIO y dashboard.
- **Punto de integración:** Resultado del auto-test reflejado en LEDs y estado web.
- **Pasos:** Ejecutar auto-test con componentes disponibles → repetir con cámara no disponible.
- **Resultados esperados:** Los indicadores físicos y la interfaz muestran el mismo resultado; el fallo se identifica sin indicar falsamente que el sistema está listo.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

**INT-03 — Configuración a proceso de monitoreo**

- **Sistemas involucrados:** Interfaz web, validación/almacenamiento de configuración y módulos de detección/alerta.
- **Punto de integración:** Parámetros aceptados por la interfaz son utilizados por el procesamiento.
- **Pasos:** Cambiar un parámetro válido → guardar → iniciar/reiniciar monitoreo → comprobar el valor usado por el módulo.
- **Resultados esperados:** El valor guardado se aplica; un valor inválido no modifica la configuración activa.
- **Resultados reales:** Pendiente de ejecución.
- **Estado:** No ejecutado.

## 7. Caja negra: rendimiento

Las mediciones deben realizarse en el hardware objetivo (Raspberry Pi especificada), registrando versión de software, resolución, iluminación, duración y carga. No se debe presentar una medición de PC como resultado de Raspberry Pi.

**PERF-01 — Frecuencia de procesamiento**

- **Guion:** Procesamiento continuo de video con rostro visible.
- **Condiciones de carga:** Raspberry Pi objetivo; cámara y resolución documentadas; ejecución durante al menos 60 segundos.
- **Pasos:** Iniciar monitoreo → medir fotogramas procesados y tiempo → calcular FPS promedio y mínimo por intervalos.
- **Tiempo de respuesta previsto:** 8 FPS o más.
- **Tiempo de respuesta real:** Pendiente de medición; registrar FPS observado.
- **Estado:** No ejecutado.

**PERF-02 — Arranque y auto-test**

- **Guion:** Encendido desde sistema en reposo hasta disponibilidad de monitoreo.
- **Condiciones de carga:** Hardware objetivo; cámara y actuadores conectados.
- **Pasos:** Medir desde señal de encendido hasta fin del auto-test y hasta monitoreo listo; repetir cinco veces.
- **Tiempo de respuesta previsto:** Auto-test menor de 10 s; arranque hasta monitoreo menor de 30 s.
- **Tiempo de respuesta real:** Pendiente de medición; registrar cada repetición.
- **Estado:** No ejecutado.

**PERF-03 — Apagado seguro**

- **Guion:** Detención del sistema desde monitoreo normal.
- **Condiciones de carga:** Monitoreo activo y registro de eventos habilitado si aplica.
- **Pasos:** Solicitar apagado → medir hasta que captura, procesamiento y actuadores queden en estado seguro.
- **Tiempo de respuesta previsto:** Menos de 10 s.
- **Tiempo de respuesta real:** Pendiente de medición.
- **Estado:** No ejecutado.

## 8. Caja blanca: pruebas unitarias y de flujo

Ejecutar sobre funciones aisladas con datos sintéticos y dependencias simuladas. La cámara, GPIO, relés y buzzer no deben activarse físicamente en estas pruebas. Registrar cobertura de sentencias y ramas; criterio sugerido para la lógica crítica: cubrir todas las ramas de fatiga, distracción, error y validación.

| ID | Unidad/ruta | Datos o condición | Resultado esperado |
|---|---|---|---|
| WB-01 | Cálculo EAR | Distancia horizontal entre puntos externos = 10; dos distancias verticales = 4 cada una | EAR = (4 + 4) / (2 × 10) = 0.4, usando la fórmula estándar y el orden de puntos definido por la implementación |
| WB-02 | Cálculo EAR | Distancia horizontal igual a cero o puntos no válidos | Manejo controlado del dato inválido; no hay división por cero ni cierre del proceso |
| WB-03 | Cálculo PERCLOS | Ventana de dos segundos con la mitad de las muestras clasificadas como cerradas | PERCLOS = 50 %; resultado dentro del rango 0–100 % |
| WB-04 | Umbral de ojo cerrado/fatiga | Valor por debajo, igual y por encima del umbral configurado | Cada rama aplica la regla documentada; confirmar explícitamente si la comparación implementada es `<` o `<=` |
| WB-05 | Duración de distracción | Desviación de 2.0 s y de más de 2.0 s | A 2.0 s no se activa por la regla “más de 2 s”; sobre 2.0 s se activa |
| WB-06 | Máquina de estados | Secuencia reposo → auto-test → monitoreo → alerta → monitoreo; auto-test fallido | Transiciones válidas en orden; ante fallo no se entra al estado operativo y se selecciona estado de error |
| WB-07 | Validación de parámetros | Valor mínimo, máximo, fuera de rango y texto no numérico | Límites válidos según configuración; inválidos rechazados sin reemplazar el último valor válido |
| WB-08 | Errores de dependencias | Cámara sin abrir, fallo del modelo y excepción del actuador | Error capturado, estado actualizado y aplicación sin terminar abruptamente; actuadores quedan en estado seguro |

## 9. Registro de ejecución

Completar para cada caso después de ejecutarlo: fecha, responsable, versión/commit, equipo, datos usados, resultado real, estado y enlace al defecto si falla. No marcar un caso como aprobado hasta comparar evidencia observada con el resultado esperado.

### Observaciones pendientes de la ERS

- Definir numéricamente el umbral EAR/PERCLOS que activa fatiga y los umbrales angulares de mirada/cabeza.
- Precisar rangos permitidos para cada parámetro configurable y el mecanismo de autenticación de la interfaz.
- La ERS menciona registro/historial de eventos en la interfaz, pero no detalla los requisitos funcionales de almacenamiento; agregar RF y casos para historial si esa función se implementará.
- Validar las tres historias de usuario propuestas con el equipo y vincularlas al diagrama de casos de uso.
- Las pruebas de detección con personas requieren consentimiento informado. No usar el prototipo como único mecanismo de seguridad ni probarlo conduciendo.