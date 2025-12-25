import wave
import os

def encode_audio(audio_path, message, output_path):
    song = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    message += '###' # Delimiter
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

def decode_audio(audio_path):
    song = wave.open(audio_path, mode='rb')
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    
    start_extraction = False
    
    # Extract bits
    extracted = ""
    for i in range(len(frame_bytes)):
        extracted += str(frame_bytes[i] & 1)

    # Convert to chars
    decoded_message = ""
    for i in range(0, len(extracted), 8):
        byte = extracted[i:i+8]
        char = chr(int(byte, 2))
        decoded_message += char
        
        if decoded_message.endswith('###'):
            return decoded_message[:-3]
            
    # If delimiter not found (or file too short/noisy)
    return "Hidden message not found or file corrupted."
