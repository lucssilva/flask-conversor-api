from flask import Flask, make_response, request, jsonify
from functools import wraps
import base64
import pandas as pd

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
            if 'file' not in request.files:
                return make_response(jsonify({"error": "No file provided"}), 400)
            
            file = request.files['file']
            if file.filename == '':
                return make_response(jsonify({"error": "No file selected"}), 400)
            
            if not file.filename.endswith(allowed_extension):
                return make_response(
                    jsonify({"error": f"File must be a {allowed_extension.upper()}"}),
                    400
                )
            
            return f(file, *args, **kwargs)
        return wrapper
    return decorator

@app.route('/convert/csv', methods=['POST'])
@validate_file('.csv')
def convert_csv(file):
    try:
        raw = pd.read_csv(file).to_dict(orient='records')        
        return str(raw).replace("'", '\\"')
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/convert/pdf', methods=['POST'])
@validate_file('.pdf')
def convert_pdf(file):
    try:
        raw = base64.b64encode(file.read()).decode('utf-8')
        return f"data:application/pdf;base64,{raw}"
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
