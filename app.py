import json
import mimetypes
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Generador de prompts con archivo", page_icon="🧩", layout="centered")

MENSAJE_SIN_ARCHIVO = "AGREGA EL ARCHIVO para el formato de la sesión o documento que deseas."
EXTENSIONES_TEXTO = {".txt", ".md", ".csv", ".json", ".html", ".xml", ".py", ".js"}

# Cada campo: (clave, etiqueta, descripción de lo que debe poner, ejemplo)
CAMPOS = [
    ("objetivo", "Objetivo",
     "Escribe en una o dos frases qué quieres lograr con la IA. Es lo más importante: sin objetivo, la IA adivina.",
     "Ej.: Quiero un resumen de las evidencias del documento para presentarlo en la ratificación."),
    ("role", "Role",
     "Indica qué papel debe asumir la IA: un experto, un profesor, un revisor, un redactor, etc.",
     "Ej.: Actúa como abogado especialista en trámites administrativos."),
    ("context", "Context",
     "Explica la situación: para quién es, por qué lo necesitas, qué está pasando y cualquier dato de fondo.",
     "Ej.: Es para una audiencia el lunes; el documento reúne evidencias de un proceso de ratificación."),
    ("input", "Input",
     "Di qué parte del archivo o qué información debe analizar la IA y en qué fijarse.",
     "Ej.: Usa solo las secciones de evidencias y fechas; ignora los anexos."),
    ("constraint", "Constraint",
     "Pon los límites y reglas: qué NO debe hacer, extensión máxima, idioma, datos que no debe inventar.",
     "Ej.: Máximo una página. No inventes datos que no estén en el archivo. En español."),
    ("output", "Output (formato de salida)",
     "Describe cómo quieres recibir la respuesta: lista, tabla, párrafos, documento con títulos, plantilla, etc.",
     "Ej.: Una tabla con columnas Evidencia | Fecha | Descripción, y al final un párrafo de conclusión."),
    ("quality", "Quality",
     "Indica el nivel de detalle y precisión que esperas: breve o detallado, formal o sencillo, con o sin citas.",
     "Ej.: Detallado y preciso, citando la página o sección de donde sale cada dato."),
    ("validation", "Validation",
     "Explica cómo vas a comprobar que la respuesta está bien: qué debe incluir sí o sí, o qué debe revisar la IA antes de entregar.",
     "Ej.: Verifica que todas las evidencias del documento aparezcan en la tabla y que las fechas coincidan."),
    ("tono", "Tono",
     "Elige cómo debe sonar la respuesta: formal, cercano, motivador, técnico, neutro, etc.",
     "Ej.: Formal y claro, sin tecnicismos innecesarios."),
    ("extra", "Instrucciones extra",
     "Agrega cualquier otra indicación que no encaje arriba: ejemplos, palabras a usar o evitar, pasos especiales.",
     "Ej.: Si algo no está claro en el archivo, márcalo como 'por confirmar' en vez de suponer."),
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

st.subheader("Archivo de referencia")
archivo = st.file_uploader(
    "Sube el documento que la IA debe tomar como base (opcional)",
    help="Puede ser una sesión, un informe, una plantilla, etc. La IA lo usará como modelo o fuente de información.",
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
for clave, etiqueta, descripcion, ejemplo in CAMPOS:
    st.markdown(f"**{etiqueta}**")
    st.caption(descripcion)
    datos[clave] = st.text_area(
        etiqueta,
        placeholder=ejemplo,
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
