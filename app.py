from flask import Flask, render_template, request, send_file, jsonify
import os
from dotenv import load_dotenv

# ===== Optional AI (Gemini) =====
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from utils.stego import (
    allowed_file,
    encode_message,
    decode_message,
    calculate_capacity,
    encode_image_in_image,
    decode_image_from_image
)

from utils.analysis import analyze_image
from utils.audio import encode_audio, decode_audio

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# ===== Gemini Configuration (Safe) =====
if GEMINI_AVAILABLE:
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    except Exception:
        GEMINI_AVAILABLE = False

# ================= ROUTES =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode')
def encode_page():
    return render_template('encode.html')

@app.route('/decode')
def decode_page():
    return render_template('decode.html')

@app.route('/capacity')
def capacity_page():
    return render_template('capacity.html')

# ========== TEXT STEGANOGRAPHY ==========

@app.route('/encode_message', methods=['POST'])
def encode():
    if 'image' not in request.files or 'message' not in request.form:
        return "Invalid request", 400

    image = request.files['image']
    if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
        return "Invalid file type", 400

    message = request.form['message']
    password = request.form.get('password')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    output_name = f"encoded_{os.path.splitext(image.filename)[0]}.png"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_name)

    image.save(input_path)
    encode_message(input_path, message, output_path, password)

    return send_file(output_path, as_attachment=True, download_name=output_name)

@app.route('/decode_message', methods=['POST'])
def decode():
    if 'image' not in request.files:
        return "Invalid request", 400

    image = request.files['image']
    password = request.form.get('password')

    if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
        return "Invalid file type", 400

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    message = decode_message(image_path, password)
    return render_template('decode_result.html', message=message)

@app.route('/calculate_capacity', methods=['POST'])
def calculate():
    if 'image' not in request.files:
        return "Invalid request", 400

    image = request.files['image']
    if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
        return "Invalid file type", 400

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(path)

    capacity = calculate_capacity(path)
    return render_template('capacity_result.html', capacity=capacity)

# ========== AI MESSAGE (OPTIONAL) ==========

@app.route('/generate_ai_message', methods=['POST'])
def generate_ai_message():
    if not GEMINI_AVAILABLE:
        return jsonify({
            "message": "AI feature unavailable. Please write your own message."
        }), 503

    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()

        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = (
            f"Write a short secret message about: {user_prompt}"
            if user_prompt
            else "Write a short mysterious secret message under 200 characters."
        )

        response = model.generate_content(prompt)

        return jsonify({
            "message": response.text.strip()
        })

    except Exception as e:
        print("Gemini Error:", e)
        return jsonify({
            "message": "AI limit exceeded or key issue. Try again later."
        }), 500

# ========== IMAGE ANALYSIS ==========

@app.route('/analyze')
def analyze_page():
    return render_template('analyze.html')

@app.route('/analyze_image', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return "Invalid request", 400

    image = request.files['image']
    if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
        return "Invalid file type", 400

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis_' + image.filename)

    image.save(img_path)
    analyze_image(img_path, output_path)

    return render_template(
        'analyze_result.html',
        original_image=f'uploads/{image.filename}',
        analysis_image=f'uploads/analysis_{image.filename}'
    )

# ========== IMAGE IN IMAGE ==========

@app.route('/encode_image')
def encode_image_page():
    return render_template('encode_image.html')

@app.route('/decode_image')
def decode_image_page():
    return render_template('decode_image.html')

@app.route('/encode_image_action', methods=['POST'])
def encode_image_action():
    if 'cover_image' not in request.files or 'secret_image' not in request.files:
        return "Invalid request", 400

    cover = request.files['cover_image']
    secret = request.files['secret_image']

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover.filename)
    secret_path = os.path.join(app.config['UPLOAD_FOLDER'], secret.filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'img_hidden.png')

    cover.save(cover_path)
    secret.save(secret_path)

    encode_image_in_image(cover_path, secret_path, output_path)
    return send_file(output_path, as_attachment=True)

@app.route('/decode_image_action', methods=['POST'])
def decode_image_action():
    if 'image' not in request.files:
        return "Invalid request", 400

    image = request.files['image']
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'recovered_secret.png')

    image.save(image_path)

    try:
        decode_image_from_image(image_path, output_path)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

# ========== AUDIO STEGANOGRAPHY ==========

@app.route('/audio')
def audio_page():
    return render_template('audio.html')

@app.route('/encode_audio', methods=['POST'])
def encode_audio_action():
    if 'audio' not in request.files or 'message' not in request.form:
        return "Invalid request", 400

    audio = request.files['audio']
    message = request.form['message']

    if not audio.filename.lower().endswith('.wav'):
        return "Only WAV files supported", 400

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio_encoded.wav')

    audio.save(audio_path)
    encode_audio(audio_path, message, output_path)

    return send_file(output_path, as_attachment=True)

@app.route('/decode_audio', methods=['POST'])
def decode_audio_action():
    if 'audio' not in request.files:
        return "Invalid request", 400

    audio = request.files['audio']
    if not audio.filename.lower().endswith('.wav'):
        return "Only WAV files supported", 400

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
    audio.save(audio_path)

    message = decode_audio(audio_path)
    return render_template('audio.html', decoded_message=message)

# ================= MAIN =================

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)