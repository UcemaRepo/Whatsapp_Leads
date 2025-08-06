import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)

# Cargar variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GAS_WEBHOOK_URL = os.getenv("GAS_WEBHOOK_URL")  # Google Apps Script Web App URL

# Inicializar cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Lista de carreras válidas para matchear
CARRERAS_DISPONIBLES = [
    "Ingeniería en Informática", "Abogacía", "Economía", "Marketing",
    "Administración de Empresas", "Ciencias Políticas", "Finanzas",
    "Relaciones Internacionales", "Contador Público", "Ingeniería en Inteligencia Artificial",
    "Economía Empresarial", "Analítica de Negocios", "Negocios Digitales", "Actuario",
    "Artes Liberales y Ciencias (BA)"
]

def extraer_datos(texto, telefono):
    prompt = f"""Extraé del siguiente mensaje los datos de la persona (si están): nombre, apellido, carrera de interés y si ya fue contactado o no. Elegí la carrera solo de esta lista: {", ".join(CARRERAS_DISPONIBLES)}. Respondé en formato JSON con las claves: nombre, apellido, carrera, estado_contacto.

Mensaje:
"{texto}""""

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    try:
        contenido = completion.choices[0].message.content
        datos = eval(contenido)  # usar json.loads si el modelo devuelve JSON real
    except Exception as e:
        datos = {}

    datos["telefono"] = telefono
    datos["ultimo_mensaje"] = texto
    datos["timestamp"] = datetime.now().isoformat()
    return datos

@app.route("/procesar-mensaje", methods=["POST"])
def procesar_mensaje():
    data = request.get_json()
    mensaje = data.get("mensaje")
    telefono = data.get("telefono")

    if not mensaje or not telefono:
        return jsonify({"error": "Faltan datos"}), 400

    datos = extraer_datos(mensaje, telefono)

    # Enviar a Google Sheets
    try:
        requests.post(GAS_WEBHOOK_URL, json=datos)
    except Exception as e:
        return jsonify({"error": "Error enviando a Google Sheets", "detalle": str(e)}), 500

    return jsonify({"status": "ok", "datos": datos})