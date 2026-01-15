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

# ========== TEXT STEGANOGRAPHY ==========

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        try:
            if 'image' not in request.files or 'message' not in request.form:
                return render_template('encode.html', error="Invalid request")

            image = request.files['image']
            if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
                return render_template('encode.html', error="Invalid file type")

            message = request.form['message']
            encrypt = request.form.get('encrypt') == 'on'
            password = request.form.get('password', '')

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            input_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            output_name = f"encoded_{os.path.splitext(image.filename)[0]}.png"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_name)

            image.save(input_path)
            encode_message(input_path, message, output_path, password if encrypt else None)

            return send_file(output_path, as_attachment=True, download_name=output_name)
        except Exception as e:
            return render_template('encode.html', error=str(e))
    
    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode_page():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return render_template('decode.html', error="Invalid request")

            image = request.files['image']
            password = request.form.get('password')

            if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
                return render_template('decode.html', error="Invalid file type")

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)

            message = decode_message(image_path, password)
            return render_template('decode.html', message=message)
        except Exception as e:
            return render_template('decode.html', error=str(e))
    
    return render_template('decode.html')

@app.route('/capacity', methods=['GET', 'POST'])
def capacity_page():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return render_template('capacity.html', error="Invalid request")

            image = request.files['image']
            if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
                return render_template('capacity.html', error="Invalid file type")

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(path)

            capacity = calculate_capacity(path)
            return render_template('capacity.html', capacity=capacity)
        except Exception as e:
            return render_template('capacity.html', error=str(e))
    
    return render_template('capacity.html')

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

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_page():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return render_template('analyze.html', error="Invalid request")

            image = request.files['image']
            if not allowed_file(image.filename, ALLOWED_EXTENSIONS):
                return render_template('analyze.html', error="Invalid file type")

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis_' + image.filename)

            image.save(img_path)
            analyze_image(img_path, output_path)

            return render_template(
                'analyze.html',
                original_image=f'uploads/{image.filename}',
                analysis_image=f'uploads/analysis_{image.filename}'
            )
        except Exception as e:
            return render_template('analyze.html', error=str(e))
    
    return render_template('analyze.html')

# ========== IMAGE IN IMAGE ==========

@app.route('/encode_image', methods=['GET', 'POST'])
def encode_image_page():
    if request.method == 'POST':
        try:
            if 'cover_image' not in request.files or 'secret_image' not in request.files:
                return render_template('encode_image.html', error="Invalid request")

            cover = request.files['cover_image']
            secret = request.files['secret_image']

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            cover_path = os.path.join(app.config['UPLOAD_FOLDER'], cover.filename)
            secret_path = os.path.join(app.config['UPLOAD_FOLDER'], secret.filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'img_hidden.png')

            cover.save(cover_path)
            secret.save(secret_path)

            encode_image_in_image(cover_path, secret_path, output_path)
            return send_file(output_path, as_attachment=True, download_name='img_hidden.png')
        except Exception as e:
            return render_template('encode_image.html', error=str(e))
    
    return render_template('encode_image.html')

@app.route('/decode_image', methods=['GET', 'POST'])
def decode_image_page():
    if request.method == 'POST':
        try:
            if 'image' not in request.files:
                return render_template('decode_image.html', error="Invalid request")

            image = request.files['image']
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'recovered_secret.png')

            image.save(image_path)
            decode_image_from_image(image_path, output_path)
            
            return send_file(output_path, as_attachment=True, download_name='recovered_secret.png')
        except Exception as e:
            return render_template('decode_image.html', error=str(e))
    
    return render_template('decode_image.html')

# ========== AUDIO STEGANOGRAPHY ==========

@app.route('/audio', methods=['GET', 'POST'])
def audio_page():
    if request.method == 'POST':
        action = request.form.get('action')

        try:
            if action == 'encode':
                if 'audio' not in request.files or 'message' not in request.form:
                    return render_template('audio.html', error="Invalid request")

                audio = request.files['audio']
                message = request.form['message']

                if not audio.filename.lower().endswith('.wav'):
                    return render_template('audio.html', error="Only WAV files supported")

                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio_encoded.wav')

                audio.save(audio_path)
                encode_audio(audio_path, message, output_path)

                return send_file(output_path, as_attachment=True, download_name='audio_encoded.wav')

            elif action == 'decode':
                if 'audio' not in request.files:
                    return render_template('audio.html', error="Invalid request")

                audio = request.files['audio']
                if not audio.filename.lower().endswith('.wav'):
                    return render_template('audio.html', error="Only WAV files supported")

                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio.filename)
                audio.save(audio_path)

                message = decode_audio(audio_path)
                return render_template('audio.html', decoded_message=message)
        except Exception as e:
            return render_template('audio.html', error=str(e))
    
    return render_template('audio.html')

# ================= MAIN =================

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)