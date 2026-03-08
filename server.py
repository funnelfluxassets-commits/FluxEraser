from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import subprocess
import uuid
import base64
import sys
import shutil
from PIL import Image

# HARD-CODED ABSOLUTE PATHS TO PREVENT ANY MAC OS VOLUME ISSUES
BASE_DIR = "/Volumes/WDB-2TB-B/App Projects/FluxEraser"
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'inputs')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

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
        
        # THRUMBNAIL FORCE Fix: Hard-coding extension to .jpg for Mac Finder compatibility
        output_filename = f"ai_pure_{file_id}.jpg"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        # 1. Save inputs
        image_file.save(input_path)
        header, encoded = mask_data.split(",", 1)
        with open(mask_path, "wb") as f:
            f.write(base64.b64decode(encoded))

        # 2. RUN AI ENGINE (LaMa)
        print(f"--- [AI] Purifying with LaMa: {output_filename} ---")
        temp_out_dir = os.path.join(OUTPUT_FOLDER, f"tmp_{file_id}")
        os.makedirs(temp_out_dir, exist_ok=True)
        
        cmd = [sys.executable, '-m', 'iopaint', 'run', '--model=lama', '--image', input_path, '--mask', mask_path, '--output', temp_out_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"AI Engine ERROR: {result.stderr}")
            return jsonify({"error": f"AI Engine Failed: {result.stderr}"}), 500

        # Find the result file and Standardize it for Mac Thumbnails
        contents = os.listdir(temp_out_dir)
        result_name = os.path.basename(input_path)
        actual_result_path = os.path.join(temp_out_dir, result_name)
        
        if not os.path.exists(actual_result_path) and len(contents) > 0:
            actual_result_path = os.path.join(temp_out_dir, contents[0])

        if os.path.exists(actual_result_path):
            try:
                # RE-ENCODING FOR THUMBNAIL VISIBILITY
                with Image.open(actual_result_path) as img:
                    rgb_img = img.convert('RGB')
                    rgb_img.save(output_path, 'JPEG', quality=95, subsampling=0)
                shutil.rmtree(temp_out_dir)
            except Exception as e:
                print(f"Standardization Error: {e}")
                shutil.move(actual_result_path, output_path)
                shutil.rmtree(temp_out_dir)
        else:
            return jsonify({"error": "Engine finished but final image not synthesized."}), 500

        print(f"--- THUMBNAIL FORCE READY: {output_filename} ---")
        return jsonify({
            "status": "success",
            "final_file_name": output_filename
        })
        
    except Exception as e:
        print(f"Generic Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/outputs/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__':
    print("🚀 FluxEraser THUMBNAIL-FORCE running on http://127.0.0.1:5055")
    app.run(port=5055, debug=True)
