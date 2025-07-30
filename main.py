from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json

app = Flask(__name__)
CORS(app) 

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print("¡Éxito! Modelo de Gemini configurado correctamente.")
except Exception as e:
    print(f"ALERTA: Error configurando Gemini: {e}")
    model = None

@app.route('/generate-ideas', methods=['POST'])
def generate_ideas_route():
    # ... (Esta función ya funciona, la dejamos como está) ...
    if not model: return jsonify({"error": "El modelo de IA no está funcionando."}), 500
    data = request.json
    topic = data.get('topic')
    formato = data.get('format')
    if not topic: return jsonify({"error": "No se recibió ningún tema."}), 400
    prompt_ideas = f"""Actúa como un experto creador de contenido viral. Para un video en formato {formato} sobre el tema '{topic}', genera lo siguiente en un formato JSON claro y conciso: 1. Tres (3) sugerencias de títulos virales. 2. Tres (3) ideas creativas para la miniatura, descritas visualmente. Por favor, devuelve ÚNICAMENTE el objeto JSON, con las claves "titulos" y "miniaturas"."""
    try:
        response = model.generate_content(prompt_ideas)
        json_text = response.text
        start_index = json_text.find('{')
        end_index = json_text.rfind('}') + 1
        if start_index != -1 and end_index != 0:
            clean_json_text = json_text[start_index:end_index]
            json_response = json.loads(clean_json_text)
            return jsonify(json_response)
        else: raise ValueError("La respuesta de la IA (ideas) no contenía un JSON válido.")
    except Exception as e:
        print(f"Error generando ideas: {e}")
        return jsonify({"error": "Error al generar ideas."}), 500

@app.route('/generate-final-script', methods=['POST'])
def generate_final_script_route():
    if not model: return jsonify({"error": "El modelo de IA no está funcionando."}), 500
    data = request.json
    topic = data.get('topic')
    formato = data.get('format')
    if not topic: return jsonify({"error": "No se recibió ningún tema."}), 400
    prompt_guion = f"""
    Actúa como un guionista experto de videos cortos.
    Para un video en formato {formato} sobre el tema '{topic}', escribe un guion detallado.
    Incluye indicaciones de escenas, tiempos y sugerencias visuales.

    Por favor, devuelve el guion como un objeto JSON con una única clave "guion".
    El valor de la clave "guion" debe ser UN ÚNICO STRING DE TEXTO.
    Usa el carácter especial '\\n' para representar los saltos de línea dentro del string del guion.
    NO incluyas saltos de línea literales dentro del string.

    EJEMPLO DE FORMATO DE SALIDA PERFECTO:
    {{
      "guion": "ESCENA 1 (0:00-0:05): Intro animada con música upbeat.\\n\\nESCENA 2 (0:05-0:15): Presentación de la presentadora en la playa."
    }}
    """
    try:
        response = model.generate_content(prompt_guion)
        json_text = response.text
        start_index = json_text.find('{')
        end_index = json_text.rfind('}') + 1
        if start_index != -1 and end_index != 0:
            clean_json_text = json_text[start_index:end_index]
            json_response = json.loads(clean_json_text)
            return jsonify(json_response)
        else: raise ValueError("La respuesta de la IA (guion) no contenía un JSON válido.")
    except Exception as e:
        # --- ¡ESTA ES LA PARTE NUEVA Y MEJORADA! ---
        print(f"Error generando el guion final: {e}")
        # Le pedimos que nos muestre el texto exacto que intentó procesar
        if 'clean_json_text' in locals():
            print("--- TEXTO JSON QUE CAUSÓ EL FALLO ---")
            print(clean_json_text)
            print("------------------------------------")
        return jsonify({"error": "Error al generar el guion final."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)