import unittest
import io
import os
import wave
import base64
import json
import sys

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import app

class StegoFullTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        print("\n" + "="*50)
        
        # 1. Create Dummy Image (100x100 Red PNG)
        from PIL import Image
        img = Image.new('RGB', (200, 200), color = 'red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        self.image_bytes = img_byte_arr.getvalue()
        self.image_b64 = "data:image/png;base64," + base64.b64encode(self.image_bytes).decode('utf-8')
        
        # 2. Create Dummy Secret Image (50x50 Blue PNG)
        secret_img = Image.new('RGB', (50, 50), color = 'blue')
        secret_byte_arr = io.BytesIO()
        secret_img.save(secret_byte_arr, format='PNG')
        self.secret_image_bytes = secret_byte_arr.getvalue()
        self.secret_image_b64 = "data:image/png;base64," + base64.b64encode(self.secret_image_bytes).decode('utf-8')
        
        # 3. Create Dummy Audio (1 sec silent WAV)
        audio_byte_arr = io.BytesIO()
        with wave.open(audio_byte_arr, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(1)
            wav_file.setframerate(8000)
            wav_file.writeframes(b'\x00' * 8000)
        self.audio_bytes = audio_byte_arr.getvalue()
        self.audio_b64 = "data:audio/wav;base64," + base64.b64encode(self.audio_bytes).decode('utf-8')

    def log(self, msg):
        print(f"TEST: {msg}")

    # ================= HEALTH CHECK =================
    def test_01_health_check(self):
        self.log("Checking Health Endpoint...")
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.log("✅ Health Check Passed")

    # ================= TEXT IN IMAGE =================
    def test_02_text_in_image(self):
        self.log("Testing Text in Image (Encode -> Decode)...")
        msg = "Secret Text 123"
        
        # Encode
        data = {
            'image': (io.BytesIO(self.image_bytes), 'test.png'),
            'message': msg
        }
        resp_enc = self.app.post('/api/encode/text-image', data=data, content_type='multipart/form-data')
        self.assertEqual(resp_enc.status_code, 200)
        self.assertTrue(resp_enc.json['success'])
        
        encoded_img_b64 = resp_enc.json['encodedImage'].split(',')[1]
        encoded_bytes = base64.b64decode(encoded_img_b64)
        
        # Decode
        data_dec = {
            'image': (io.BytesIO(encoded_bytes), 'encoded.png')
        }
        resp_dec = self.app.post('/api/decode/text-image', data=data_dec, content_type='multipart/form-data')
        self.assertEqual(resp_dec.json['text'], msg)
        self.log("✅ Text-Image Flow Passed")

    def test_03_text_in_image_encrypted(self):
        self.log("Testing Text in Image ENCRYPTED...")
        msg = "Super Secret"
        pwd = "password123"
        
        # Encode
        data = {
            'image': (io.BytesIO(self.image_bytes), 'test.png'),
            'message': msg,
            'password': pwd
        }
        resp_enc = self.app.post('/api/encode/text-image', data=data, content_type='multipart/form-data')
        self.assertEqual(resp_enc.status_code, 200)
        
        encoded_bytes = base64.b64decode(resp_enc.json['encodedImage'].split(',')[1])
        
        # Decode with Password
        data_dec = {
            'image': (io.BytesIO(encoded_bytes), 'enc.png'),
            'password': pwd
        }
        resp_dec = self.app.post('/api/decode/text-image', data=data_dec, content_type='multipart/form-data')
        self.assertEqual(resp_dec.json['text'], msg)
        self.log("✅ Encrypted Text-Image Flow Passed")

    # ================= AUDIO STEGANOGRAPHY =================
    def test_04_audio_stego(self):
        self.log("Testing Audio Steganography...")
        msg = "Audio Message"
        
        # Encode
        data = {
            'audio': (io.BytesIO(self.audio_bytes), 'test.wav'),
            'message': msg
        }
        resp_enc = self.app.post('/api/encode/audio', data=data, content_type='multipart/form-data')
        self.assertEqual(resp_enc.status_code, 200)
        self.assertTrue(resp_enc.json['success'])
        
        encoded_bytes = base64.b64decode(resp_enc.json['encodedAudio'].split(',')[1])
        
        # Decode
        data_dec = {
            'audio': (io.BytesIO(encoded_bytes), 'enc.wav')
        }
        resp_dec = self.app.post('/api/decode/audio', data=data_dec, content_type='multipart/form-data')
        self.assertEqual(resp_dec.json['text'], msg)
        self.log("✅ Audio Flow Passed")

    # ================= IMAGE IN IMAGE =================
    def test_05_image_in_image(self):
        self.log("Testing Image in Image...")
        
        # Encode
        data = {
            'cover_image': (io.BytesIO(self.image_bytes), 'cover.png'),
            'secret_image': (io.BytesIO(self.secret_image_bytes), 'secret.png')
        }
        resp_enc = self.app.post('/api/encode/image-image', data=data, content_type='multipart/form-data')
        self.assertEqual(resp_enc.status_code, 200)
        self.assertTrue(resp_enc.json['success'])
        
        encoded_bytes = base64.b64decode(resp_enc.json['encodedImage'].split(',')[1])
        
        # Decode
        data_dec = {
            'image': (io.BytesIO(encoded_bytes), 'stego_img.png')
        }
        resp_dec = self.app.post('/api/decode/image-image', data=data_dec, content_type='multipart/form-data')
        self.assertTrue(resp_dec.json['success'])
        
        # Verify we got an image back
        self.assertTrue(resp_dec.json['secretImage'].startswith('data:image/png;base64,'))
        self.log("✅ Image-Image Flow Passed")

    # ================= CHECK CAPACITY =================
    def test_06_capacity(self):
        self.log("Testing Capacity Check...")
        data = {
            'image': (io.BytesIO(self.image_bytes), 'cap.png')
        }
        resp = self.app.post('/api/capacity', data=data, content_type='multipart/form-data')
        cap = resp.json['capacity']
        self.assertTrue(cap['max_chars'] > 0)
        self.log(f"✅ Capacity Check Passed (Max chars: {cap['max_chars']})")

if __name__ == '__main__':
    unittest.main(verbosity=2)
