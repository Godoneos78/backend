from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configura tu clave de API de OpenAI
openai.api_key = "tu_api_key_aqui"


# Función para guardar el prediagnóstico en la base de datos
def guardar_prediagnostico(nombre, edad, diagnostico):
    conn = sqlite3.connect("prediagnosticos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO prediagnosticos (nombre, edad, diagnostico) VALUES (?, ?, ?)", (nombre, int(edad), diagnostico))
    conn.commit()
    conn.close()

# Endpoint para analizar la imagen y generar un prediagnóstico
@app.route('/prediagnostico', methods=['POST'])
def analizar_imagen():
    nombre = request.form.get('nombre')
    edad = request.form.get('edad')
    imagen = request.files.get('imagen')

    if not nombre or not edad or not imagen:
        return jsonify({"error": "Falta el nombre, la edad o la imagen"}), 400

    # Prompt para obtener un diagnóstico simulado
    prompt = (
        "Imagina que estás observando una imagen de una boca humana, donde puedes ver dientes y encías. "
        "Describe cualquier posible problema dental que puedas inferir en cuanto a caries, inflamación de encías, "
        "estado de los dientes, enrojecimiento o infecciones visibles. Proporciona un prediagnóstico con 3 ejemplos de posibles problemas dentales, "
        "sin introducciones , solo el diagnóstico directo, pero al final sugerir la parte de consulte con un dentista para un diagnóstico preciso."

    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente que proporciona observaciones simuladas basadas en la descripción dental proporcionada."},
                {"role": "user", "content": prompt}
            ]
        )

        # Obtén el resultado del diagnóstico
        diagnostico = response.choices[0].message['content'].strip()

        # Guarda el prediagnóstico en la base de datos
        guardar_prediagnostico(nombre, edad, diagnostico)

        return jsonify({"diagnostico": diagnostico}), 200

    except Exception as e:
        print("Error en OpenAI:", str(e))
        return jsonify({"error": "Error al procesar el diagnóstico"}), 500

# Endpoint para listar todos los prediagnósticos realizados
@app.route('/listar', methods=['GET'])
def listar_prediagnosticos():
    conn = sqlite3.connect("prediagnosticos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, edad FROM prediagnosticos")
    rows = cursor.fetchall()
    conn.close()

    prediagnosticos = [{"id": row[0], "nombre": row[1], "edad": row[2]} for row in rows]
    return jsonify(prediagnosticos), 200

# Endpoint para ver el detalle de un prediagnóstico específico
@app.route('/detalle/<int:id>', methods=['GET'])
def detalle_prediagnostico(id):
    conn = sqlite3.connect("prediagnosticos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, edad, diagnostico FROM prediagnosticos WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        detalle = {
            "nombre": row[0],
            "edad": row[1],
            "diagnostico": row[2]
        }
        return jsonify(detalle), 200
    else:
        return jsonify({"error": "No se encontró el prediagnóstico"}), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
