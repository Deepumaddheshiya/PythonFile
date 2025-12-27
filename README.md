AI-Powered Advanced Steganography Tool

A next-generation Steganography platform blending classic data hiding techniques with modern AI and Cryptography.

![Project Banner](static/animation.gif.gif)

🚀 Overview
This project is a powerful web application that allows you to hide secret messages, files, and images inside other media files. It goes beyond simple text-shuffling by offering **AES-256 Encryption** for security, **Google Gemini AI** for content generation, and **Steganalysis** tools for detection.

Built with **Python**, **Flask**, and **Modern** Glassmorphism UI**.


🧩 System Architecture
User → Web UI (HTML/CSS/JS)  
→ Flask Backend  
→ AES-256 Encryption Layer  
→ Steganography Engine (Image / Audio LSB)  
→ AI Content Generator (Google Gemini)  
→ Secure Output Media


✨ **Key Features**
### 1. 📝 Text Steganography (Classic)
- Hide secret text messages inside PNG images.
- **AI Integration**: Stuck on what to write? Ask the built-in AI to generate a poem, story, or message for you!
- <img width="563" height="838" alt="image" src="https://github.com/user-attachments/assets/a83e1c8a-4381-47e6-95da-07bf889ef97f" />

### 2. 🔐 AES-256 Military-Grade Encryption
- Secure your hidden messages with a password.
- Even if someone extracts the data, they cannot read it without your key.
- <img width="565" height="867" alt="image" src="https://github.com/user-attachments/assets/baba65fb-725b-4087-994d-f85840064a4d" />

### 3. 🖼️ Image-in-Image Steganography
- Hide a **full image** inside another larger cover image.
- Perfect for secretly transferring diagrams, photos, or maps.
- <img width="564" height="712" alt="image" src="https://github.com/user-attachments/assets/f1892445-ff75-4d35-87a6-050a7f5b343b" />

### 4. 🎵 **Audio Steganography**
- Hide secret text messages inside `.wav` audio files.
- Modifies the LSB (Least Significant Bit) of audio frames for undetectable transmission.
- <img width="900" height="723" alt="image" src="https://github.com/user-attachments/assets/8804bbc3-74f5-4697-a660-df4b571b4c80" />

### 5. 🕵️ Steganalysis (Defensive Mode)
- Suspect an image has hidden data?
- Use the **Scan Image** tool to visualize LSB noise and detect hidden payloads.

---

## 🔒 Security Workflow
1. User inputs secret text, image, or file  
2. Data is encrypted using AES-256 with a user-defined password  
3. Encrypted payload is embedded using LSB steganography  
4. Extraction requires correct password and decoding logic  
5. Without the key, extracted data remains unreadable  

---

## 🤖 AI-Assisted Content Generation
Unlike traditional steganography tools, this application integrates **Google Gemini AI**
to generate natural-sounding poems or stories automatically.
This improves usability and makes hidden data statistically harder to detect.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.10+, Flask
- **Image Processing**: Pillow (PIL)
- **Cryptography**: `cryptography` (Fernet/AES)
- **AI Model**: Google Gemini Pro (`google-generativeai`)
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript

---

## 📁 Project Structure
<img width="763" height="658" alt="image" src="https://github.com/user-attachments/assets/e17d4318-a37f-4584-a88a-5fe088f52d65" />
<img width="685" height="817" alt="image" src="https://github.com/user-attachments/assets/fdd170a7-311d-4451-8c01-112976dad545" />


## 📦 Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/Deepumaddheshiya/PythonFile.git
cd Steganography_AI_Tool

2. Install Dependencies
pip install -r requirements.txt

3. Configure API Key
GEMINI_API_KEY=your_api_key_here

4. Run the Application
python app.py

5. Open in Browser
Visit: http://127.0.0.1:5000


🎨 User Interface

The application features a modern Glassmorphism UI with:

Animated backgrounds

Frosted glass cards

Gradient buttons

Fully responsive layout

<img width="561" height="499" alt="image" src="https://github.com/user-attachments/assets/9f0d7d78-21c4-400d-a693-73f82ba8ced4" />


🎯 Use Cases

Secure communication for journalists and researchers

Cybersecurity education and ethical hacking labs

Red & Blue team steganography training

Privacy-focused data transfer


🚧 Limitations & Future Enhancements

Currently supports PNG images and WAV audio only

Video steganography can be added

Cloud deployment planned

Mobile app version using Flutter

Advanced ML-based steganalysis


⚠️ Legal Disclaimer

This tool is intended for educational and ethical testing purposes only.
The authors are not responsible for any misuse of this software.
