import os
import json
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

# Lista de carreras válidas
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

        # Mapear a claves que espera Google Sheets
        resultado = {
            "Teléfono": telefono,
            "Nombre": datos_extraidos.get("nombre", ""),
            "Apellido": datos_extraidos.get("apellido", ""),
            "Carrera": datos_extraidos.get("carrera", ""),
            "Estado_Contacto": datos_extraidos.get("estado_contacto", ""),
            "Último mensaje": texto,
            "Timestamp": datetime.now().isoformat()
        }
        return resultado
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")
        return None


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

    # Enviar a Google Sheets
    try:
        response = requests.post(GAS_WEBHOOK_URL, json=datos)
        print(f"Enviado a Sheets. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        return jsonify({"error": "Error enviando a Google Sheets", "detalle": str(e)}), 500

    return jsonify({"status": "ok", "datos": datos})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

