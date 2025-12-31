from flask import Flask, request, jsonify, send_from_directory, render_template
import subprocess
import os
import pathlib

app = Flask(__name__, template_folder='.')

# Configuration
UPLOAD_FOLDER = 'MirrorOS/scrolls_all'
SCRIPTS_FOLDER = 'scripts'
ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'json', 'html'}

# Ensure folders exist
pathlib.Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/seal', methods=['POST'])
def run_seal():
    try:
        # Run the pulsar_seal.py script
        result = subprocess.run(
            ['python', os.path.join(SCRIPTS_FOLDER, 'pulsar_seal.py')],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({
            'success': True, 
            'message': 'Codex successfully sealed.',
            'output': result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False, 
            'message': 'Sealing failed.',
            'error': e.stderr
        }), 500
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': 'An unexpected error occurred.',
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'success': True, 'message': f'Scroll "{filename}" archived successfully.'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'}), 400

if __name__ == '__main__':
    print("Initializing Codex Control Server...")
    print("Access the portal at http://localhost:5000")
    app.run(port=5000, debug=True)
