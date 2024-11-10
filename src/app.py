import logging
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from src.classifier import classify_file

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/classify_file', methods=['POST', 'OPTIONS'])
@cross_origin(origins="*")  # Explicitly allow all origins for this route
def classify_file_route():
    # Log the origin of the incoming request
    origin = request.headers.get('Origin')
    logging.debug(f"Incoming request origin: {origin}")

    if request.method == 'OPTIONS':
        # Reply to the preflight (OPTIONS) request with headers
        response = jsonify({'status': 'CORS preflight successful'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    # Handle POST request
    if 'file' not in request.files:
        logging.warning("No file part in the request.")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.warning("No file selected in the request.")
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        logging.warning(f"File type not allowed for file: {file.filename}")
        return jsonify({"error": f"File type not allowed"}), 400

    file_class = classify_file(file)
    logging.info(f"File classified as: {file_class}")
    return jsonify({"file_class": file_class}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)