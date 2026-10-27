# Calificador de Exámenes — Documento de proyecto

27 de octubre de 2026 · Johannes

## Resumen

Calificador de Exámenes es una aplicación web que permite a un profesor subir lotes de exámenes (principalmente manuscritos y de STEM), calificarlos con IA bajo los criterios que él mismo define y revisar los resultados con una aprobación humana obligatoria antes de que la nota sea final. Es una pieza del proyecto Teacher Assistant (TA) y arranca desde cero.

Se construyen **dos aplicaciones**: un **front** (React) y una **API** (Python, con LangGraph para el pipeline de IA). Toda la infraestructura corre en **AWS** y los datos viven en **bases de datos estructuradas (relacionales)**. El procesamiento es **asíncrono**: un solo modo, con cola de trabajos y progreso visible.

El proyecto se valida con un profesor piloto y 40 estudiantes reales. El objetivo es construir primero algo de alta calidad con un modelo de referencia (baseline) y después iterar en modelos y costos.

## El problema y la necesidad

Calificar a mano consume entre 65 y 187 horas al mes a un profesor típico, y la calidad baja con el cansancio. El cálculo sale de 560 exámenes al mes (7 grupos × 40 estudiantes × 2 evaluaciones) a 7–20 minutos cada uno.

| Dato | Valor | Fuente |
| --- | --- | --- |
| Grupos por profesor en LATAM | 3 a 7 | Experiencia del fundador (fue profesor) |
| Estudiantes por grupo | 40 o más | Experiencia del fundador |
| Exámenes por mes (mínimo) | 560 | 7 grupos × 40 × 2 evaluaciones |
| Evaluaciones semanales (algunas instituciones) | unas 280 talleres por semana | Experiencia del fundador |
| Tiempo por examen | 7 a 20 minutos | Experiencia del fundador |
| Lote completo de un profesor | unas 6 horas, con calidad decreciente | Experiencia del fundador |
| Caso reciente (Álgebra Lineal) | 100 estudiantes, 5 problemas, 4 calificadores, unas 3 horas | Experiencia del fundador |
| Formato de las respuestas | Principalmente papel; también Word o PDF. Cerca del 60% de los profesores usa solo papel | Conversaciones con profesores |
| Cómo se califica | 60% con clave de respuestas, 25% "a ojo", 15% con rúbrica | Conversaciones con profesores |

Las cifras vienen de la experiencia directa del fundador y de conversaciones previas con profesores; todavía no hay una medición formal, y el piloto sirve para contrastarlas.

**Cómo se hace hoy (caso Algebra Lineal):** el equipo reparte los problemas entre calificadores. Cada uno revisa el resultado y el desarrollo de su problema para todos los estudiantes, deja comentarios y asigna el puntaje con un criterio interno. El paquete pasa al siguiente calificador. Al final se pondera cada ejercicio, se registra la nota y se reordenan los exámenes. Si un estudiante no está conforme, hay que auditar por qué recibió esa nota.

**Consecuencias:** retroalimentación tardía, inconsistencia entre calificadores y entre horas del día, y sobre todo trabajo extra no remunerado para el docente.

**Enunciado del problema:** los profesores que califican exámenes a mano pierden horas de trabajo extra, repetitivo y desgastante, y la calidad de la calificación se compromete por el cansancio.

**Necesidad:** una herramienta simple, pensada para profesores de baja familiaridad tecnológica, que califique grandes volúmenes con los criterios del profesor, que sea fácil de auditar y que deje siempre la decisión final en sus manos.

## Objetivo del proyecto

**Objetivo general.** Reducir de forma radical el tiempo que un profesor dedica a calificar, manteniendo (o mejorando) la consistencia de la nota y la capacidad de auditarla, con la IA proponiendo y el profesor decidiendo.

**Objetivos específicos**

1. Permitir crear, por curso, un evaluador con enunciado y criterios (clave, rúbrica o 3 ejemplos calificados), validado por el profesor.
2. Calificar lotes de exámenes en PDF o foto, con nota, justificación y nivel de confianza por criterio.
3. Dar al profesor una revisión eficiente: documento original anotado, edición de notas y aceptación masiva revisando primero los casos más discrepantes.
4. Guardar de forma estructurada cursos, evaluadores, lotes, exámenes, notas y cambios, por usuario.
5. Establecer una línea base de calidad y costo que permita comparar otros modelos más adelante.

**Métricas de éxito**

| Métrica | Meta | Estado |
| --- | --- | --- |
| Concordancia entre la nota de la IA y la del profesor | Objetivo 95%, mínimo 90% | Definida por el fundador |
| Autonomía del piloto | El profesor piloto procesa un lote de 40 estudiantes y recibe resultados sin ayuda del equipo | Definida por el fundador |
| Tiempo de procesamiento | 100 exámenes en menos de 24 horas (techo). Para un lote de 40, resultados en 15 minutos o menos | Techo definido; el de 40 es propuesto |
| Inconformidad de estudiantes | Menos del 10% | Definida por el fundador |
| Notas finales sin aprobación del profesor | 0 | Regla de producto |
| Costo de IA por examen | Propuesto: 45 COP o menos (la mitad del ingreso por examen) | Propuesto, por validar en el piloto |

El precio objetivo es 50.000 COP mensuales por profesor. Con 560 exámenes al mes eso equivale a unos 89 COP de ingreso por examen, y de ahí sale el techo de costo propuesto. El precio es un supuesto sin validar.

**Fuera del alcance de esta fase:** chatbot de acompañamiento para crear exámenes, portal de estudiantes, integración con LMS, envío de notas por correo, versión móvil, pagos, retroalimentación pedagógica elaborada (la justificación por nota sí entra).

## Usuario y alcance del MVP

**Usuario principal:** profesor de colegio o universidad, en ciencias naturales y STEM, con grupos de unos 40 estudiantes y entre 3 y 7 cursos. Usa poca tecnología (Excel y Moodle en el mejor caso, casi el 60% solo papel) y trabaja desde un computador. En esta fase es el único que toca el resultado y quien decide y paga la herramienta.

**Tipo de evaluación:** enunciado, desarrollo matemático y resultado final (el caso dominante). También hay opción múltiple, verdadero/falso y código; muy pocos ensayos. El idioma inicial es español, pero el sistema debe ser agnóstico de idioma y de materia.

**Formato de entrada:** papel (escaneado o fotografiado y subido desde el computador), PDF o Word.

| Funcionalidad | Prioridad | Nota |
| --- | --- | --- |
| Cuentas de usuario, cursos y guardado de historial | P1 | Todo es por usuario y curso |
| Crear evaluador: subir enunciado y clave, rúbrica o 3 ejemplos | P1 | La IA propone criterios y el profesor los valida |
| Subir lote de exámenes (PDF o imagen) con validación de calidad | P1 | Detecta fotos ilegibles al subir |
| Identificar estudiante (nombre o código) por examen | P1 | Si no se infiere, se marca para el profesor |
| Leer manuscrito desde foto o escaneo | P1 | Es el mayor riesgo técnico |
| Calificar: opción múltiple, V/F, respuesta corta y desarrollo con rúbrica | P1 | Con justificación y confianza por criterio |
| Procesamiento asíncrono de lotes con progreso | P1 | Un solo modo |
| Revisión y ajuste manual, aceptación individual y masiva | P1 | Nunca hay nota final sin aprobación |
| Exportar a Excel o CSV y PDF por estudiante | P2 | Es lo primero que se sacrifica si falta tiempo |
| Informe de análisis por pregunta y por grupo | P2 | Insights para el profesor |
| Descargar resultados anteriores | P2 | Del examen actual y de los anteriores |
| Retroalimentación pedagógica elaborada | Fuera | La justificación por nota sí es P1 |
| Chatbot para crear exámenes, portal de estudiantes, LMS, correo, móvil, pagos | Fuera | Iteraciones futuras |

