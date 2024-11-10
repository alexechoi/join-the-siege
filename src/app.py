import logging
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.classifier import classify_file

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["10 per minute"])

# File upload configurations
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'txt'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Limit file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Limit file size
@app.before_request
def limit_file_size():
    if request.content_length > MAX_FILE_SIZE:
        return jsonify({"error": "File too large"}), 413

@app.route('/classify_file', methods=['POST', 'OPTIONS'])
@cross_origin(origins="*")  # Explicitly allow all origins for this route
@limiter.limit("10 per minute")  # Apply rate limiting
def classify_file_route():
    # Log the origin of the incoming request
    origin = request.headers.get('Origin')
    logging.debug(f"Incoming request origin: {origin}")

    if request.method == 'OPTIONS':
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

    # Classify file
    file_class = classify_file(file)
    logging.info(f"File classified as: {file_class}")

    return jsonify({"file_class": file_class}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)