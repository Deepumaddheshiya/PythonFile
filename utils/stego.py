from PIL import Image
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def encode_message(image_path, message, output_path, password=None):
    img = Image.open(image_path).convert("RGB")  # Always convert to RGB to avoid channel issues
    pixels = img.load()
    width, height = img.size

    if password:
        # Encryption Mode
        salt = os.urandom(16)
        key = derive_key(password, salt)
        f = Fernet(key)
        # Prefix with SALT + encrypted_message
        encrypted_message = f.encrypt(message.encode())
        # We need to store: [MAGIC_FLAG][SALT][Message] to know it's encrypted
        # Let's say magic flag is "ENC:"
        final_payload_bytes = b"ENC:" + salt + encrypted_message
        
        # Convert bytes to binary string
        binary_message = ''.join(format(byte, '08b') for byte in final_payload_bytes)
    else:
        # Plaintext Mode
        binary_message = ''.join(format(ord(char), '08b') for char in message)
    
    binary_message += '00000000'  # Null terminator

    if len(binary_message) > width * height * 3:
        raise ValueError("Message too long for this image")

    bit_index = 0
    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])
            for channel in range(3):
                if bit_index < len(binary_message):
                    pixel[channel] = (pixel[channel] & 0xFE) | int(binary_message[bit_index])
                    bit_index += 1
            pixels[x, y] = tuple(pixel)
            if bit_index >= len(binary_message):
                break
        else:
            continue
        break

    img.save(output_path)

def decode_message(image_path, password=None):
    img = Image.open(image_path).convert("RGB")  # Always convert to RGB for consistent channel access
    pixels = img.load()
    width, height = img.size

    binary_message = []
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            for channel in range(3):
                binary_message.append(str(pixel[channel] & 1))

    # Convert binary to bytes
    all_bytes = bytearray()
    for i in range(0, len(binary_message), 8):
        byte_str = binary_message[i:i+8]
        if byte_str == ['0']*8:
            break
        all_bytes.append(int(''.join(byte_str), 2))
    
    # Try to detect if encrypted
    # Format: b"ENC:" + 16 bytes salt + ciphertext
    if all_bytes.startswith(b"ENC:"):
        if not password:
            return "🔒 This message is encrypted. Please provide a password."
        
        try:
            salt = bytes(all_bytes[4:20])
            ciphertext = bytes(all_bytes[20:])
            
            key = derive_key(password, salt)
            f = Fernet(key)
            decrypted_message = f.decrypt(ciphertext)
            return decrypted_message.decode()
        except Exception:
            return "❌ Incorrect password or corrupted data."
    else:
        # Backward compatibility for old plain text messages
        try:
            return all_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback for old character-by-character logic if bytes fail (rare)
            return "Error decoding message (format mismatch)."

def calculate_capacity(image_path):
    img = Image.open(image_path).convert("RGB")  # Convert to RGB to get accurate capacity
    width, height = img.size
    max_bits = width * height * 3
    max_bytes = max_bits // 8
    return {
        'width': width,
        'height': height,
        'pixels': width * height,
        'max_bits': max_bits,
        'max_bytes': max_bytes,
        'max_chars': max_bytes - 1  # Subtract 1 for null terminator
    }

