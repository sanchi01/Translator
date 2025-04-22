import os
import pandas as pd
from googletrans import Translator
from flask import Flask, request, jsonify, send_file, render_template

# Initialize Flask app and translator
app = Flask(__name__)
translator = Translator()

# Function to detect language and translate text to English
def translate_to_english(text):
    if not text:  # Handle empty cells
        return text
    detected_language = translator.detect(text).lang
    if detected_language != 'en':
        translated = translator.translate(text, src=detected_language, dest='en')
        return translated.text
    return text  # Return original if it's already in English

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate_excel():
    # Check if the user uploaded a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Read the uploaded Excel file
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500

    # Check if the required column 'TobeTranslated' exists
    if 'TobeTranslated' not in df.columns:
        return jsonify({'error': "'TobeTranslated' column not found in the Excel file"}), 400

    # Translate the text and create a new column
    df['translated'] = df['TobeTranslated'].apply(translate_to_english)

    # Save the output to a new Excel file
    output_filename = '/tmp/output_translated.xlsx'
    df.to_excel(output_filename, index=False)

    # Send the file back as a response
    return send_file(output_filename, as_attachment=True, download_name='translated_file.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == '__main__':
    app.run(debug=True)