## Flujo del profesor

*Diagrama (versión en texto) — flujo del profesor, 8 pasos y 1 decisión:*

1. Crea el evaluador (enunciado y criterios).
2. Fija los criterios (la IA propone, el profesor edita).
3. Sube los exámenes (PDF o foto, con aviso de calidad).
4. Lanza el lote (asíncrono, con avance).
5. La IA califica (nota y justificación).
   - Decisión: ¿hay duda? Si no, pasa directo a la revisión. Si sí, se escala la duda a un modelo más capaz; si la duda sigue, el examen queda como "requiere revisión". Luego pasa a la revisión.
6. Revisa primero los exámenes más distintos.
7. Aprueba las notas, una por una o en masa (ninguna nota es final hasta este paso).
8. Descarga notas e informe.

La IA propone y marca lo dudoso; el profesor revisa primero los exámenes más distintos y aprueba, uno por uno o en masa. Los pasos 1 a 3 se hacen una vez por examen; los pasos 4 a 8, una vez por lote.

## Arquitectura

*Diagrama (versión en texto) — arquitectura, 2 apps sobre AWS:*

- **App 1 · Front (React):** corre en el navegador del profesor; hosting en S3 + CloudFront. Inicia sesión con Amazon Cognito, llama a la API por HTTPS con token y sube los archivos directo a S3 con URLs firmadas.
- **App 2 · API en Python (FastAPI en ECS Fargate tras un ALB):** valida el token, firma URLs de S3, lee y escribe en la base de datos y **encola** trabajos en Amazon SQS (con cola de errores).
- **Workers (mismo código que la API, pipeline de IA con LangGraph):** toman trabajos de la cola, leen los exámenes en S3, llaman al proveedor de modelos de IA (fuera de AWS) para leer y calificar, y guardan las notas en la base de datos.
- **Datos:** Amazon RDS PostgreSQL (cursos, evaluadores, lotes, notas, auditoría) y Amazon S3 (exámenes, privado y cifrado).
- La cola es lo que separa a la API de la calificación con IA.

La API responde de inmediato y deja el trabajo en la cola; los workers, que comparten el código de la API, califican en segundo plano. El navegador sube los archivos directo a S3 con una URL firmada por la API, y tanto la API como los workers guardan en la base relacional. Todo corre en AWS salvo el proveedor de modelos de IA.

## Pipeline de IA

La IA propone y el profesor decide. El pipeline se implementa como un grafo de etapas (LangGraph) que corre dentro de los workers, una ejecución por examen. Cada etapa guarda su resultado, su confianza y su costo.

1. **Validación de entrada (en la subida).** Revisa formato, número de páginas, nitidez, rotación y recorte. Si la imagen no es legible, el profesor lo sabe de inmediato y puede repetir la foto.
2. **Segmentación e identificación.** Agrupa páginas por estudiante e intenta inferir nombre o código. Si no puede, marca el examen para que el profesor lo asigne.
3. **Transcripción.** Un modelo de visión económico separa las respuestas por pregunta o ejercicio y transcribe el desarrollo y el resultado final.
4. **Calificación por criterio.** Aplica la rúbrica aprobada. Cada criterio recibe un puntaje sobre 10 o un resultado binario (cumple / revisar) mediante un juez LLM, y luego se escala a la escala del profesor. Cada puntaje trae una justificación que cita lo que el estudiante escribió.
5. **Confianza.** Cada criterio recibe un nivel de confianza. Una respuesta ambigua registra por qué lo es.
6. **Escalamiento.** Con baja confianza, el examen pasa por un modelo más capaz. Si persiste la duda, queda como "requiere revisión" con la explicación de lo ocurrido.
7. **Persistencia.** Se guardan transcripción, notas propuestas, justificaciones, confianza, modelo usado y costo.

**Reglas de producto**

- La nota final nunca se decide sin aprobación del profesor.
- Un error con alta confianza no lo detecta la máquina, por eso el profesor revisa primero los casos más distintos del lote (menor confianza y mayor desviación frente a la distribución de notas; criterio de ordenamiento propuesto) y puede aceptar en masa el resto.
- Lo ilegible se detecta al subir; lo ambiguo se explica al profesor.
- El modelo se esconde detrás de una interfaz propia (un adaptador por proveedor) para comparar modelos sin tocar el resto del sistema.
- Primero calidad con un modelo de referencia, después bajar costos y comparar alternativas.

## Modelo de datos

Base relacional (propuesta: PostgreSQL en Amazon RDS). Los archivos pesados (PDF e imágenes) viven en S3; la base guarda solo su metadata y su clave. Toda fila pertenece a un usuario, directamente o a través de su curso, y cada consulta se filtra por ese dueño.

| Tabla | Para qué sirve | Campos clave | Relaciones |
| --- | --- | --- | --- |
| users | Profesor autenticado | id, email, nombre, id externo del proveedor de identidad, consentimiento (fecha y versión), creado | 1 a muchos con courses |
| courses | Curso o grupo | id, user_id, nombre, periodo | 1 a muchos con evaluators |
| evaluators | Evaluador de un examen o taller | id, course_id, nombre, escala máxima, estado, versión vigente | 1 a muchos con evaluator_versions y batches |
| evaluator_versions | Versión aprobada de los criterios | id, evaluator_id, número, estado (borrador / aprobada), aprobado_en | 1 a muchos con criteria y reference_examples |
| criteria | Criterio de calificación | id, version_id, referencia de pregunta, descripción, puntaje máximo, tipo (clave / rúbrica / ejemplo), orden | 1 a muchos con grade_items |
| reference_examples | Ejemplos calificados aportados por el profesor | id, version_id, file_id, nota, comentario | Pertenece a evaluator_versions |
| files | Metadata de cada archivo en S3 | id, dueño, clave S3, tipo MIME, número de páginas, hash, creado | Referenciada por páginas y ejemplos |
| batches | Lote de exámenes a calificar | id, evaluator_id, versión usada, estado, total de exámenes, costo acumulado, creado | 1 a muchos con submissions |
| submissions | Examen de un estudiante | id, batch_id, código o nombre, identificado (sí/no), estado, banderas de calidad | 1 a muchos con submission_pages y transcriptions; 1 a 1 con grades |
| submission_pages | Páginas del examen | id, submission_id, file_id, número de página | Pertenece a submissions |
| transcriptions | Texto leído por pregunta | id, submission_id, referencia de pregunta, texto, modelo, confianza | Pertenece a submissions |
| grades | Nota agregada del examen | id, submission_id, nota IA, nota final, estado (pendiente / aceptada / editada / requiere revisión), aprobado_por, aprobado_en | 1 a muchos con grade_items |
| grade_items | Puntaje por criterio | id, grade_id, criterion_id, puntaje IA, puntaje final, justificación, confianza, escalado (sí/no) | 1 a muchos con grade_audit_log |
| grade_audit_log | Historial de cambios de nota | id, grade_item_id, user_id, valor anterior, valor nuevo, motivo, fecha | Pertenece a grade_items |
| jobs | Trabajo asíncrono por examen | id, submission_id, etapa, estado, intentos, error | Pertenece a submissions |
| model_runs | Cada llamada a un modelo | id, job_id, etapa, modelo, tokens de entrada y salida, costo, latencia | Pertenece a jobs |
| exports | Archivos generados para descargar | id, batch_id, tipo (Excel / CSV / PDF), file_id, creado | Pertenece a batches |