def encode_image_in_image(cover_path, secret_path, output_path):
    cover = Image.open(cover_path)
    secret = Image.open(secret_path)
    
    # Calculate max size for secret image (same logic as text, 1 bit per channel)
    cover_width, cover_height = cover.size
    max_secret_pixels = (cover_width * cover_height * 3) // 8  # bits -> bytes
    # approx max square size: sqrt(max_bytes / 3) / 8... simplify:
    
    # Resize secret image to be small enough. 
    # Let's say we aim for it to be much smaller to ensure quality.
    # For MVP, we resize secret to 100x100 if it's too big, or error out?
    # Better: Resize to fit.
    
    # 1 secret pixel = 3 bytes (24 bits). We need 24 cover pixels to hide 1 secret pixel? 
    # No, 1 cover pixel has 3 basic updates (LSB R, G, B) = 3 bits capacity.
    # So 1 secret pixel (24 bits) needs 8 cover pixels (8 * 3 = 24).
    
    max_pixels = (cover_width * cover_height) // 8
    
    if secret.width * secret.height > max_pixels:
        # Resize secret
        ratio = (max_pixels / (secret.width * secret.height)) ** 0.5
        new_w = int(secret.width * ratio * 0.9)
        new_h = int(secret.height * ratio * 0.9)
        secret = secret.resize((new_w, new_h))
    
    secret = secret.convert('RGB')
    cover = cover.convert('RGB')
    
    secret_pixels = secret.load()
    cover_pixels = cover.load()
    
    # Header: "IMG:" + 4 bytes width + 4 bytes height
    w_bytes = secret.width.to_bytes(4, 'big')
    h_bytes = secret.height.to_bytes(4, 'big')
    header = b"IMG:" + w_bytes + h_bytes
    
    # Convert header + secret pixels to bits
    bits = []
    
    # Header bits
    for byte in header:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
            
    # Secret Image bits
    for y in range(secret.height):
        for x in range(secret.width):
            r, g, b = secret_pixels[x, y]
            for val in (r, g, b):
                for i in range(8):
                    bits.append((val >> (7 - i)) & 1)
                    
    # Embed
    bit_idx = 0
    total_bits = len(bits)
    
    for y in range(cover_height):
        for x in range(cover_width):
            r, g, b = cover_pixels[x, y]
            
            if bit_idx < total_bits:
                r = (r & 0xFE) | bits[bit_idx]
                bit_idx += 1
            if bit_idx < total_bits:
                g = (g & 0xFE) | bits[bit_idx]
                bit_idx += 1
            if bit_idx < total_bits:
                b = (b & 0xFE) | bits[bit_idx]
                bit_idx += 1
                
            cover_pixels[x, y] = (r, g, b)
            
            if bit_idx >= total_bits:
                break
        else:
            continue
        break
        
    cover.save(output_path)


def decode_image_from_image(image_path, output_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()
    width, height = img.size
    
    bits = []
    
    # Extract all bits (this is inefficient for huge images, but okay for MVP)
    # Be careful with memory. We only need enough for header first!
    
    extracted_bytes = bytearray()
    byte_builder = 0
    bit_count = 0
    
    state = "HEADER" # HEADER, PIXELS
    secret_w = 0
    secret_h = 0
    expected_bytes = 0
    
    # header is 4 ("IMG:") + 4 (W) + 4 (H) = 12 bytes
    HEADER_SIZE = 12
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            for val in (r, g, b):
                byte_builder = (byte_builder << 1) | (val & 1)
                bit_count += 1
                
                if bit_count == 8:
                    extracted_bytes.append(byte_builder)
                    byte_builder = 0
                    bit_count = 0
                    
                    if state == "HEADER" and len(extracted_bytes) == HEADER_SIZE:
                        if extracted_bytes[:4] != b"IMG:":
                             raise ValueError("No hidden image found (Magic Header missing)")
                        
                        secret_w = int.from_bytes(extracted_bytes[4:8], 'big')
                        secret_h = int.from_bytes(extracted_bytes[8:12], 'big')
                        expected_bytes = secret_w * secret_h * 3
                        state = "PIXELS"
                        extracted_bytes = bytearray() # Reset for pixel data
                        
                    elif state == "PIXELS" and len(extracted_bytes) >= expected_bytes:
                         # Done!
                         secret_img = Image.new('RGB', (secret_w, secret_h))
                         secret_pixels = secret_img.load()
                         idx = 0
                         for sy in range(secret_h):
                             for sx in range(secret_w):
                                 r = extracted_bytes[idx]
                                 g = extracted_bytes[idx+1]
                                 b = extracted_bytes[idx+2]
                                 secret_pixels[sx, sy] = (r, g, b)
                                 idx += 3
                         
                         secret_img.save(output_path)
                         return True
                         
            if state == "PIXELS" and len(extracted_bytes) >= expected_bytes:
                break
        if state == "PIXELS" and len(extracted_bytes) >= expected_bytes:
            break

    if state != "PIXELS" or len(extracted_bytes) < expected_bytes:
         raise ValueError("Incomplete data or image too noisy")

