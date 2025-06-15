# 🔐 StegoGhost – Steganographic Application

## ✨ Features

* 🔒 **Security** – AES-256 encryption with password protection
* 🎯 **Advanced Steganography** – LSB with pseudo-random pixel distribution
* 📊 **Capacity Analysis** – Automatically calculates maximum message size
* 🖼️ **Format Support** – PNG, JPEG, WebP images
* 💪 **Reliability** – Deterministic algorithms for accurate extraction

## 🖥️ Interface

The application provides two main operation modes:

### 🔒 Hide Message

* Select a container image
* Enter a secret message (up to 4096 characters)
* Set a strong password
* Save the resulting image automatically

### 🔓 Extract Message

* Upload an image with hidden data
* Enter the password to decrypt
* Display the extracted message

## 🚀 Installation

### Requirements

* Python 3.8 or higher
* Windows (primary support)

### Install dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

* **Pillow** – Image processing
* **cryptography** – Cryptographic functions
* **PyQt5** – GUI framework
* **numpy** – Numerical computing
* **psutil** – System info

## 🎯 Usage

### Run the application

```bash
python main.py
```

### Hiding a message

1. Open the "🔒 Hide Message" tab
2. Click "Browse..." and select an image
3. Enter your secret message
4. Set a strong password
5. Click "🔐 Hide and Save"
6. Choose a location to save the result

### Extracting a message

1. Open the "🔓 Extract Message" tab
2. Select the image containing hidden data
3. Enter the correct password
4. Click "🔓 Extract Message"
5. Read the extracted message

## 🔧 Technical Details

### Steganography Algorithm

* **Method**: LSB (Least Significant Bit) in the red channel
* **Distribution**: Pseudo-random pixel selection based on the password
* **Header**: 4-byte header to store encrypted data length

### Cryptography

* **Encryption**: AES-256 in CBC mode
* **Key**: Derived from password using PBKDF2
* **Salt**: Random 16-byte salt for each message

### Data Format

```
[4 bytes - length] [encrypted data]
```

## 📁 Project Structure

```
stegomouse/
├── main.py              # Application entry point  
├── gui.py               # GUI (PyQt5)  
├── stego_engine.py      # Steganographic engine  
├── crypto_module.py     # Cryptographic functions

├── build.py             # Build script  
├── requirements.txt     # Python dependencies  
├── .gitignore           # Git ignore rules  
├── README.md            # Documentation  
└── CHANGELOG.md         # Changelog
```

## 🛠️ Building Executable

To generate a `.exe` file:

```bash
python build.py
```

The result will be placed in the `dist/` folder.

## 🔒 Security

### Password Recommendations

* Use long passwords (12+ characters)
* Include letters, numbers, and special characters
* Avoid dictionary words

### Limitations

* Maximum message size: 4096 characters
* Supported formats: PNG, JPEG, WebP
* PNG is recommended for best quality

## ⚠️ Notes

* **Output format**: Always saved as PNG for quality preservation
* **Original image**: Remains unchanged, a new copy is created
* **Performance**: Depends on image size
* **Compatibility**: Main support for Windows

## 🐛 Troubleshooting

### Encryption Errors

* Check if the correct password was entered
* Ensure the image contains hidden data

### Format Issues

* Use PNG for better compatibility
* Avoid highly compressed JPEGs

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a new branch for your changes
3. Implement and test your modifications
4. Submit a Pull Request

## 📞 Support

For questions or suggestions, feel free to open an issue or contact the maintainer.

