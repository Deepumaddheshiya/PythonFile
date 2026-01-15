# 🔐 AI-Powered Advanced Steganography Tool

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Cryptography](https://img.shields.io/badge/Encryption-AES--256-red.svg)

**A next-generation steganography platform combining classic data hiding techniques with modern AI and military-grade cryptography.**

[Features](#-features) • [Installation](#-installation--setup) • [Usage](#-usage) • [Tech Stack](#-tech-stack) • [Documentation](#-api-documentation)

</div>

---

## 📖 Overview

This is a powerful web-based steganography tool that allows you to hide secret messages, files, and images inside other media files using LSB (Least Significant Bit) techniques. It goes beyond traditional steganography by offering:

- **🔒 AES-256 Encryption** for enhanced security
- **🤖 Google Gemini AI** for intelligent content generation
- **🕵️ Steganalysis** tools for hidden data detection
- **🎵 Audio Steganography** for WAV files
- **🖼️ Image-in-Image** embedding

Built with **Python**, **Flask**, and a modern **Glassmorphism UI**.

---

## 🎯 System Architecture

```
User Interface (HTML/CSS/JS)
          ↓
    Flask Backend
          ↓
  AES-256 Encryption Layer
          ↓
Steganography Engine (LSB)
    ├── Image Processing
    └── Audio Processing
          ↓
  AI Content Generator (Gemini)
          ↓
    Secure Output Media
```

---

## ✨ Features

### 1. 📝 Text Steganography
- Hide secret text messages inside PNG/JPEG images
- **AI Integration**: Generate poems, stories, or custom messages using Google Gemini AI
- Optional password protection with AES-256 encryption
- Visual capacity calculator to check how much data can be hidden

<img width="425" height="903" alt="image" src="https://github.com/user-attachments/assets/c610cbe5-c573-4318-a2ab-5c018ae80b13" />


### 2. 🔐 Military-Grade Encryption
- AES-256 encryption with password-based key derivation (PBKDF2)
- Salt generation for enhanced security
- Even if data is extracted, it remains unreadable without the correct password

<img width="565" alt="Encrypted Steganography" src="https://github.com/user-attachments/assets/baba65fb-725b-4087-994d-f85840064a4d" />

### 3. 🖼️ Image-in-Image Steganography
- Hide a complete image inside another larger cover image
- Automatic dimension validation
- Perfect for transferring diagrams, photos, or maps covertly

<img width="564" alt="Image in Image" src="https://github.com/user-attachments/assets/f1892445-ff75-4d35-87a6-050a7f5b343b" />

### 4. 🎵 Audio Steganography
- Embed secret text messages in `.wav` audio files
- LSB manipulation of audio frames for undetectable data hiding
- Extract hidden messages from audio files

<img width="900" alt="Audio Steganography" src="https://github.com/user-attachments/assets/8804bbc3-74f5-4697-a660-df4b571b4c80" />

### 5. 🕵️ Steganalysis (Detection Mode)
- Analyze images for hidden data
- Visualize LSB noise patterns
- Chi-square statistical analysis
- Detect potential steganographic content

---

## 🔒 Security Workflow

1. **Input**: User provides secret text, image, or file
2. **Encryption**: Data is encrypted using AES-256 with user-defined password
3. **Embedding**: Encrypted payload is embedded using LSB steganography
4. **Extraction**: Requires correct password and decoding logic
5. **Decryption**: Without the key, extracted data remains unreadable

**Security Features:**
- Password-based key derivation (PBKDF2HMAC)
- Random salt generation
- SHA-256 hashing
- Secure file handling

---

## 🤖 AI-Assisted Content Generation

Unlike traditional steganography tools, this application integrates **Google Gemini AI** to:
- Generate natural-sounding poems, stories, or messages
- Improve usability for non-technical users
- Make hidden data statistically harder to detect with natural language patterns
- Support creative writing prompts

**Optional Feature**: Works with or without API key (graceful fallback)

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend** | Python 3.10+, Flask |
| **Image Processing** | Pillow (PIL) |
| **Cryptography** | `cryptography` library (Fernet/AES-256) |
| **AI Model** | Google Gemini Pro API |
| **Audio Processing** | Wave module |
| **Frontend** | HTML5, CSS3 (Glassmorphism), JavaScript |
| **Security** | PBKDF2HMAC, SHA-256 |

---

## 📁 Project Structure

```
PythonFile/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── models.txt                 # Model information
├── README.md                  # Project documentation
├── .env                       # Environment variables (not in repo)
├── .gitignore                 # Git ignore rules
├── static/
│   └── style.css             # Glassmorphism UI styles
├── templates/                 # HTML templates
│   ├── index.html            # Landing page
│   ├── encode.html           # Text encoding
│   ├── decode.html           # Text decoding
│   ├── encode_image.html     # Image-in-image encoding
│   ├── decode_image.html     # Image extraction
│   ├── audio.html            # Audio steganography
│   ├── analyze.html          # Steganalysis
│   ├── capacity.html         # Capacity calculator
│   └── *_result.html         # Result pages
├── uploads/                   # Temporary file storage (gitignored)
└── utils/                     # Core steganography modules
    ├── stego.py              # Image steganography functions
    ├── audio.py              # Audio steganography
    └── analysis.py           # Steganalysis tools
```

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip package manager
- (Optional) Google Gemini API key

### Step-by-Step Installation

1. **Clone the Repository**
```bash
git clone https://github.com/Deepumaddheshiya/PythonFile.git
cd PythonFile
```

2. **Create Virtual Environment (Recommended)**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
```

**Get your API key**: [Google AI Studio](https://makersuite.google.com/app/apikey)

> **Note**: The application works without an API key, but AI features will be disabled.

5. **Run the Application**
```bash
python app.py
```

6. **Open in Browser**
```
http://127.0.0.1:5000
```

---

## 🚀 Usage

### Encoding a Secret Message
1. Navigate to **Encode Text** page
2. Upload a cover image (PNG/JPEG)
3. Enter your secret message or use AI to generate one
4. (Optional) Set a password for encryption
5. Click **Encode** to download the stego-image

### Decoding a Hidden Message
1. Navigate to **Decode Text** page
2. Upload the stego-image
3. Enter the password (if used during encoding)
4. Click **Decode** to reveal the secret message

### Image-in-Image Steganography
1. Navigate to **Hide Image** page
2. Upload cover image (must be larger)
3. Upload secret image to hide
4. Download the result

### Audio Steganography
1. Navigate to **Audio** page
2. Upload a WAV audio file
3. Enter secret message
4. Download the modified audio file

### Steganalysis
1. Navigate to **Analyze Image** page
2. Upload a suspicious image
3. View LSB visualization and statistical analysis

---

## 📡 API Documentation

### Core Functions

#### `encode_message(image_path, message, output_path, password=None)`
Embeds text into an image using LSB steganography.
- **Parameters**:
  - `image_path`: Path to cover image
  - `message`: Secret text to hide
  - `output_path`: Output stego-image path
  - `password`: Optional encryption password
- **Returns**: Path to stego-image

#### `decode_message(image_path, password=None)`
Extracts hidden message from stego-image.
- **Returns**: Decrypted message string

#### `encode_image_in_image(cover_path, secret_path, output_path)`
Hides one image inside another.

#### `calculate_capacity(image_path)`
Returns maximum data capacity in bytes.

---

## 🎨 User Interface

Modern **Glassmorphism Design** featuring:
- 🌊 Animated gradient backgrounds
- ❄️ Frosted glass cards with backdrop blur
- 🎨 Smooth transitions and hover effects
- 📱 Fully responsive layout
- ✨ Professional color scheme

<img width="561" alt="UI Preview" src="https://github.com/user-attachments/assets/9f0d7d78-21c4-400d-a693-73f82ba8ced4" />

---

## 🎯 Use Cases

- 🗞️ **Journalists**: Secure communication in hostile environments
- 🔬 **Researchers**: Privacy-focused data transfer
- 🎓 **Education**: Cybersecurity and cryptography labs
- 🛡️ **Red/Blue Teams**: Steganography training exercises
- 🔐 **Privacy Advocates**: Covert data transmission

---

## 🚧 Limitations & Future Enhancements

### Current Limitations
- Image support limited to PNG, JPEG, BMP
- Audio support only for WAV format
- Maximum file size: 5MB
- Local deployment only

### Planned Features
- [ ] Video steganography (MP4, AVI)
- [ ] Advanced ML-based steganalysis
- [ ] Cloud deployment (AWS/Azure)
- [ ] Multi-language support
- [ ] Mobile app (Flutter)
- [ ] Batch processing
- [ ] CLI version
- [ ] Docker containerization

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Legal Disclaimer

**IMPORTANT**: This tool is intended for **educational and ethical testing purposes only**. 

- Use only on files you own or have explicit permission to modify
- Do not use for illegal activities or unauthorized data hiding
- The authors are **not responsible** for any misuse of this software
- Check your local laws regarding steganography and encryption
- Using steganography for malicious purposes may be illegal in your jurisdiction

---

## 👨‍💻 Author

**Deepu Maddheshiya**
- GitHub: [@Deepumaddheshiya](https://github.com/Deepumaddheshiya)
- Github: [@adarshhh25](https://github.com/adarshhh25)
---

## 🙏 Acknowledgments

- Google Gemini AI for intelligent content generation
- Flask community for excellent web framework
- Pillow contributors for image processing capabilities
- Cryptography library developers

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ and Python

</div>