**Reglas de datos**

- Las versiones de criterios son inmutables una vez aprobadas; un cambio crea una versión nueva, y cada lote recuerda con cuál se calificó.
- Toda edición de nota queda en grade_audit_log, porque el estudiante puede pedir una auditoría.
- model_runs es la fuente del costo por examen y por lote.

## Contrato de la API

API REST en JSON bajo `/v1`, documentada con OpenAPI; el front se genera o valida contra ese contrato. Autenticación con token del proveedor de identidad en cada llamada. Errores con formato estándar (código, mensaje, detalle), listas paginadas e `Idempotency-Key` en las operaciones que lanzan trabajo. El progreso de un lote se consulta por polling; si hace falta tiempo real se pasa a eventos más adelante.

| Método y ruta | Qué hace | Respuesta |
| --- | --- | --- |
| GET /v1/me | Datos del profesor autenticado | 200 |
| GET, POST /v1/courses | Lista y crea cursos | 200, 201 |
| POST /v1/courses/{id}/evaluators | Crea un evaluador con enunciado y fuente de criterios | 201 |
| POST /v1/evaluators/{id}/criteria:propose | La IA propone criterios a partir del enunciado y la clave, la rúbrica o los ejemplos | 202, luego consulta |
| PUT /v1/evaluators/{id}/criteria | El profesor edita los criterios | 200 |
| POST /v1/evaluators/{id}/approve | Aprueba la versión de criterios | 200 |
| POST /v1/files:presign | Entrega una URL prefirmada para subir un archivo a S3 | 200 |
| POST /v1/evaluators/{id}/batches | Crea un lote | 201 |
| POST /v1/batches/{id}/submissions | Registra los archivos subidos y devuelve la validación de calidad | 201 |
| POST /v1/batches/{id}/start | Lanza la calificación asíncrona (requiere Idempotency-Key) | 202 |
| GET /v1/batches/{id} | Estado y progreso del lote, con costo acumulado | 200 |
| GET /v1/batches/{id}/results | Resultados con filtros por confianza, estado y discrepancia | 200 |
| GET /v1/submissions/{id} | Documento, transcripción, notas, justificaciones y anotaciones | 200 |
| PATCH /v1/grade-items/{id} | Edita un puntaje y registra el motivo | 200 |
| POST /v1/batches/{id}/accept | Acepta en masa los exámenes indicados o todos los no marcados | 200 |
| GET /v1/batches/{id}/report | Informe de análisis por pregunta y grupo | 200 |
| POST /v1/batches/{id}/exports, GET /v1/exports/{id} | Genera y descarga Excel, CSV o PDF | 202, 200 |

## Calidad de la IA, métricas y costo por examen

La calidad se mide contra un **conjunto de referencia (golden set)**: el examen real del profesor piloto, su clave o rúbrica y las respuestas de sus estudiantes, calificadas por él mismo. Cada cambio de modelo, de prompt o de rúbrica se evalúa contra ese conjunto antes de llegar a producción.

| Métrica | Cómo se mide | Umbral |
| --- | --- | --- |
| Concordancia de la nota con el profesor | Porcentaje de exámenes y de criterios donde la nota de la IA coincide con la del profesor (la tolerancia en puntos se define con el golden set) | Objetivo 95%, mínimo 90% |
| Exactitud de la transcripción | Error en cifras y resultados finales sobre una muestra revisada a mano | Por definir con el golden set |
| Detección de errores | De las notas equivocadas, qué fracción quedó marcada con baja confianza o "requiere revisión" | Por definir con el golden set |
| Justificaciones sin sustento | Citas de la justificación que no aparecen en la transcripción | 0 |
| Costo de IA por examen | Suma de model_runs del examen | 45 COP o menos (propuesto) |
| Tiempo de un lote | Desde el inicio hasta el último examen listo | 15 minutos o menos para 40; menos de 24 horas para 100 |

**Control de alucinaciones:** salidas estructuradas validadas contra un esquema, justificación obligatoria con cita verificable en la transcripción, temperatura baja, escalamiento por baja confianza y aprobación humana de toda nota final.

**Costo por examen.** Los componentes son la transcripción (por página), la calificación (por examen y por criterio), el escalamiento (fracción de exámenes que lo necesita) y la infraestructura de AWS (base de datos, almacenamiento, cola y cómputo). Con 50.000 COP al mes y 560 exámenes, el ingreso es de unos 89 COP por examen.

Palancas para bajar el costo después de fijar la línea base: modelo de visión más barato, reducir la resolución de las imágenes cuando no afecte la lectura, reutilizar el prefijo de criterios entre llamadas, usar la modalidad de lotes con descuento del proveedor cuando exista y escalar solo lo dudoso. La API muestra el costo acumulado de cada lote y permite fijar un tope por lote.

## Seguridad, privacidad y consentimiento

La aplicación maneja exámenes de estudiantes con nombre o código y, a futuro en colegios, posiblemente de menores de edad. En la versión 0 no se espera trabajar con menores, pero el diseño parte de que el producto sí llegará a ellos.

- **Consentimiento:** antes de enviar exámenes a una API de IA externa se pide permiso al profesor, y a la institución cuando aplique. La fecha y la versión del texto aceptado se guardan en la cuenta.
- **Minimización:** se usa el código del estudiante en lugar del nombre cuando sea posible y a la IA solo se envía lo necesario para calificar.
- **Cifrado:** TLS en tránsito; cifrado en reposo en la base de datos y en S3 con llaves administradas.
- **Archivos:** buckets privados; descarga y subida solo con URLs prefirmadas de corta duración.
- **Aislamiento:** cada consulta se filtra por el dueño de los datos; un profesor nunca ve cursos, lotes ni exámenes de otro.
- **Secretos y logs:** credenciales en un gestor de secretos; los registros no contienen el contenido de los exámenes.
- **Proveedor de IA:** confirmar en sus términos y configuración que los datos enviados no se usan para entrenar modelos.
- **Retención y borrado:** el profesor puede borrar un lote y sus archivos; el plazo de retención por defecto queda como decisión abierta.
- **Normativa:** aplica la ley de protección de datos personales del país de operación (habeas data en Colombia). Conviene una revisión legal antes de abrir el producto a colegios o a menores.

## Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación | Tarea |
| --- | --- | --- | --- |
| El modelo de visión lee mal el manuscrito matemático (cifras, signos, subíndices) | Notas equivocadas desde la primera etapa | Prueba de 3 a 5 hojas reales con 2 modelos antes de construir; validación de calidad al subir; escalamiento por baja confianza | E1, E2, D2 |
| No hay examen real para medir | No se puede probar el 90% | El fundador consigue el ejemplo con clave y respuestas antes de empezar el motor | E1 |
| Alucinaciones: justificaciones o notas inventadas | Pérdida de confianza del profesor | Citas verificables, salidas estructuradas, aprobación humana obligatoria | E3, E4 |
| Error con alta confianza que nadie detecta | Nota injusta publicada | Revisión priorizada por discrepancia, muestreo aleatorio en la revisión y auditoría de cambios | G2, G3 |
| El costo por examen supera el ingreso (89 COP) | El producto pierde dinero | Medición por examen, tope por lote, palancas de optimización tras la línea base | E5 |
| Profesores con baja familiaridad tecnológica | No lo adoptan | Flujo guiado y simple; el piloto lo usa sin ayuda | I3 |
| Datos de estudiantes sin consentimiento claro | Riesgo legal y de reputación | Consentimiento registrado, minimización, revisión legal | I2 |
| Dependencia de un solo proveedor de IA | Cambios de precio o servicio | Adaptador por proveedor y golden set para comparar | E2, E3 |
| Lotes que fallan a medias | Resultados incompletos | Trabajos por examen, reintentos, idempotencia y cola de errores | F1, F2 |
| El precio de 50.000 COP al mes no está validado | El modelo de negocio no cierra | Preguntar la disposición a pagar al piloto y a otros profesores | I3 |

