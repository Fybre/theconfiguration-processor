"""Flask web interface for Therefore Configuration Processor."""

from flask import Flask, request, render_template_string, Response, send_file
from io import BytesIO
from .parser.config_parser import ConfigurationParser
from .generator.html_generator import HTMLGenerator

app = Flask(__name__)

# Maximum file size: 50MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

UPLOAD_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Therefore Configuration Processor</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        h1 {
            color: #1a202c;
            margin-bottom: 8px;
            font-size: 1.75rem;
        }
        .subtitle {
            color: #718096;
            margin-bottom: 32px;
            font-size: 0.95rem;
        }
        .upload-area {
            border: 2px dashed #cbd5e0;
            border-radius: 12px;
            padding: 40px 20px;
            margin-bottom: 24px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .upload-area:hover, .upload-area.dragover {
            border-color: #667eea;
            background: #f7fafc;
        }
        .upload-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        .upload-text {
            color: #4a5568;
            margin-bottom: 8px;
        }
        .upload-hint {
            color: #a0aec0;
            font-size: 0.85rem;
        }
        input[type="file"] {
            display: none;
        }
        .file-selected {
            background: #f0fff4;
            border-color: #48bb78;
            padding: 20px;
        }
        .file-selected .file-name {
            color: #2f855a;
            font-weight: 500;
            word-break: break-all;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 32px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -10px rgba(102, 126, 234, 0.5);
        }
        button:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .error {
            background: #fff5f5;
            color: #c53030;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 0.9rem;
        }
        .loading {
            display: none;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .loading.active {
            display: flex;
        }
        .spinner {
            width: 20px;
            height: 20px;
            border: 3px solid #e2e8f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Therefore Configuration Processor</h1>
        <p class="subtitle">Generate HTML documentation from Therefore configuration exports</p>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <form method="post" enctype="multipart/form-data" id="uploadForm">
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📄</div>
                <p class="upload-text">Drop your XML file here or click to browse</p>
                <p class="upload-hint">TheConfiguration.xml export from Therefore</p>
            </div>
            <input type="file" name="file" id="fileInput" accept=".xml">

            <button type="submit" id="submitBtn" disabled>
                <span class="btn-text">Generate Documentation</span>
                <span class="loading" id="loading">
                    <span class="spinner"></span>
                    Processing...
                </span>
            </button>
        </form>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const submitBtn = document.getElementById('submitBtn');
        const btnText = document.querySelector('.btn-text');
        const loading = document.getElementById('loading');
        const form = document.getElementById('uploadForm');

        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileDisplay();
            }
        });

        fileInput.addEventListener('change', updateFileDisplay);

        function updateFileDisplay() {
            if (fileInput.files.length) {
                const fileName = fileInput.files[0].name;
                uploadArea.classList.add('file-selected');
                uploadArea.innerHTML = `
                    <div class="upload-icon">✅</div>
                    <p class="file-name">${fileName}</p>
                `;
                submitBtn.disabled = false;
            }
        }

        form.addEventListener('submit', () => {
            btnText.style.display = 'none';
            loading.classList.add('active');
            submitBtn.disabled = true;
        });
    </script>
</body>
</html>
"""

RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation Generated - Therefore Configuration Processor</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f7fafc;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
        }
        .header h1 {
            font-size: 1.25rem;
            font-weight: 600;
        }
        .header-actions {
            display: flex;
            gap: 12px;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 0.9rem;
            font-weight: 500;
            text-decoration: none;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }
        .btn-primary {
            background: white;
            color: #667eea;
        }
        .btn-primary:hover {
            background: #f0f0f0;
        }
        .btn-secondary {
            background: rgba(255,255,255,0.2);
            color: white;
        }
        .btn-secondary:hover {
            background: rgba(255,255,255,0.3);
        }
        .stats {
            background: white;
            padding: 16px 24px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
        }
        .stat {
            display: flex;
            align-items: baseline;
            gap: 6px;
        }
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }
        .stat-label {
            color: #718096;
            font-size: 0.85rem;
        }
        .iframe-container {
            height: calc(100vh - 130px);
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        <div class="header-actions">
            <a href="/download" class="btn btn-primary">
                <span>⬇️</span> Download HTML
            </a>
            <a href="/" class="btn btn-secondary">
                <span>📄</span> New File
            </a>
        </div>
    </div>
    <div class="stats">
        {% for label, value in stats %}
        {% if value > 0 %}
        <div class="stat">
            <span class="stat-value">{{ value }}</span>
            <span class="stat-label">{{ label }}</span>
        </div>
        {% endif %}
        {% endfor %}
    </div>
    <div class="iframe-container">
        <iframe src="/preview" title="Documentation Preview"></iframe>
    </div>
</body>
</html>
"""

# Store the last generated HTML for download
_last_generated_html = None
_last_generated_title = "documentation"


@app.route('/', methods=['GET', 'POST'])
def upload():
    """Handle file upload and display results."""
    global _last_generated_html, _last_generated_title

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(UPLOAD_PAGE, error="No file selected")

        file = request.files['file']
        if file.filename == '':
            return render_template_string(UPLOAD_PAGE, error="No file selected")

        if not file.filename.lower().endswith('.xml'):
            return render_template_string(UPLOAD_PAGE, error="Please upload an XML file")

        try:
            # Parse the XML
            xml_content = file.read().decode('utf-8')
            parser = ConfigurationParser()
            config = parser.parse_string(xml_content)

            # Generate HTML
            title = file.filename.replace('.xml', '').replace('_', ' ').title()
            generator = HTMLGenerator(config, title=title)
            html_content = generator.generate_string()

            # Store for download
            _last_generated_html = html_content
            _last_generated_title = file.filename.replace('.xml', '')

            # Get stats for display
            stats_dict = config.get_statistics()
            stats = [
                ("Categories", stats_dict.get("categories", 0)),
                ("Fields", stats_dict.get("fields", 0)),
                ("Workflows", stats_dict.get("workflows", 0)),
                ("Tasks", stats_dict.get("workflow_tasks", 0)),
                ("Folders", stats_dict.get("folders", 0)),
                ("Roles", stats_dict.get("roles", 0)),
                ("EForms", stats_dict.get("eforms", 0)),
                ("Dictionaries", stats_dict.get("keyword_dictionaries", 0)),
            ]

            return render_template_string(RESULT_PAGE, title=title, stats=stats)

        except Exception as e:
            return render_template_string(UPLOAD_PAGE, error=f"Error processing file: {str(e)}")

    return render_template_string(UPLOAD_PAGE, error=None)


@app.route('/preview')
def preview():
    """Return the generated HTML for iframe preview."""
    global _last_generated_html
    if _last_generated_html:
        return Response(_last_generated_html, mimetype='text/html')
    return "No documentation generated yet", 404


@app.route('/download')
def download():
    """Download the generated HTML file."""
    global _last_generated_html, _last_generated_title
    if _last_generated_html:
        from datetime import datetime
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{_last_generated_title}_documentation_{timestamp}.html"
        buffer = BytesIO(_last_generated_html.encode('utf-8'))
        return send_file(
            buffer,
            mimetype='text/html',
            as_attachment=True,
            download_name=filename
        )
    return "No documentation generated yet", 404


def main():
    """Run the web server."""
    print("Starting Therefore Configuration Processor Web Server...")
    print("Open http://localhost:5050 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5050)


if __name__ == '__main__':
    main()
