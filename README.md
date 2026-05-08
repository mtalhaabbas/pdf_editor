# 📄 PDF Text Editor

A modern, interactive web-based PDF text editor that allows you to click on any text in a PDF to edit it while preserving the original font, size, and color. Features advanced OCR capabilities to detect and edit text rendered as images.

![PDF Text Editor](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### Core Functionality
- 🖱️ **Click-to-Edit Interface** - Simply click on any text in the PDF to edit it
- 🎨 **Format Preservation** - Maintains original font family, size, and color
- 📱 **Responsive Design** - Beautiful, modern UI that works on desktop, tablet, and mobile
- 🔄 **Real-time Preview** - See your changes instantly in the PDF viewer
- 📑 **Multi-page Support** - Navigate and edit across multiple pages
- 💾 **Easy Export** - Download your edited PDF with one click

### Advanced Features
- 🤖 **OCR Text Detection** - Automatically detects text in images using Tesseract OCR
- 🎯 **Dual Text Support**:
  - **Native PDF Text** (Blue highlight) - Editable text embedded in PDF
  - **OCR Text** (Yellow dashed highlight) - Text detected in images/graphics
- 🔍 **High-Quality Rendering** - Crystal-clear PDF display with high-DPI support
- 📐 **Smart Scaling** - Automatically scales PDFs to optimal viewing size (max 1200px)
- 🎭 **Smooth Animations** - Professional transitions and hover effects

### User Interface
- 🎨 **Modern Gradient Design** - Beautiful purple gradient background
- 📊 **Horizontal Top Bar** - All controls accessible in one compact row
- 🔘 **Toggle Controls** - Show/hide top bar for distraction-free viewing
- 📱 **Mobile Responsive** - Adapts perfectly to any screen size
- 🌙 **Clean Layout** - Minimalist design focused on productivity

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR (for image text detection)

### 1. Clone the Repository
```bash
git clone https://github.com/mtalhaabbas/pdf_editor.git
cd pdf_editor
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
1. Download the installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and follow the setup wizard
3. Add Tesseract to your system PATH

**Verify Installation:**
```bash
tesseract --version
```

## 📖 Usage

### Starting the Application

1. **Start the Flask server:**
```bash
python app.py
```

2. **Open your browser:**
```
http://localhost:5000
```

### Editing a PDF

1. **Upload PDF**
   - Click the file input in the top bar
   - Select your PDF file
   - Click "Load PDF" button

2. **Navigate Pages**
   - Use "← Prev" and "Next →" buttons to move between pages
   - Current page and total pages shown in the info section

3. **Edit Text**
   - **Hover** over text to see it highlight
   - **Click** on the text you want to edit
   - **Type** your new text in the modal dialog
   - **Press Enter** or click "Save Changes"

4. **Download Edited PDF**
   - Click the "💾 Download" button in the top bar
   - Your edited PDF will download as `edited_[filename].pdf`

### Understanding Text Types

- **Blue Highlight** = Native PDF text (fully editable)
- **Yellow Dashed Highlight** = OCR-detected text from images
  - Hover to see OCR confidence score
  - When edited, image is replaced with actual text

### Keyboard Shortcuts

- **Enter** - Save text changes in edit modal
- **Escape** - Close edit modal (click outside also works)

## 🎨 Interface Overview

### Top Bar (Left to Right)
1. **Title** - Application branding
2. **File Upload** - Choose and load PDF files
3. **Document Info** - Page count and current page number
4. **Navigation** - Previous/Next page buttons
5. **Legend** - Visual guide for text types
6. **Download** - Export edited PDF

### Toggle Button
- **Location**: Top-right corner
- **Function**: Show/hide top bar for full-screen viewing
- **Icon**: × (close) / ☰ (menu)

## 🛠️ Technical Stack

### Backend
- **Flask 3.0.0** - Web framework
- **PyMuPDF (fitz) 1.23.8** - PDF manipulation
- **Pytesseract 0.3.10** - OCR text detection
- **OpenCV 4.8.1** - Image processing
- **Pillow 10.1.0** - Image handling

### Frontend
- **PDF.js 3.11.174** - Client-side PDF rendering
- **Vanilla JavaScript** - No framework dependencies
- **Modern CSS3** - Gradients, animations, flexbox
- **Google Fonts (Inter)** - Professional typography

## 📁 Project Structure

```
pdf-text-editor/
├── app.py                 # Flask application & API endpoints
├── pdf_editor.py          # PDF manipulation & OCR logic
├── requirements.txt       # Python dependencies
├── README.md             # Documentation
├── templates/
│   └── index.html        # Frontend UI
├── uploads/              # Temporary PDF storage (auto-created)
└── outputs/              # Edited PDFs (auto-created)
```

## 🔧 Configuration

### Adjusting PDF Display Width
Edit `templates/index.html`, line ~280:
```javascript
if (baseViewport.width * pageScale > 1200) {
    scale = 1200 / baseViewport.width;  // Change 1200 to your preferred max width
}
```

### Changing OCR Confidence Threshold
Edit `pdf_editor.py`, line ~85:
```python
if text and conf > 30:  # Change 30 to adjust sensitivity (0-100)
```

### Adjusting Rendering Quality
Edit `templates/index.html`, line ~250:
```javascript
let pageScale = 2.5;  // Increase for higher quality (slower), decrease for speed
```

## 🐛 Troubleshooting

### OCR Not Working
**Problem**: "Warning: OCR libraries not available"

**Solution**:
```bash
# Install Tesseract OCR (see Installation section)
# Then reinstall Python packages
pip install --upgrade pytesseract opencv-python
```

### NumPy Compatibility Error
**Problem**: "AttributeError: _ARRAY_API not found"

**Solution**:
```bash
pip install "numpy<2"
```

### PDF Not Displaying
**Problem**: Blank screen after upload

**Solutions**:
- Check browser console for errors (F12)
- Ensure PDF is not corrupted
- Try a different PDF file
- Clear browser cache

### Text Edits Not Saving
**Problem**: Changes disappear after editing

**Solutions**:
- Wait for "Updating PDF..." message to complete
- Check terminal for error messages
- Ensure sufficient disk space
- Verify write permissions in project directory

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PyMuPDF](https://pymupdf.readthedocs.io/) - Excellent PDF manipulation library
- [PDF.js](https://mozilla.github.io/pdf.js/) - Mozilla's PDF rendering engine
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Powerful OCR engine
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

**Made with ❤️ by Talha Abbas**
