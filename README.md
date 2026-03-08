---
title: FluxEraser Brain
emoji: 🪄
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
---
# FluxEraser | Precision AI Watermark Removal

FluxEraser is a powerful, locally-hosted AI tool designed for ultra-precise watermark and object removal. It uses the state-of-the-art **LaMa (LArge Mask Inpainting)** model to synthesize realistic textures (even complex ones like swirly floors) instead of simply blurring them.

---

## 🚀 Quick Start

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Launch the AI Engine
Start the Flask backend server:
```bash
python3 server.py
```
The engine will run on `http://127.0.0.1:5055`.

### 3. Open the UI
Simply open `index.html` in your favorite browser.

---

## 🎨 Features
- **Dynamic Lens Cursor**: A professional circular cursor that scales with your brush size for pixel-perfect selections.
- **Dual-Mode Canvas**: Switch between **Brush** (Selection) and **Eraser** (Correction) for total control.
- **LaMa AI Integration**: Advanced texture synthesis that "purifies" the image rather than smudging it.
- **High-Quality Export**: One-click download with standardized headers to ensure macOS Finder thumbnails work perfectly.

---

## 🛠 Project Structure
- `index.html`: The premium, glassmorphic web interface.
- `server.py`: The Flask backend coordinating the AI engine on port 5055.
- `inputs/`: Temporary storage for uploaded images and masks (excluded from Git).
- `outputs/`: Where your purified results are locally saved (excluded from Git).

---

## ⚖️ License
Personal use only. Ensure you have the rights to modify images before removing watermarks.