## Plan de tareas

Las tareas se agrupan en nueve épicas (A a I). Cada tarea trae su **objetivo**, sus **criterios de aprobación**, sus **pruebas borde** (los casos límite que deben probarse), la **tecnología** y los **acuerdos con otras áreas**. No se estiman horas: el orden lo da la columna "Depende de".

**Áreas y qué aporta cada una**

| Área | Responsabilidad | Lo que entrega a las demás |
| --- | --- | --- |
| Front | Aplicación React: pantallas, subida, revisión y descargas | Necesidades de la API; textos y flujos |
| API | Aplicación Python (FastAPI) y workers: reglas de negocio, orquestación y contrato | Contrato OpenAPI, estados de lote, errores estándar |
| Datos | Esquema relacional, migraciones, índices y reglas de integridad | Esquema versionado y diccionario de datos |
| IA | Pipeline de transcripción y calificación, golden set, métricas y costo | Interfaz del pipeline, resultados con confianza y costo |
| Infraestructura | AWS como código, CI/CD, ambientes, observabilidad y secretos | URLs, roles, variables de entorno y límites operativos |
| Producto y piloto | Prioridades, ejemplo real, criterios de aceptación, pruebas con el profesor | Golden set, textos, decisiones abiertas |
| Legal y privacidad | Consentimiento, retención y normativa | Textos legales y reglas de retención |

**Acuerdos transversales (contratos entre áreas)**

1. **Front y API:** el contrato OpenAPI es la fuente de verdad; un cambio que rompe compatibilidad exige una versión nueva.
2. **API y Datos:** todo cambio de esquema pasa por una migración revisada; ninguna consulta de datos de usuario omite el filtro de dueño.
3. **API e IA:** el pipeline recibe un identificador de examen y una versión de criterios, y devuelve transcripciones y puntajes por criterio con justificación, confianza, modelo y costo, en JSON validado contra un esquema.
4. **Infraestructura y el resto:** dos ambientes (dev y prod), secretos en un gestor, límites documentados (tamaño de archivo, tiempos máximos).
5. **Producto e IA:** el golden set y los umbrales de la sección de calidad son el criterio de aceptación del motor.
6. **Legal y Producto:** el texto de consentimiento se aprueba antes de que el primer profesor ajeno al equipo suba exámenes.

**Definición de terminado (común a todas):** código revisado, pruebas automáticas pasando, contrato OpenAPI y diccionario de datos actualizados, errores y métricas visibles en los registros, y criterios de aprobación de la tarea verificados.

**Mapa de tareas**

| ID | Tarea | Prioridad | Depende de |
| --- | --- | --- | --- |
| A1 | Infraestructura base en AWS como código | P1 | — |
| A2 | Repositorios, CI/CD y ambientes | P1 | A1 |
| B1 | Esquema relacional y migraciones | P1 | A1 |
| B2 | Autenticación y aislamiento por usuario | P1 | A1, B1 |
| B3 | Cursos | P1 | B2 |
| C1 | Creación de evaluador | P1 | B3, D1 |
| C2 | Propuesta de criterios por IA y aprobación | P1 | C1, E1 |
| D1 | Carga segura de archivos | P1 | A1, B2 |
| D2 | Validación de calidad al subir | P1 | D1 |
| D3 | Identificación del estudiante y agrupación de páginas | P1 | D2, E2 |
| E1 | Golden set y arnés de evaluación | P1 | Ejemplo real del fundador |
| E2 | Transcripción de manuscrito con visión | P1 | E1 |
| E3 | Calificación por criterio con justificación y confianza | P1 | E2, C2 |
| E4 | Escalamiento por baja confianza y verificación de citas | P1 | E3 |
| E5 | Medición y control de costos | P1 | E3, B1 |
| F1 | Cola de trabajos, workers y estados de lote | P1 | A1, B1 |
| F2 | Reintentos, idempotencia y manejo de fallas | P1 | F1 |
| G1 | Pantalla de resultados con documento anotado | P1 | E3, F1 |
| G2 | Edición, aceptación individual y masiva, priorización de casos | P1 | G1 |
| G3 | Auditoría de cambios de nota | P1 | B1, G2 |
| H1 | Exportación a Excel, CSV y PDF por estudiante | P2 | G2 |
| H2 | Informe de análisis por pregunta y grupo | P2 | G2 |
| I1 | Observabilidad y alertas | P1 | A2 |
| I2 | Seguridad, privacidad y consentimiento | P1 | B2 |
| I3 | Piloto con el profesor y medición | P1 | Todas las P1 |

## Épica A — Fundaciones

### A1 · Infraestructura base en AWS como código

- **Objetivo:** tener en AWS, de forma repetible, todo lo que las dos aplicaciones necesitan para correr de manera segura, en dos ambientes (dev y prod).
- **Criterios de aprobación:**
  - Un solo comando crea y otro destruye un ambiente completo desde cero.
  - Existen red privada, base PostgreSQL cifrada con copias automáticas, buckets S3 privados y cifrados, cola con cola de errores, proveedor de identidad, registro de imágenes, cómputo para API y workers, balanceador, distribución del front y gestor de secretos.
  - Dev y prod usan la misma definición con valores distintos.
  - El costo mensual estimado de cada ambiente está documentado.
- **Pruebas borde:** destruir y recrear sin dejar recursos huérfanos; restaurar una copia de la base y verificar los datos; intentar acceso público a un bucket y que falle; rotar un secreto sin tumbar la API; cuenta nueva de AWS con límites de servicio bajos.
- **Tecnología:** Terraform (alternativa: AWS CDK en Python); VPC, RDS PostgreSQL, S3, SQS, Cognito, ECR, ECS Fargate, ALB, CloudFront, Secrets Manager, KMS.
- **Acuerdos con otras áreas:** Infraestructura entrega a API y Front nombres de recursos, variables de entorno y roles de mínimo privilegio, y documenta los límites (tamaño máximo de archivo, tiempos máximos). Producto aprueba el presupuesto mensual de infraestructura y la región de AWS (decisión abierta).

### A2 · Repositorios, CI/CD y ambientes

- **Objetivo:** que cada cambio se pruebe y se despliegue de forma repetible a dev y, con aprobación, a prod.
- **Criterios de aprobación:**
  - Repositorios separados para front, API e infraestructura.
  - Cada cambio ejecuta análisis estático, pruebas y construcción; el merge a la rama principal despliega a dev.
  - El despliegue a prod requiere aprobación manual y las migraciones corren como parte del despliegue.
  - Volver a la versión anterior toma minutos y está documentado.
  - Ningún secreto vive en el repositorio.
