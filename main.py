import os
import json
from flask import Flask, request, jsonify
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)

# Cargar API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializar cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

CARRERAS_DISPONIBLES = [
    "Ingeniería en Informática", "Abogacía", "Economía", "Marketing",
    "Administración de Empresas", "Ciencias Políticas", "Finanzas",
    "Relaciones Internacionales", "Contador Público", "Ingeniería en Inteligencia Artificial",
    "Economía Empresarial", "Analítica de Negocios", "Negocios Digitales", "Actuario",
    "Artes Liberales y Ciencias (BA)"
]

ARCHIVO_DATOS = "data.json"

def extraer_datos(texto, telefono):
    prompt = f"""Extraé del siguiente mensaje los datos de la persona (si están): nombre, apellido, carrera de interés y si ya fue contactado o no. Elegí la carrera solo de esta lista: {", ".join(CARRERAS_DISPONIBLES)}. Respondé en formato JSON con las claves: nombre, apellido, carrera, estado_contacto.

Mensaje:
'{texto}'"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sos un asistente que extrae datos para carga de formularios."},
                {"role": "user", "content": prompt}
            ]
        )
        contenido = response.choices[0].message.content
        datos_extraidos = json.loads(contenido)

        resultado = {
            "telefono": telefono,
            "nombre": datos_extraidos.get("nombre", ""),
            "apellido": datos_extraidos.get("apellido", ""),
            "carrera": datos_extraidos.get("carrera", ""),
            "estado_contacto": datos_extraidos.get("estado_contacto", ""),
            "ultimo_mensaje": texto,
            "timestamp": datetime.now().isoformat()
        }
        return resultado
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")
        return None


def guardar_datos_locales(nuevos_datos):
    try:
        # Si ya existe, cargarlos
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                datos_existentes = json.load(f)
        else:
            datos_existentes = []

        datos_existentes.append(nuevos_datos)

        # Guardar todo nuevamente
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos_existentes, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando archivo local: {e}")

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')


@app.route("/procesar-mensaje", methods=["POST"])
def procesar_mensaje():
    data = request.get_json()
    mensaje = data.get("mensaje")
    telefono = data.get("telefono")

    if not mensaje or not telefono:
        return jsonify({"error": "Faltan datos"}), 400

    datos = extraer_datos(mensaje, telefono)
    if not datos:
        return jsonify({"error": "No se pudieron extraer datos"}), 500

    guardar_datos_locales(datos)

    return jsonify({"status": "ok", "datos": datos})


@app.route("/descargar-json", methods=["GET"])
def descargar_json():
    if not os.path.exists(ARCHIVO_DATOS):
        return jsonify({"error": "No hay datos para descargar"}), 404

    with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
        datos = json.load(f)

    return jsonify(datos)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

