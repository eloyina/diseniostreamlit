import mimetypes
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Generador de prompts con archivo", page_icon="🧩", layout="centered")

MENSAJE_SIN_ARCHIVO = "AGREGA EL ARCHIVO para el formato de la sesión o documento que deseas."
EXTENSIONES_TEXTO = {".txt", ".md", ".csv", ".json", ".html", ".xml", ".py", ".js"}

# Cada campo: (clave, etiqueta, descripción, ejemplos: profesora, ventas, prompt engineering)
CAMPOS = [
    ("objetivo", "Objetivo",
     "Escribe en una o dos frases qué quieres lograr con la IA. Es lo más importante: sin objetivo, la IA adivina.",
     ("Crear una sesión de aprendizaje de 45 minutos sobre las vocales para 1.er grado, en formato UGEL.",
      "Escribir 5 mensajes de WhatsApp para recuperar clientes que no compran hace 2 meses.",
      "Mejorar mi prompt para que la IA me dé respuestas más precisas y sin relleno.")),
    ("role", "Role",
     "Indica qué papel debe asumir la IA: un experto, un profesor, un revisor, un redactor, etc.",
     ("Actúa como docente de primaria con experiencia en el Currículo Nacional y en sesiones UGEL.",
      "Actúa como especialista en ventas y atención al cliente para pequeños negocios.",
      "Actúa como experto en prompt engineering que revisa y corrige prompts.")),
    ("context", "Context",
     "Explica la situación: para quién es, por qué lo necesitas, qué está pasando y cualquier dato de fondo.",
     ("Tengo un aula de 25 niños de 6 años, varios con dificultades de atención; la sesión es para la próxima semana.",
      "Vendo ropa por Instagram y WhatsApp; mis clientas son mujeres de 25 a 40 años.",
      "Uso la IA en mi trabajo y mis prompts dan respuestas genéricas; quiero entender por qué.")),
    ("input", "Input",
     "Di qué parte del archivo o qué información debe analizar la IA y en qué fijarse.",
     ("Usa el archivo como modelo de formato: respeta sus secciones (competencia, capacidad, desempeño y momentos).",
      "Toma del archivo la lista de productos y precios; ignora los datos de proveedores.",
      "Analiza el prompt que está en el archivo y señala qué partes son ambiguas.")),
    ("constraint", "Constraint",
     "Pon los límites y reglas: qué NO debe hacer, extensión máxima, idioma, datos que no debe inventar.",
     ("Lenguaje sencillo para niños, actividades de máximo 15 minutos y sin materiales costosos.",
      "Mensajes de máximo 3 líneas y sin prometer descuentos mayores al 10 %.",
      "No cambies la intención original del prompt ni agregues información que yo no di.")),
    ("output", "Output (formato de salida)",
     "Describe cómo quieres recibir la respuesta: lista, tabla, párrafos, documento con títulos, plantilla, etc.",
     ("Tabla con Inicio, Desarrollo y Cierre, con tiempos y materiales, y una lista de cotejo al final.",
      "Lista numerada de 5 mensajes listos para copiar, con un emoji cada uno.",
      "El prompt corregido en un bloque para copiar y, debajo, la lista de cambios que hiciste.")),
    ("quality", "Quality",
     "Indica el nivel de detalle y precisión que esperas: breve o detallado, formal o sencillo, con o sin citas.",
     ("Detallada y alineada a las competencias del área, para que otra docente pueda aplicarla sin preguntar.",
      "Claros, persuasivos y naturales, como si los escribiera la dueña del negocio.",
      "Preciso y explicado paso a paso, para que aprenda a hacerlo por mi cuenta.")),
    ("validation", "Validation",
     "Explica cómo vas a comprobar que la respuesta está bien: qué debe incluir sí o sí, o qué debe revisar la IA antes de entregar.",
     ("Verifica que cada momento tenga tiempo, actividad y material, y que el propósito coincida con la competencia.",
      "Revisa que cada mensaje tenga saludo, producto, beneficio y una invitación a comprar.",
      "Comprueba que el prompt final tenga rol, contexto, tarea, formato y restricciones.")),
    ("tono", "Tono",
     "Elige cómo debe sonar la respuesta: formal, cercano, motivador, técnico, neutro, etc.",
     ("Cálido y motivador, pensado para niños.",
      "Cercano y amable, tuteando a la clienta.",
      "Técnico pero fácil de entender.")),
    ("extra", "Instrucciones extra",
     "Agrega cualquier otra indicación que no encaje arriba: ejemplos, palabras a usar o evitar, pasos especiales.",
     ("Incluye una adaptación para estudiantes con necesidades educativas especiales.",
      "Sugiere también el mejor horario para enviar los mensajes.",
      "Dame dos versiones del prompt: una corta y una detallada.")),
]

OBLIGATORIOS = {"objetivo": "Objetivo", "output": "Formato de salida"}

AVISOS_VACIOS = {
    "context": "El contexto está vacío; la respuesta puede quedar más genérica.",
    "input": "No se describió qué debe analizarse del archivo.",
    "constraint": "No se agregaron restricciones; la IA podría responder con demasiada libertad.",
    "validation": "No se indicó validación; será más difícil comprobar si la salida cumple.",
}

