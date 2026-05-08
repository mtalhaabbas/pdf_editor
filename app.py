from flask import Flask, request, send_file, render_template, jsonify
from pdf_editor import PDFEditor
import os
from werkzeug.utils import secure_filename
import base64
import tempfile
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

editors = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    editor = PDFEditor(filepath)
    editors[filename] = editor
    
    return jsonify({
        'filename': filename,
        'page_count': editor.get_page_count()
    })

@app.route('/page/<filename>/<int:page_num>')
def get_page(filename, page_num):
    if filename not in editors:
        return jsonify({'error': 'File not found'}), 404
    
    editor = editors[filename]
    text_elements = editor.get_page_text_elements(page_num)
    
    return jsonify({
        'text_elements': text_elements
    })

@app.route('/get_pdf/<filename>')
def get_pdf(filename):
    if filename not in editors:
        return jsonify({'error': 'File not found'}), 404
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, mimetype='application/pdf')

@app.route('/edit', methods=['POST'])
def edit_text():
    try:
        data = request.json
        filename = data['filename']
        page_num = data['page_num']
        element_index = data['element_index']
        new_text = data['new_text']
        
        if filename not in editors:
            return jsonify({'error': 'File not found'}), 404
        
        editor = editors[filename]
        
        # Get the original text element to preserve its properties
        text_elements = editor.get_page_text_elements(page_num)
        if element_index >= len(text_elements):
            return jsonify({'error': 'Invalid element index'}), 400
        
        element = text_elements[element_index]
        
        print(f"Editing element: {element['text']} -> {new_text}")
        print(f"Font: {element['font']}, Size: {element['size']}, Color: {element['color']}")
        print(f"Type: {element.get('type', 'text')}")
        
        # Replace text with exact same formatting
        success = editor.replace_text_at_bbox(
            page_num,
            element['bbox'],
            element['text'],
            new_text,
            element['font'],
            element['size'],
            element['color'],
            element['flags'],
            element['origin'],
            element.get('type', 'text')
        )
        
        if success:
            # Save to a temporary file first
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
            os.close(temp_fd)
            
            try:
                editor.save(temp_path)
                editor.close()
                
                # Replace the original file with the temp file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                shutil.move(temp_path, filepath)
                
                print(f"PDF saved successfully to {filepath}")
                
                # Reload the editor with updated PDF
                editors[filename] = PDFEditor(filepath)
                
                print(f"Editor reloaded, new text elements count: {len(editors[filename].get_page_text_elements(page_num))}")
                
                return jsonify({'success': True})
            except Exception as save_error:
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise save_error
        
        return jsonify({'error': 'Text replacement failed'}), 400
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in edit_text: {error_trace}")
        return jsonify({'error': str(e), 'trace': error_trace}), 500

@app.route('/download/<filename>')
def download(filename):
    if filename not in editors:
        return jsonify({'error': 'File not found'}), 404
    
    # The edited file is in the uploads folder (we save changes there)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Download with a new name to indicate it's edited
    download_name = f"edited_{filename}"
    return send_file(filepath, as_attachment=True, download_name=download_name)

if __name__ == '__main__':
    app.run(debug=True, port=5000)