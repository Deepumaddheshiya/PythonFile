"""
Steganography API Service
Flask REST API for secure message encoding/decoding
Runs on port 5001 (separate from Node.js on 5010)
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import base64
import io
import threading
import time
from dotenv import load_dotenv

from utils.stego import (
    allowed_file,
    encode_message,
    decode_message,
    calculate_capacity,
    encode_image_in_image,
    decode_image_from_image
)
from utils.audio import encode_audio, decode_audio
from utils.analysis import analyze_image

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for Node.js communication

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
ALLOWED_AUDIO_EXTENSIONS = {'wav'}

# Auto-cleanup settings (delete files older than 5 minutes)
CLEANUP_INTERVAL = 300  # 5 minutes

def cleanup_old_files():
    """Background task to delete old uploaded files"""
    while True:
        time.sleep(CLEANUP_INTERVAL)
        try:
            folder = app.config['UPLOAD_FOLDER']
            if os.path.exists(folder):
                now = time.time()
                for filename in os.listdir(folder):
                    filepath = os.path.join(folder, filename)
                    if os.path.isfile(filepath):
                        if now - os.path.getmtime(filepath) > CLEANUP_INTERVAL:
                            os.remove(filepath)
                            print(f"🗑️ Cleaned up: {filename}")
        except Exception as e:
            print(f"Cleanup error: {e}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()

def generate_unique_filename(extension):
    """Generate a unique filename to prevent collisions"""
    return f"{uuid.uuid4().hex}.{extension}"

def file_to_base64(filepath):
    """Convert file to base64 string"""
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def cleanup_files(*filepaths):
    """Delete temporary files"""
    for filepath in filepaths:
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Failed to delete {filepath}: {e}")

# ==================== ROOT & HEALTH CHECK ====================

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "running", "service": "Secure-App Stego Service"})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "stego-service",
        "version": "1.0.0"
    })

# ==================== TEXT → IMAGE STEGANOGRAPHY ====================

@app.route('/api/encode/text-image', methods=['POST'])
def encode_text_in_image():
    try:
        if 'image' not in request.files or 'message' not in request.form:
             return jsonify({"success": False, "error": "Missing image or message"}), 400

        image = request.files['image']
        message = request.form['message']
        password = request.form.get('password')

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))

        image.save(input_path)
        encode_message(input_path, message, output_path, password)

        # Return base64 encoded image
        encoded_string = file_to_base64(output_path)
        
        cleanup_files(input_path, output_path)
            
        return jsonify({
            "success": True,
            "encodedImage": f"data:image/png;base64,{encoded_string}"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/decode/text-image', methods=['POST'])
def decode_text_from_image():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "Missing image"}), 400

        image = request.files['image']
        password = request.form.get('password')

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        image.save(input_path)

        message = decode_message(input_path, password)
        
        cleanup_files(input_path)

        return jsonify({
            "success": True,
            "text": message
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== IMAGE → IMAGE STEGANOGRAPHY ====================

@app.route('/api/encode/image-image', methods=['POST'])
def encode_image_in_image_api():
    try:
        if 'cover_image' not in request.files or 'secret_image' not in request.files:
            return jsonify({"success": False, "error": "Missing images"}), 400

        cover = request.files['cover_image']
        secret = request.files['secret_image']
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        cover_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        secret_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        
        cover.save(cover_path)
        secret.save(secret_path)
        
        encode_image_in_image(cover_path, secret_path, output_path)
        
        encoded_string = file_to_base64(output_path)
        
        cleanup_files(cover_path, secret_path, output_path)
        
        return jsonify({
            "success": True,
            "encodedImage": f"data:image/png;base64,{encoded_string}"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/decode/image-image', methods=['POST'])
def decode_image_from_image_api():
    try:
        if 'image' not in request.files:
             return jsonify({"success": False, "error": "Missing image"}), 400
             
        image = request.files['image']
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        
        image.save(input_path)
        
        decode_image_from_image(input_path, output_path)
        
        encoded_string = file_to_base64(output_path)
             
        cleanup_files(input_path, output_path)

        return jsonify({
            "success": True,
            "secretImage": f"data:image/png;base64,{encoded_string}"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== AUDIO STEGANOGRAPHY ====================

@app.route('/api/encode/audio', methods=['POST'])
def encode_audio_api():
    try:
        if 'audio' not in request.files or 'message' not in request.form:
             return jsonify({"success": False, "error": "Missing audio or message"}), 400
             
        audio = request.files['audio']
        message = request.form['message']
        password = request.form.get('password')
        
        if not audio.filename.lower().endswith('.wav'):
             return jsonify({"success": False, "error": "Only WAV supported"}), 400
             
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('wav'))
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('wav'))
        
        audio.save(input_path)
        encode_audio(input_path, message, output_path, password)
        
        encoded_string = file_to_base64(output_path)

        cleanup_files(input_path, output_path)
        
        return jsonify({
            "success": True,
            "encodedAudio": f"data:audio/wav;base64,{encoded_string}"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/decode/audio', methods=['POST'])
def decode_audio_api():
    try:
        if 'audio' not in request.files:
             return jsonify({"success": False, "error": "Missing audio"}), 400
             
        audio = request.files['audio']
        password = request.form.get('password')
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('wav'))
        audio.save(input_path)
        
        message = decode_audio(input_path, password)
        
        cleanup_files(input_path)
             
        return jsonify({
            "success": True,
            "text": message
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CAPACITY CHECK ====================

@app.route('/api/capacity', methods=['POST'])
def check_capacity_api():
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "error": "Missing image"}), 400
            
        image = request.files['image']
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], generate_unique_filename('png'))
        image.save(input_path)
        
        capacity = calculate_capacity(input_path)
        
        cleanup_files(input_path)
             
        return jsonify({
            "success": True,
            "capacity": capacity
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    print("🔐 Steganography API Service Starting...")
    app.run(host='127.0.0.1', port=5001, debug=True)
