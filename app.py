from conversion import convert_csv_to_str, convert_pdf_to_base64, logger
from flask import Flask, make_response, request, jsonify
from functools import wraps
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "message": "Service is running",
        "version": "0.0.1",
    })

def validate_file(allowed_extension):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            logger.info(f"Validating file with allowed extension: {allowed_extension}")
            
            if 'data' not in request.files:
                logger.error("No file provided in request")
                return make_response(jsonify({"error": "No file provided"}), 400)
            
            file = request.files['data']
            if file.filename == '':
                logger.error("Empty filename provided")
                return make_response(jsonify({"error": "No file selected"}), 400)
            
            if not file.filename.endswith(allowed_extension):
                logger.error(f"Invalid file extension: {file.filename}. Expected: {allowed_extension}")
                return make_response(
                    jsonify({"error": f"File must be a {allowed_extension.upper()}"}),
                    400
                )
            logger.info(f"File validation successful for: {file.filename}")
            return f(file, *args, **kwargs)
        return wrapper
    return decorator

@app.route('/convert/csv', methods=['POST'])
@validate_file('.csv')
def convert_csv_route(file):
    try:
        logger.info(f"Starting CSV conversion for file: {file.filename}")
        return convert_csv_to_str(file)
    except Exception as e:
        logger.error(f"Error converting CSV file: {str(e)}")
        logger.error(f"Stack trace: ", exc_info=True)
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/convert/pdf', methods=['POST'])
@validate_file('.pdf')
def convert_pdf_route(file):
    try:
        logger.info(f"Starting PDF conversion for file: {file.filename}")
        raw = convert_pdf_to_base64(file)
        logger.info(f"Successfully converted PDF data")
        return f"data:application/pdf;base64,{raw}"
    except Exception as e:
        logger.error(f"Error converting PDF file: {str(e)}")
        logger.error(f"Stack trace: ", exc_info=True)
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/session', methods=['GET'])
def has_session():
    token = request.headers.get('token')
    if not token:
        return make_response(jsonify({"error": "Token is required"}), 401)
    
    try:
        logger.info(f"Checking session with token: {token}")
        response = requests.get('https://developers.botcity.dev/api/v2/audit', 
                              params={'size': 1},
                              headers={'token': token})
        response.raise_for_status()
        logger.info(f"Successfully checked session")
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking session: {str(e)}")
        logger.error(f"Stack trace: ", exc_info=True)
        return make_response(jsonify({"error": str(e)}), response.status_code if hasattr(response, 'status_code') else 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
