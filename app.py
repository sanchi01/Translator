import os
import pandas as pd
from deep_translator import GoogleTranslator
from flask import Flask, request, jsonify, send_file, render_template

# Initialize Flask app
app = Flask(__name__)

# Function to translate text to English
def translate_to_english(text):
    if not text or pd.isna(text):  # Handle empty or NaN
        return text
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        print(f"Translation error for '{text}': {e}")
        return text  # Fallback to original if translation fails

# Home page (upload form)
@app.route('/')
def index():
    return render_template('index.html')

# Handle translation
@app.route('/translate', methods=['POST'])
def translate_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        df = pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500

    if 'TobeTranslated' not in df.columns:
        return jsonify({'error': "'TobeTranslated' column not found in the Excel file"}), 400

    # Translate each row
    df['translated'] = df['TobeTranslated'].apply(translate_to_english)

    # Save output
    output_path = '/tmp/output_translated.xlsx'
    df.to_excel(output_path, index=False)

    return send_file(
        output_path,
        as_attachment=True,
        download_name='translated_file.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(debug=True)