- **Pruebas borde:** una migración que falla a la mitad detiene el despliegue; dos despliegues simultáneos; volver atrás después de aplicar una migración (las migraciones son compatibles hacia atrás); dependencia con vulnerabilidad conocida.
- **Tecnología:** GitHub Actions con identidad federada (OIDC) hacia AWS, Docker, Alembic, ruff y pytest en Python, eslint y vitest en el front.
- **Acuerdos con otras áreas:** Front y API acuerdan convención de ramas y versionado del contrato; Infraestructura concede al pipeline permisos de mínimo privilegio sin llaves estáticas.

## Épica B — Datos y API base

### B1 · Esquema relacional y migraciones

- **Objetivo:** crear el modelo de datos descrito en este documento con migraciones versionadas.
- **Criterios de aprobación:**
  - Todas las tablas tienen claves primarias y foráneas, restricciones (no nulos, únicos, rangos de puntaje) e índices para las consultas frecuentes (lote a exámenes, examen a ítems).
  - Las migraciones se aplican hacia adelante y hacia atrás en un ambiente limpio.
  - Hay datos de semilla para desarrollo y un diagrama del esquema publicado.
  - La tabla de usuarios incluye fecha y versión del consentimiento.
  - La consulta de resultados de un lote de 40 exámenes responde en menos de 500 ms.
- **Pruebas borde:** dos ediciones simultáneas de la misma nota (control de versión optimista); puntaje fuera de rango; examen sin estudiante identificado; borrar un lote y sus archivos en S3; criterio con notas existentes (no se puede modificar, se crea una versión); tildes, ñ y emoji en nombres; 10.000 filas de ítems de nota.
- **Tecnología:** PostgreSQL (RDS), SQLAlchemy 2, Alembic, identificadores UUID, marcas de tiempo con zona horaria.
- **Acuerdos con otras áreas:** Datos publica el esquema y API lo consume; no se crean tablas fuera de migraciones. IA y Datos acuerdan qué tablas escribe el pipeline (transcriptions, grade_items, model_runs). Producto y Legal confirman los campos de consentimiento.

### B2 · Autenticación y aislamiento por usuario

- **Objetivo:** que el profesor entre con correo y clave y que cada uno vea solo sus propios datos.
- **Criterios de aprobación:**
  - Registro, inicio y cierre de sesión y recuperación de clave funcionan.
  - La API valida el token en cada llamada y filtra por dueño en cada consulta.
  - Pedir un recurso ajeno devuelve 404, no 403.
  - Hay pruebas automáticas de acceso cruzado entre dos usuarios.
  - Los intentos fallidos repetidos se limitan.
- **Pruebas borde:** token vencido en medio de una subida larga (se renueva sin perder el lote); correo con mayúsculas; correo sin verificar; dos pestañas con sesiones distintas; identificador adivinado de otro usuario; usuario eliminado con datos existentes.
- **Tecnología:** Amazon Cognito (propuesta), tokens JWT, dependencias de FastAPI, flujo de autenticación en React.
- **Acuerdos con otras áreas:** Front y API acuerdan manejo de tokens y mensajes de error; Infraestructura provee el grupo de usuarios; Legal entrega el texto de consentimiento que se muestra en el registro.

### B3 · Cursos

- **Objetivo:** que el profesor cree y vea sus cursos y, dentro de cada uno, los evaluadores y exámenes anteriores.
- **Criterios de aprobación:**
  - Crear, editar y archivar cursos.
  - Al entrar se ve la lista de cursos; dentro de un curso, los evaluadores anteriores y el botón "Nuevo evaluador".
  - Los estados vacíos explican qué hacer.
  - Los textos están en español con soporte para otros idiomas.
- **Pruebas borde:** nombre vacío o de 300 caracteres; dos cursos con el mismo nombre; archivar un curso con un lote en proceso; profesor con 50 cursos; emoji en el nombre.
- **Tecnología:** FastAPI y Pydantic; React con TypeScript; cliente generado desde OpenAPI; react-i18next.
- **Acuerdos con otras áreas:** Front y API firman los esquemas del recurso en OpenAPI antes de implementar; Producto aprueba los textos.

## Épicas C y D — Evaluadores e ingesta

### C1 · Creación de evaluador

- **Objetivo:** que el profesor cree un evaluador cargando el enunciado y la fuente de criterios (clave, rúbrica o 3 ejemplos calificados).
- **Criterios de aprobación:**
  - Formulario guiado por pasos: nombre, enunciado, fuente de criterios y escala de la nota (por ejemplo 0–5, 0–10 o 0–100).
  - Acepta PDF e imagen; el soporte de Word queda como decisión abierta.
  - Con la opción de ejemplos exige al menos 3 ejemplos calificados.
  - Se guarda como borrador y se puede retomar después.
- **Pruebas borde:** enunciado de 40 páginas; archivo corrupto; PDF con contraseña; solo 2 ejemplos (se bloquea con un mensaje claro); nota de un ejemplo por encima de la escala; cerrar el navegador a mitad del proceso; dos evaluadores con el mismo nombre.
- **Tecnología:** React con formularios por pasos (react-hook-form y zod), FastAPI, subida a S3 con URL prefirmada.
- **Acuerdos con otras áreas:** Front y API acuerdan los estados del evaluador (borrador, criterios propuestos, aprobado); Datos garantiza el versionado; Producto fija textos y límites de tamaño.

### C2 · Propuesta de criterios por IA y aprobación

- **Objetivo:** que la IA convierta el enunciado y la fuente en criterios explícitos, y que el profesor los edite y apruebe, congelando una versión.
- **Criterios de aprobación:**
  - La propuesta se genera sin bloquear la pantalla y muestra su progreso.
  - Hay criterios por pregunta con descripción, puntaje máximo y tipo (clave, rúbrica o ejemplo); los puntajes suman la escala elegida.
  - El profesor puede editar, agregar, borrar y reordenar.
  - Al aprobar se crea una versión inmutable y sin aprobación no se puede lanzar un lote.
  - El profesor piloto confirma que los criterios propuestos reflejan su intención con pocas ediciones.
- **Pruebas borde:** pregunta sin puntaje en el enunciado; puntajes que no suman la escala (aviso); rúbrica ambigua; criterio para una pregunta que no existe; ejemplos que se contradicen; editar tras aprobar (genera versión nueva); enunciado en otro idioma.
- **Tecnología:** pipeline LangGraph con salida estructurada validada contra un esquema; endpoint asíncrono criteria:propose; editor de tabla en React.
- **Acuerdos con otras áreas:** IA y API fijan el esquema JSON de criterios; Producto valida con el piloto; Datos garantiza que una versión aprobada no se modifica.

### D1 · Carga segura de archivos

- **Objetivo:** subir PDF e imágenes de forma fiable, directo a S3.
- **Criterios de aprobación:**
  - URLs prefirmadas de corta duración y archivos privados.
  - Subida de varios archivos en paralelo, con progreso y reintento por archivo.
  - Tipos permitidos (PDF, JPG, PNG, y HEIC convertido); límites de tamaño y de páginas configurables.
  - Hash del archivo para detectar duplicados; metadata guardada en la tabla files.
- **Pruebas borde:** archivo de 0 bytes; ejecutable renombrado como PDF (se verifica el tipo real); 200 archivos a la vez; pérdida de conexión a mitad; el mismo archivo dos veces; nombres con caracteres especiales; URL prefirmada vencida.
- **Tecnología:** S3 con subida directa (multiparte para archivos grandes), FastAPI, un componente de carga en React, verificación de tipo real (python-magic) y conversión HEIC (pillow-heif).
- **Acuerdos con otras áreas:** Infraestructura configura CORS y límites del bucket; API registra el archivo solo después de confirmar la subida; Front define la experiencia de progreso; Legal fija la retención.

