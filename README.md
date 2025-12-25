# 🕵️ AI-Powered Advanced Steganography Tool

**A next-generation Steganography platform blending classic data hiding techniques with modern AI and Cryptography.**

![Project Banner](static/animation.gif.gif)

## 🚀 Overview
This project is a powerful web application that allows you to hide secret messages, files, and images inside other media files. It goes beyond simple text-shuffling by offering **AES-256 Encryption** for security, **Google Gemini AI** for content generation, and **Steganalysis** tools for detection.

Built with **Python**, **Flask**, and **Modern Glassmorphism UI**.

## ✨ Key Features

### 1. 📝 Text Steganography (Classic)
- Hide secret text messages inside PNG images.
- **AI Integration**: Stuck on what to write? Ask the built-in AI to generate a poem, story, or message for you!

### 2. 🔐 AES-256 Military-Grade Encryption
- Secure your hidden messages with a password.
- Even if someone extracts the data, they cannot read it without your key.

### 3. 🖼️ Image-in-Image Steganography
- Hide a **full image** inside another larger cover image.
- Perfect for secretly transferring diagrams, photos, or maps.

### 4. 🎵 Audio Steganography
- Hide secret text messages inside `.wav` audio files.
- Modifies the LSB (Least Significant Bit) of audio frames for undetectable transmission.

### 5. 🕵️ Steganalysis (Defensive Mode)
- Suspect an image has hidden data?
- Use the **Scan Image** tool to visualize LSB noise and detect hidden payloads.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.10+, Flask
- **Image Processing**: Pillow (PIL)
- **Cryptography**: `cryptography` (Fernet/AES)
- **AI Model**: Google Gemini Pro (via `google-generativeai`)
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript

---

## 📦 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/steganography-tool.git
    cd steganography-tool
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key**
    - Create a `.env` file in the root directory.
    - Add your Google Gemini API Key:
      ```env
      GEMINI_API_KEY=your_api_key_here
      ```

4.  **Run the Application**
    ```bash
    python app.py
    ```

5.  **Open in Browser**
    - Visit `http://127.0.0.1:5000`

---

## 🎨 User Interface
The application features a dark, modern **Glassmorphism** design with:
- Animated backgrounds
- Frosted glass cards
- Gradient buttons
- Responsive layout for mobile and desktop

## ⚠️ Legal Disclaimer
This tool is intended for educational and ethical testing purposes only. The authors are not responsible for any misuse of this software.
