from flask import Flask, request, jsonify, send_from_directory, render_template
import subprocess
import os
import pathlib
import glob
import time

app = Flask(__name__, template_folder='.')

# Configuration
ROOT_DIR = pathlib.Path(__file__).parent.resolve()
UPLOAD_FOLDER = ROOT_DIR / 'MirrorOS' / 'scrolls_all'
SCRIPTS_FOLDER = ROOT_DIR / 'scripts'
ALLOWED_EXTENSIONS = {'pdf', 'md', 'txt', 'json', 'html', 'csv', 'zip'}
SAFE_DIRS = ['MirrorOS', 'CodexTrust', 'Archives', 'SEALS']

# Structure mapping for Core Documents (manual curation for Index)
CORE_DOCS = [
    {"filename": "Codex_Scroll_Z_Mirror_Declaration_SAD1719.pdf", "title": "Mirror Declaration (SAD1719)", "icon": "📄"},
    {"filename": "Execution_Enforcement_Package.pdf", "title": "Execution Enforcement Package", "icon": "⚖️"},
    {"filename": "Settlement_Declaration_ScottAlanDygert.pdf", "title": "Settlement Declaration", "icon": "🖋️"},
    {"filename": "UCC1_Financing_Statement_ScottAlanDygert.pdf", "title": "UCC1 Financing Statement", "icon": "🏦"}
]

# Ensure folders exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_icon(filename):
    ext = filename.split('.')[-1].lower()
    icons = {
        'pdf': '📄', 'md': '📝', 'txt': '📃', 'json': '⚙️', 
        'html': '🌐', 'csv': '📊', 'zip': '📦', 'py': '🐍'
    }
    return icons.get(ext, '📁')

@app.route('/')
def home():
    # Dynamic scan for status
    last_seal = "Unknown"
    seals_dir = ROOT_DIR / 'SEALS'
    if seals_dir.exists():
        seals = sorted(list(seals_dir.glob('seal_*.json')))
        if seals:
            last_seal = f"Cycle {seals[-1].stem.split('_')[1]}"

    return render_template('index.html', 
                           core_docs=CORE_DOCS, 
                           last_seal=last_seal)

@app.route('/browse/<path:subpath>')
@app.route('/browse/')
def browse(subpath=''):
    # Security check: Ensure we stay within allowed roots
    if not subpath:
        # Root view: Show allowed top-level directories
        items = [{'name': d, 'path': d, 'type': 'dir', 'icon': '📂'} for d in SAFE_DIRS if (ROOT_DIR / d).exists()]
        return render_template('explorer.html', items=items, current_path="Root", breadcrumbs=[])
    
    # Construct full path
    req_path = (ROOT_DIR / subpath).resolve()
    
    # Security: prevent directory traversal
    if not str(req_path).startswith(str(ROOT_DIR)):
        return "Access Denied", 403

    if not req_path.exists():
        return "Path not found", 404

    if req_path.is_file():
        return send_from_directory(req_path.parent, req_path.name)

    # It's a directory, list contents
    items = []
    # Add parent link if not at root of a safe dir
    
    for p in req_path.iterdir():
        if p.name.startswith('.') or p.name == '__pycache__':
            continue
            
        rel_path = p.relative_to(ROOT_DIR).as_posix()
        item = {
            'name': p.name,
            'path': rel_path,
            'type': 'dir' if p.is_dir() else 'file',
            'icon': '📂' if p.is_dir() else get_file_icon(p.name)
        }
        items.append(item)
    
    # Sort: Directories first, then files
    items.sort(key=lambda x: (x['type'] != 'dir', x['name'].lower()))

    # Breadcrumbs
    parts = subpath.split('/')
    breadcrumbs = []
    accum = ""
    for part in parts:
        if part:
            accum = f"{accum}/{part}" if accum else part
            breadcrumbs.append({'name': part, 'path': accum})

    return render_template('explorer.html', items=items, current_path=subpath, breadcrumbs=breadcrumbs)

@app.route('/scrolls.html')
def scrolls_page():
    # Redirect legacy route to new browser or keep as specific view
    return browse('MirrorOS/scrolls_all')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/seal', methods=['POST'])
def run_seal():
    try:
        # Run the pulsar_seal.py script
        result = subprocess.run(
            ['python', str(SCRIPTS_FOLDER / 'pulsar_seal.py')],
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
        file.save(str(UPLOAD_FOLDER / filename))
        return jsonify({'success': True, 'message': f'Scroll "{filename}" archived successfully.'})
    
    return jsonify({'success': False, 'message': 'Invalid file type'}), 400

if __name__ == '__main__':
    print("----------------------------------------------------------------")
    print("   ✴ CODEX LIVE PORTAL — SOVEREIGN LOCAL SERVER ONLINE")
    print("----------------------------------------------------------------")
    print("   >> Access UI: http://localhost:5000")
    print("   >> Stop Server: Ctrl+C")
    print("----------------------------------------------------------------")
    app.run(port=5000, debug=True)