### D2 · Validación de calidad al subir

- **Objetivo:** avisar al profesor de inmediato si una foto o un PDF no sirve para calificar.
- **Criterios de aprobación:**
  - Por página se revisan nitidez, orientación, recorte, resolución mínima y página en blanco.
  - El profesor ve miniaturas marcadas como correcta, revisar o repetir, con el motivo.
  - Puede forzar el uso de una página marcada.
  - Los umbrales salen del golden set, balanceando falsos positivos y falsos negativos.
- **Pruebas borde:** foto con sombra; hoja rotada 90 o 180 grados; dos hojas en una sola foto; página casi en blanco que es una respuesta vacía legítima; PDF escaneado a muy baja resolución; PDF con texto digital en lugar de manuscrito; hojas fuera de orden.
- **Tecnología:** Pillow y OpenCV (nitidez, bordes, orientación) en Python; opcionalmente un modelo de visión liviano para casos dudosos.
- **Acuerdos con otras áreas:** IA define y calibra los umbrales; API expone las banderas de calidad en cada examen; Front muestra los motivos en lenguaje simple.

### D3 · Identificación del estudiante y agrupación de páginas

- **Objetivo:** saber de quién es cada examen y agrupar sus páginas.
- **Criterios de aprobación:**
  - Se infiere el nombre o el código del encabezado y se agrupan las páginas de un mismo examen.
  - Si no se logra, el examen queda marcado y el profesor lo asigna antes de lanzar el lote.
  - El lote informa cuántos exámenes quedaron sin identificar.
  - La identificación alcanza el umbral definido con el golden set.
- **Pruebas borde:** nombre ilegible; dos estudiantes con el mismo nombre; códigos con dígitos confusos (1 y 7, 0 y O); encabezado en la segunda página; páginas de dos estudiantes mezcladas; examen sin código; hojas adicionales.
- **Tecnología:** modelo de visión sobre el recorte del encabezado, coincidencia aproximada de texto (rapidfuzz) contra una lista opcional, reglas de agrupación por orden de subida.
- **Acuerdos con otras áreas:** Producto decide si se pide una lista de estudiantes (decisión abierta); IA y API acuerdan la salida (referencia del estudiante y confianza); Legal prefiere el código sobre el nombre.

## Épicas E y F — Motor de calificación y procesamiento asíncrono

### E1 · Golden set y arnés de evaluación

- **Objetivo:** tener un conjunto de referencia y un programa que mida, de forma repetible, qué tan bien califica el pipeline frente al profesor.
- **Criterios de aprobación:**
  - El conjunto incluye el examen real, su clave o rúbrica y las respuestas de al menos los 40 estudiantes del piloto, con la nota del profesor por criterio.
  - Un comando ejecuta el pipeline sobre el conjunto y reporta concordancia por examen y por criterio, exactitud de la transcripción, detección de errores y costo.
  - Se comparan al menos 2 modelos de visión sobre una muestra de 3 a 5 hojas antes de elegir el de referencia (baseline).
  - Los datos del conjunto están anonimizados y guardados fuera del repositorio.
- **Pruebas borde:** hojas con tachones; letra muy pequeña; fórmulas con fracciones y subíndices; respuestas en blanco; el profesor califica distinto el mismo tipo de error en dos exámenes (se mide la propia inconsistencia del profesor); resultados no deterministas entre corridas.
- **Tecnología:** Python, pytest, un registro de experimentos sencillo (tablas y archivos versionados), datos en S3 privado.
- **Acuerdos con otras áreas:** Producto (el fundador) consigue y entrega el ejemplo real antes de empezar; IA y Producto firman los umbrales de aceptación; Legal confirma la anonimización y el permiso de uso.

### E2 · Transcripción de manuscrito con visión

- **Objetivo:** convertir cada página manuscrita en texto estructurado por pregunta, conservando el desarrollo y el resultado final.
- **Criterios de aprobación:**
  - Salida JSON por examen con pregunta, texto del desarrollo, resultado final y confianza.
  - La exactitud sobre el golden set alcanza el umbral acordado.
  - El modelo se invoca mediante un adaptador, de modo que cambiar de proveedor no toca el resto.
  - Cada llamada registra tokens, costo y latencia en model_runs.
- **Pruebas borde:** respuestas que cruzan páginas; matemática con fracciones, raíces y subíndices; dibujos y gráficas; código escrito a mano; tinta tenue; texto en dos idiomas; página con respuesta tachada y reescrita.
- **Tecnología:** modelo de visión económico (proveedor por decidir en E1), LangGraph, Pydantic para validar la salida.
- **Acuerdos con otras áreas:** IA y API fijan el esquema de transcripción; Datos define las columnas de transcriptions; Infraestructura gestiona la clave del proveedor en el gestor de secretos.

### E3 · Calificación por criterio con justificación y confianza

- **Objetivo:** aplicar la rúbrica aprobada a cada transcripción y devolver puntaje, justificación y confianza por criterio.
- **Criterios de aprobación:**
  - Cada criterio recibe un puntaje (sobre 10 o binario) que se escala a la escala del profesor.
  - Cada justificación cita lo que el estudiante escribió y es entendible como retroalimentación.
  - La salida cumple un esquema estricto; una salida inválida se reintenta.
  - La concordancia sobre el golden set alcanza al menos 90%.
  - Ningún puntaje excede el máximo del criterio.
- **Pruebas borde:** respuesta correcta con procedimiento incorrecto; respuesta incorrecta con procedimiento correcto (puntos parciales); error arrastrado de un paso previo; respuesta equivalente expresada de otra forma; respuesta vacía; criterios que se solapan; rúbrica que da puntaje por método alternativo.
- **Tecnología:** LangGraph, salidas estructuradas, juez LLM por criterio, temperatura baja, escalado de puntaje en código (no en el modelo).
- **Acuerdos con otras áreas:** Producto aprueba la regla de puntos parciales y de error arrastrado con el piloto; Datos define grade_items; API fija el formato de resultados que consume el front.

### E4 · Escalamiento por baja confianza y verificación de citas

- **Objetivo:** que lo dudoso se revise con un modelo más capaz o llegue al profesor con una explicación, y que ninguna justificación cite algo inexistente.
- **Criterios de aprobación:**
  - Un umbral de confianza decide cuándo repetir con un modelo más capaz.
  - Si la duda persiste, el examen queda como "requiere revisión" con el motivo escrito.
  - Una verificación automática comprueba que cada cita exista en la transcripción; si no existe, la justificación se rechaza y se repite.
  - Sobre el golden set, la mayoría de las notas equivocadas queda marcada (umbral definido en E1).
- **Pruebas borde:** alta confianza con nota equivocada (se mide cuántas hay); escalar el 100% de los exámenes por un umbral mal calibrado (el costo se dispara); cita con pequeñas diferencias de transcripción; el modelo más capaz contradice al primero.
- **Tecnología:** LangGraph con aristas condicionales, comparación aproximada de cadenas para las citas, métricas por etapa.
- **Acuerdos con otras áreas:** Producto define qué se le muestra al profesor cuando algo queda en revisión; IA entrega a Front la razón estandarizada; E5 vigila el costo del escalamiento.

### E5 · Medición y control de costos

