from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import uuid
import base64
import sys
import shutil
from PIL import Image

# 1. AUTO-DETECT ENVIRONMENT (Local vs Cloud)
# If we're on Hugging Face, we use relative paths. If on Mac, we use absolute.
IS_HF = "SPACE_ID" in os.environ
if IS_HF:
    BASE_DIR = os.getcwd() # Use the current app folder in the cloud
else:
    BASE_DIR = "/Volumes/WDB-2TB-B/App Projects/FluxEraser"

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'inputs')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app) # Enable Global Access

@app.route('/erase', methods=['POST'])
def erase_watermark():
    try:
        if 'image' not in request.files or 'mask' not in request.form:
            return jsonify({"error": "Missing image or mask data"}), 400
        
        image_file = request.files['image']
        mask_data = request.form['mask']
        
        file_id = str(uuid.uuid4())[:8]
        ext = os.path.splitext(image_file.filename)[1] or '.png'
        
        input_path = os.path.join(UPLOAD_FOLDER, f"brush_{file_id}{ext}")
        mask_path = os.path.join(UPLOAD_FOLDER, f"mask_{file_id}.png")
        
        # THUMBNAIL FORCE: Re-standardize everything to .jpg
        output_filename = f"ai_pure_{file_id}.jpg"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # 1. Save inputs
        image_file.save(input_path)
        header, encoded = mask_data.split(",", 1)
        with open(mask_path, "wb") as f:
            f.write(base64.b64decode(encoded))

        # 2. RUN AI ENGINE (LaMa)
        print(f"🌍 [Cloud-AI] Purifying: {output_filename}...")
        temp_out_dir = os.path.join(OUTPUT_FOLDER, f"tmp_{file_id}")
        os.makedirs(temp_out_dir, exist_ok=True)
        
        # Detect if we need 'python3' or 'python'
        py_cmd = sys.executable
        cmd = [py_cmd, '-m', 'iopaint', 'run', '--model=lama', '--image', input_path, '--mask', mask_path, '--output', temp_out_dir]
        
        # For Hugging Face, we might need --device cpu if no GPU
        if IS_HF:
            cmd.append('--device=cpu')

        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"AI ERROR: {result.stderr}")
            return jsonify({"error": f"AI Engine Failed: {result.stderr}"}), 500

        # 3. Retrieve and Normalize for Mac Thumbnails
        contents = os.listdir(temp_out_dir)
        result_name = os.path.basename(input_path)
        actual_result_path = os.path.join(temp_out_dir, result_name)
        
        if not os.path.exists(actual_result_path) and len(contents) > 0:
            actual_result_path = os.path.join(temp_out_dir, contents[0])

        if os.path.exists(actual_result_path):
            try:
                # Open and Re-save to standardize headers
                with Image.open(actual_result_path) as img:
                    rgb_img = img.convert('RGB')
                    rgb_img.save(output_path, 'JPEG', quality=95, subsampling=0)
                shutil.rmtree(temp_out_dir)
            except Exception as e:
                shutil.move(actual_result_path, output_path)
                shutil.rmtree(temp_out_dir)
        else:
            return jsonify({"error": "Synthesis check failed."}), 500

        return jsonify({
            "status": "success",
            "final_file_name": output_filename
        })
        
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/outputs/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route('/')
def home():
    return "🚀 FluxEraser ULTRA-AI Cloud Engine is ONLINE."

if __name__ == '__main__':
    # Use environment variables for Port (Hugging Face requirement)
    port = int(os.environ.get("PORT", 7860))
    print(f"🚀 FluxEraser Global Brain running on Port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
