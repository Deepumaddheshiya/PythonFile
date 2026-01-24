import wave
import os
import base64
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

def encode_audio(audio_path, message, output_path, password=None):
    song = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    if password:
        # Encryption Mode
        salt = os.urandom(16)
        key = derive_key(password, salt)
        f = Fernet(key)
        # Prefix with ENC: + SALT + encrypted_message + ###
        encrypted_message = f.encrypt(message.encode())
        final_payload_bytes = b"ENC:" + salt + encrypted_message
        
        # Convert bytes to binary string
        binary_message = ''.join(format(byte, '08b') for byte in final_payload_bytes)
        binary_message += '11111111' * 5 # specific terminator for encrypted binary
    else:
        # Plaintext Mode with delimiter
        message += '###' 
        binary_message = ''.join(format(ord(char), '08b') for char in message)
    
    if len(binary_message) > len(frame_bytes):
        raise ValueError("Message too long for this audio file")

    for i in range(len(binary_message)):
        frame_bytes[i] = (frame_bytes[i] & 254) | int(binary_message[i])
        
    frame_modified = bytes(frame_bytes)
    
    with wave.open(output_path, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    
    song.close()

def decode_audio(audio_path, password=None):
    song = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    # Extract bits
    extracted_bits = ""
    # Optimization: processing all bytes might be slow for large audio, 
    # but we don't know the length. 
    # For MVP we can read a chunk or just go for it.
    # To avoid memory issues with huge strings, we should process in chunks, 
    # but let's stick to the current logic for consistency with existing code unless it's huge.
    
    for i in range(len(frame_bytes)):
        extracted_bits += str(frame_bytes[i] & 1)

    # Convert to bytes
    all_bytes = bytearray()
    for i in range(0, len(extracted_bits), 8):
        byte_str = extracted_bits[i:i+8]
        if i + 8 > len(extracted_bits):
            break 
        val = int(byte_str, 2)
        all_bytes.append(val)
        
        # Optimization: Check for termination or headers early to break?
        # For plaintext ### (3 chars = 24 bits)
        # For encrypted, we have a binary terminator? Or we rely on the implementation.
        # Let's parse fully for now as per original design.

    # Check for Encryption Header b"ENC:"
    if all_bytes.startswith(b"ENC:"):
        if not password:
             return "🔒 This message is encrypted. Please provide a password."
        
        try:
             # ENC: (4) + SALT (16) + ...
             salt = bytes(all_bytes[4:20])
             # We need to find where it ends.
             # In encode, we didn't add a delimiter for the encrypted bytes themselves directly inside the encrypted payload,
             # but we added a binary terminator 11111111...
             # Actually, Fernet decrypt handles padding, but we need to pass the exact ciphertext bytes.
             # The extracted `all_bytes` contains EVERYTHING till the end of audio file (noise).
             # We need a robust terminator.
             
             # Re-visiting encode: I added '11111111' * 5.
             # Let's search for that pattern? 
             # Or better, just try decrypting the valid chunk if we can determine length.
             # Since we don't have length header, we might have issues with trailing noise.
             
             # IMPROVED STRATEGY for Audio Encryption:
             # Store length header? Or stick to the terminator.
             
             # Let's search for the terminator in the all_bytes if possible?
             pass 
        except:
             pass

    # Re-implementing decode with a more stream-lined approach to catch delimiters
    
    # Text mode check (###)
    extracted_text = ""
    for b in all_bytes:
        extracted_text += chr(b)
        if extracted_text.endswith('###'):
            return extracted_text[:-3]

    # Encrypted mode check
    if all_bytes.startswith(b"ENC:"):
        if not password:
             return "🔒 This message is encrypted. Please provide a password."
        
        try:
            salt = bytes(all_bytes[4:20])
            # The rest is ciphertext + noise. Fernet needs exact ciphertext.
            # We explicitly added 5 bytes of 0xFF (255) as terminator
            ciphertext_with_noise = all_bytes[20:]
            
            # Find terminator b'\xff\xff\xff\xff\xff'
            terminator = b'\xff\xff\xff\xff\xff'
            end_idx = ciphertext_with_noise.find(terminator)
            
            if end_idx != -1:
                ciphertext = bytes(ciphertext_with_noise[:end_idx])
            else:
                # If sentinel not found, maybe try decrypting everything (might fail) or just up to a reasonable point?
                # or just take it all
                ciphertext = bytes(ciphertext_with_noise)
            
            key = derive_key(password, salt)
            f = Fernet(key)
            decrypted_message = f.decrypt(ciphertext)
            return decrypted_message.decode()
        except Exception as e:
            return f"❌ Incorrect password or corrupted data. ({str(e)})"

    return "Hidden message not found or file corrupted."