- **Objetivo:** conocer y limitar el costo de cada examen y de cada lote.
- **Criterios de aprobación:**
  - Cada llamada a un modelo escribe en model_runs.
  - La API muestra el costo acumulado de un lote y un estimado antes de lanzarlo.
  - Se puede fijar un tope por lote; al alcanzarlo, el procesamiento se detiene y avisa.
  - Un reporte da el costo medio por examen, a comparar con el techo de 45 COP.
- **Pruebas borde:** lote que supera el tope a mitad; reintentos que duplican el cobro; cambio de precio del proveedor (la tabla de precios es configurable); exámenes de muchas páginas; llamadas fallidas que igual cobran.
- **Tecnología:** tabla model_runs, tabla de precios por modelo configurable, consulta agregada en la API.
- **Acuerdos con otras áreas:** Producto fija el tope por defecto; Datos garantiza la tabla; Front muestra el estimado y el tope; Infraestructura suma el costo de AWS para el costo total por examen.

### F1 · Cola de trabajos, workers y estados de lote

- **Objetivo:** procesar lotes de forma asíncrona, con un trabajo por examen y progreso visible.
- **Criterios de aprobación:**
  - Lanzar un lote devuelve de inmediato y encola un trabajo por examen.
  - Los workers procesan en paralelo con un límite de concurrencia configurable.
  - El estado del lote (en cola, procesando, completo, con errores) y su progreso se consultan por la API.
  - Un lote de 40 exámenes termina en 15 minutos o menos con el modelo de referencia, y uno de 100 en menos de 24 horas.
- **Pruebas borde:** lote de 1 examen y lote de 500; el profesor cierra el navegador mientras procesa; dos lotes simultáneos del mismo profesor; límite de tasa del proveedor de IA; un worker que se cae a mitad de un examen.
- **Tecnología:** Amazon SQS con cola de errores, workers en contenedores ECS Fargate (misma base de código que la API), estado en PostgreSQL.
- **Acuerdos con otras áreas:** API e IA acuerdan la interfaz que invoca el pipeline; Infraestructura define autoescalado y límites; Front acuerda con API los estados y mensajes de progreso.

### F2 · Reintentos, idempotencia y manejo de fallas

- **Objetivo:** que un lote termine bien aunque algunas etapas fallen, sin duplicar cobros ni resultados.
- **Criterios de aprobación:**
  - Cada etapa se reintenta con espera creciente y un número máximo de intentos.
  - Procesar dos veces el mismo examen no duplica notas ni costos (idempotencia).
  - Lo que no se logra tras los reintentos va a la cola de errores y se ve en el lote como "requiere revisión".
  - El profesor puede reintentar un examen fallido desde la pantalla.
- **Pruebas borde:** el proveedor de IA responde con errores 5xx o tarda más del límite; salida inválida repetida; el mensaje de la cola se entrega dos veces; la base de datos no está disponible por unos segundos; archivo dañado que siempre falla.
- **Tecnología:** claves de idempotencia por examen y etapa, reintentos con espera exponencial, cola de errores de SQS.
- **Acuerdos con otras áreas:** API e IA acuerdan qué errores se reintentan y cuáles no; Infraestructura configura las alarmas de la cola de errores; Front muestra el motivo en lenguaje simple.

## Épicas G y H — Revisión del profesor y salidas

### G1 · Pantalla de resultados con documento anotado

- **Objetivo:** mostrar al profesor el documento original con las notas y los comentarios de la IA donde corresponden.
- **Criterios de aprobación:**
  - Lista de exámenes del lote con nota, estado y confianza, ordenable y filtrable.
  - Al abrir un examen: las páginas originales de un lado y, del otro, criterios, puntajes, justificaciones y confianza.
  - Las anotaciones se asocian a la pregunta correspondiente.
  - Los resultados parciales se ven mientras el lote sigue procesando.
  - Un profesor sin experiencia técnica entiende la pantalla sin explicación (se observa en el piloto).
- **Pruebas borde:** exámenes de 1 y de 12 páginas; imágenes muy grandes; examen todavía procesando; PDF con página rotada; pantalla pequeña; justificación muy larga; pérdida breve de conexión.
- **Tecnología:** React con TanStack Query y TanStack Table, pdf.js, capa SVG o canvas para las anotaciones, URLs prefirmadas de lectura.
- **Acuerdos con otras áreas:** API entrega los endpoints de resultados y examen; IA entrega la página y, si el modelo lo permite, la zona aproximada de cada respuesta (si no, las anotaciones quedan por página; decisión abierta); Producto valida el diseño con el piloto.

### G2 · Edición, aceptación individual y masiva, priorización de casos

- **Objetivo:** que el profesor revise con eficiencia y apruebe las notas.
- **Criterios de aprobación:**
  - Editar el puntaje y la justificación de cada criterio, con motivo opcional.
  - Aceptar un examen, o aceptar en masa los que no están marcados, con una confirmación que muestra cuántos son.
  - Orden sugerido "más distintos primero" (menor confianza y mayor desviación frente a la distribución del lote).
  - Un examen marcado "requiere revisión" no se acepta en masa sin abrirlo.
  - La nota solo es final tras la aceptación y se puede deshacer.
- **Pruebas borde:** aceptación masiva con exámenes todavía procesando; dos ediciones simultáneas de la misma nota; aceptar 1 de 40; lote donde todos tienen baja confianza; doble clic en aceptar; puntaje no numérico o fuera de rango; editar y cancelar.
- **Tecnología:** React con actualizaciones optimistas y control de versión; el orden y las reglas de aceptación se calculan en el servidor.
- **Acuerdos con otras áreas:** API define los estados de la nota; Datos aporta el control de versión; IA entrega la señal de discrepancia; Producto fija con el piloto la regla de aceptación masiva y si se sugiere una muestra aleatoria a revisar.

### G3 · Auditoría de cambios de nota

- **Objetivo:** poder explicar por qué un estudiante recibió una nota y qué cambió.
- **Criterios de aprobación:**
  - Cada edición o aceptación escribe quién, cuándo, valor anterior, valor nuevo y motivo.
  - Hay una vista de "auditar nota" por examen con la transcripción, el criterio, la justificación de la IA y los cambios del profesor.
  - El historial no se puede modificar ni borrar desde la aplicación.
- **Pruebas borde:** muchas ediciones seguidas; edición que no cambia el valor (no se registra); cambio hecho por el sistema frente a uno del profesor (se distingue el actor); usuario eliminado; historial muy largo.
- **Tecnología:** tabla de auditoría solo de inserción (permisos sin actualizar ni borrar), vista en React.
- **Acuerdos con otras áreas:** Datos define los permisos de solo inserción; Legal fija la retención del historial; Producto define qué necesita ver el profesor ante un reclamo.

### H1 · Exportación a Excel, CSV y PDF por estudiante (P2)

- **Objetivo:** descargar las notas del lote y de lotes anteriores, y un PDF por estudiante con su documento y sus justificaciones.
- **Criterios de aprobación:**
  - Excel o CSV con una fila por estudiante, una columna por criterio y la nota final; por defecto solo notas aceptadas.
  - PDF por estudiante con el original, las notas y las justificaciones, y descarga de todos en un archivo comprimido.
  - La generación es asíncrona y entrega un enlace temporal.
  - Se pueden descargar los resultados del curso de lotes anteriores.