PASOS_POR_DEFECTO = {
    "role": "define el rol más útil para el caso.",
    "context": "explica el contexto, la situación o el problema.",
    "input": "indica qué información del archivo o del caso debe tomar como base.",
    "constraint": "marca límites, reglas, tono o condiciones que debe respetar.",
    "output": "define el formato final de salida que se necesita.",
    "quality": "señala el nivel de detalle, claridad o precisión esperado.",
    "validation": "explica cómo verificar que la respuesta cumple el objetivo.",
}


def construir_prompt(datos, archivo_info):
    partes = []
    if datos["role"]:
        partes.append(f"Actúa como: {datos['role']}.")
    else:
        partes.append("Eres un asistente experto en prompt engineering. Ayuda a la persona a crear un "
                      "prompt claro, útil y bien estructurado para que la IA resuelva mejor su objetivo.")

    if datos["objetivo"]:
        partes.append(f"Objetivo: {datos['objetivo']}")

    if archivo_info:
        partes.append(f"Usa el archivo adjunto como referencia principal. Archivo adjunto: {archivo_info['nombre']} "
                      f"Formato: {archivo_info['extension']} Tipo MIME: {archivo_info['mime']}.")
    else:
        partes.append(MENSAJE_SIN_ARCHIVO)

    partes.append("Sigue estos pasos para construir la respuesta:")
    for clave, etiqueta, *_ in CAMPOS:
        if clave in PASOS_POR_DEFECTO:
            nombre = etiqueta.split(" (")[0]
            valor = datos[clave] or PASOS_POR_DEFECTO[clave]
            partes.append(f"{nombre}: {valor}")

    if datos["tono"]:
        partes.append(f"Tono: {datos['tono']}")
    if datos["extra"]:
        partes.append(f"Instrucciones extra: {datos['extra']}")
    if archivo_info and archivo_info.get("texto"):
        partes.append(f"Contenido del archivo (extracto):\n{archivo_info['texto']}")

    partes.append("Devuelve una propuesta final que sea fácil de copiar, con lenguaje claro y pensada "
                  "para ayudar a la persona a lograr su objetivo.")
    return " ".join(partes)


# ---------------- Interfaz ----------------
st.title("Generador de prompts con archivo")
st.write("Sube un archivo y completa los pasos para crear un prompt más claro, útil y fácil de usar con IA.")
st.caption(f'Si no adjuntas nada, el prompt incluirá el mensaje: "{MENSAJE_SIN_ARCHIVO}"')
st.caption("En cada paso verás ejemplos para 👩‍🏫 profesoras, 🛍️ negocios de ventas y 🧠 prompt engineering.")

st.subheader("Archivo de referencia")
archivo = st.file_uploader(
    "Sube el documento que la IA debe tomar como base (opcional)",
    help="Puede ser una sesión, un informe, una lista de productos, un prompt anterior, etc.",
)

notas = []
archivo_info = None
if archivo is not None:
    extension = Path(archivo.name).suffix.lower()
    mime = archivo.type or mimetypes.guess_type(archivo.name)[0] or "desconocido"
    archivo_info = {"nombre": archivo.name, "extension": extension, "mime": mime}
    st.success(f"Archivo detectado: {archivo.name} · Formato: {extension}")
    if extension in EXTENSIONES_TEXTO:
        try:
            archivo_info["texto"] = archivo.getvalue().decode("utf-8", errors="ignore")[:4000]
        except Exception:
            pass
    else:
        notas.append("El archivo subido no parece de texto; se usará el nombre del archivo como referencia.")

datos = {}
for clave, etiqueta, descripcion, (ej_profe, ej_ventas, ej_prompt) in CAMPOS:
    st.markdown(f"**{etiqueta}**")
    st.caption(
        f"{descripcion}  \n"
        f"👩‍🏫 **Profesora:** {ej_profe}  \n"
        f"🛍️ **Negocio de ventas:** {ej_ventas}  \n"
        f"🧠 **Prompt engineering:** {ej_prompt}"
    )
    datos[clave] = st.text_area(
        etiqueta,
        placeholder="Escribe aquí…",
        help=descripcion,
        key=clave,
        label_visibility="collapsed",
        height=90,
    ).strip()

# Especificación
st.subheader("Especificación")
especificacion = {**datos, "archivo": archivo_info["nombre"] if archivo_info else None}
st.json(especificacion, expanded=False)

# Validación
st.subheader("Validación")
faltan = [nombre for clave, nombre in OBLIGATORIOS.items() if not datos[clave]]
if faltan:
    st.error("Faltan campos: " + ", ".join(faltan))
avisos = [texto for clave, texto in AVISOS_VACIOS.items() if not datos[clave]]
for aviso in avisos:
    st.warning(aviso)
if not faltan and not avisos:
    st.success("Todo completo. Tu prompt está listo.")

# Prompt generado
st.subheader("Prompt generado")
st.code(construir_prompt(datos, archivo_info), language=None, wrap_lines=True)

# Notas
if notas:
    st.subheader("Notas")
    for nota in notas:
        st.markdown(f"- {nota}")