- **Pruebas borde:** 500 estudiantes; nombres con comas, comillas y tildes (codificación correcta para Excel); celdas que empiezan con = + - o @ (se neutralizan para evitar inyección de fórmulas); exámenes sin identificar; lote con notas sin aceptar; enlace vencido.
- **Tecnología:** openpyxl y csv, ReportLab o WeasyPrint, trabajo asíncrono en los workers, descarga con URL prefirmada.
- **Acuerdos con otras áreas:** API ofrece el trabajo de exportación; Front el botón y el estado; Producto aprueba las columnas con el piloto; Legal define la expiración de los archivos.

### H2 · Informe de análisis por pregunta y grupo (P2)

- **Objetivo:** dar al profesor ideas útiles del lote: dificultad por pregunta, errores comunes y distribución de notas.
- **Criterios de aprobación:**
  - Por pregunta: promedio, porcentaje de acierto y distribución.
  - Distribución de notas del grupo.
  - Errores más frecuentes agrupados, cada uno con ejemplos reales citables.
  - Se calcula solo sobre notas aceptadas y se puede ver en pantalla y descargar.
- **Pruebas borde:** lote de 3 exámenes (aviso de poca muestra); pregunta que nadie respondió; todos con la misma nota; exámenes sin aceptar; agrupación de errores que no corresponde a ningún ejemplo real.
- **Tecnología:** consultas SQL de agregación, gráficos en React (Recharts), resumen de errores comunes con un LLM sobre las justificaciones.
- **Acuerdos con otras áreas:** IA y API acuerdan la llamada de resumen; Datos prepara las vistas de agregación; Producto valida con el piloto qué información le sirve.

## Épica I — Calidad transversal y piloto

### I1 · Observabilidad y alertas

- **Objetivo:** ver qué pasa en producción y enterarse de los problemas antes que el profesor.
- **Criterios de aprobación:**
  - Registros estructurados con identificador de lote y de examen.
  - Métricas de duración por etapa, tasa de error, tamaño de la cola, costo por examen y tiempo total del lote.
  - Alarmas: cola de errores con mensajes, tasa de error alta, costo de un lote sobre su tope y API caída.
  - Los registros no contienen el contenido de los exámenes ni datos personales (hay una prueba automática que lo verifica).
- **Pruebas borde:** pico de 500 exámenes; dato personal que llega a un registro por accidente; alarma que se dispara en bucle (se agrupa); worker colgado sin error (tiempos máximos y latido).
- **Tecnología:** CloudWatch (registros, métricas y alarmas), registros JSON, Sentry opcional para el front.
- **Acuerdos con otras áreas:** Infraestructura crea las alarmas y el canal de aviso; API e IA emiten métricas con nombres acordados; Producto define qué fallas deben avisarle de inmediato.

### I2 · Seguridad, privacidad y consentimiento

- **Objetivo:** cumplir lo definido en la sección de seguridad antes de que el primer profesor ajeno al equipo suba exámenes.
- **Criterios de aprobación:**
  - Texto de consentimiento aprobado, mostrado en el registro, con fecha y versión guardadas.
  - Confirmado que el proveedor de IA no usa los datos para entrenar.
  - Buckets privados y cifrado verificados con una revisión automática; pruebas de acceso cruzado en CI.
  - El borrado de un lote y de sus archivos funciona y se verifica.
  - Política de retención por defecto definida y lista de verificación de seguridad firmada.
- **Pruebas borde:** profesor que rechaza el consentimiento (no puede subir); cambio de versión del texto (se pide de nuevo); borrar un lote mientras procesa; solicitud de borrar los datos de un estudiante; examen con datos de un menor (aviso).
- **Tecnología:** Cognito, S3 con KMS, IAM de mínimo privilegio, escáner de dependencias, análisis estático de seguridad en CI.
- **Acuerdos con otras áreas:** Legal entrega el texto y la retención; Infraestructura revisa los permisos; Producto aprueba el flujo de consentimiento.

### I3 · Piloto con el profesor y medición

- **Objetivo:** comprobar con un profesor real y 40 estudiantes que el producto cumple las métricas.
- **Criterios de aprobación:**
  - El profesor crea un evaluador, sube sus exámenes, lanza el lote, revisa y descarga resultados sin ayuda del equipo (el equipo solo observa).
  - Se miden concordancia (mínimo 90%, meta 95%), tiempo del lote, costo por examen y número de ediciones del profesor.
  - Se registran sus comentarios sobre si los resultados se entienden y si la calificación se aleja de lo esperado.
  - Se pregunta la disposición a pagar y se documenta junto al supuesto de 50.000 COP.
  - Se redacta la decisión de seguir o replantear: la señal de parar es que el resultado no se entienda o que califique muy lejos de lo esperado.
- **Pruebas borde:** el profesor se atasca en un paso (se anota dónde); fotos de mala calidad tomadas con celular; el profesor no tiene tiempo de revisar todos los exámenes; un lote que falla a mitad de la prueba; el profesor discrepa de su propia calificación inicial.
- **Tecnología:** eventos de uso registrados en la aplicación, informe de métricas del arnés de E1 y de producción, entrevista corta.
- **Acuerdos con otras áreas:** Producto lidera la prueba; IA entrega el informe de métricas; Legal obtiene el consentimiento antes de empezar; Infraestructura mantiene el ambiente estable durante la prueba.

## Decisiones abiertas y supuestos por validar

| # | Decisión | Propuesta | Quién decide | Se resuelve en |
| --- | --- | --- | --- | --- |
| 1 | Región de AWS | Elegir entre costo, latencia hacia LATAM y disponibilidad del proveedor de IA | Producto e Infraestructura | A1 |
| 2 | Modelo de visión de referencia | El que mejor lea las hojas del piloto entre 2 candidatos | IA | E1 |
| 3 | Herramienta de infraestructura como código | Terraform (o AWS CDK) | Infraestructura | A1 |
| 4 | Entrada en Word (.docx) | Aceptar solo PDF e imagen en P1; Word convertido a PDF después | Producto | C1 |
| 5 | Lista de estudiantes opcional para identificar exámenes | Sí, opcional | Producto | D3 |
| 6 | Exportación mínima | CSV simple como parte de G2 si es barato; el resto sigue en P2 | Producto | H1 |
| 7 | Precisión de las anotaciones | Por página como mínimo; por zona si el modelo lo permite | IA y Front | G1 |
| 8 | Retención por defecto de exámenes | Por definir con revisión legal | Legal y Producto | I2 |
| 9 | Tolerancia en puntos para contar una nota como coincidente | Definir con el golden set | IA y Producto | E1 |
| 10 | Techo de costo por examen y tope por lote | 45 COP por examen; tope por lote por definir | Producto | E5 |
| 11 | Tiempo objetivo para 40 exámenes | 15 minutos o menos | Producto | F1 |
| 12 | Regla de puntos parciales y error arrastrado | Definir con el profesor piloto | Producto | E3 |
| 13 | Proveedor de identidad | Amazon Cognito | API e Infraestructura | B2 |

**Supuestos todavía sin validar**

- El precio de 50.000 COP mensuales por profesor es disposición a pagar real, y el negocio es rentable con ese precio.
- Un modelo de visión económico lee con suficiente calidad el manuscrito matemático de los profesores.
- Una clave de respuestas basta como fuente de criterios para la mayoría de los profesores (hoy el 60% califica con clave).
- Los profesores digitalizan sus exámenes (escáner o foto) y los suben desde un computador.
- El profesor piloto representa al usuario objetivo y su criterio es consistente de un examen a otro.
- El cálculo de 560 exámenes al mes es típico del usuario objetivo.
