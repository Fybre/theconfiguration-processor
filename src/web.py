"""Flask web interface for Therefore Configuration Processor."""

from flask import Flask, request, render_template_string, Response, send_file
from io import BytesIO
from . import __version__
from .parser.config_parser import ConfigurationParser
from .generator.html_generator import HTMLGenerator
from .differ.comparator import DiffComparator
from .differ.diff_generator import DiffHTMLGenerator

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
            max-width: 600px;
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

        /* Mode tabs */
        .mode-tabs {
            display: flex;
            margin-bottom: 24px;
            border-radius: 8px;
            overflow: hidden;
            border: 2px solid #667eea;
        }
        .mode-tab {
            flex: 1;
            padding: 12px 20px;
            border: none;
            background: white;
            color: #667eea;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .mode-tab:hover {
            background: #f0f4ff;
        }
        .mode-tab.active {
            background: #667eea;
            color: white;
        }

        /* Upload areas */
        .upload-area {
            border: 2px dashed #cbd5e0;
            border-radius: 12px;
            padding: 30px 20px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .upload-area:hover, .upload-area.dragover {
            border-color: #667eea;
            background: #f7fafc;
        }
        .upload-icon {
            font-size: 36px;
            margin-bottom: 12px;
        }
        .upload-text {
            color: #4a5568;
            margin-bottom: 8px;
            font-size: 0.95rem;
        }
        .upload-hint {
            color: #a0aec0;
            font-size: 0.85rem;
        }
        .upload-label {
            display: block;
            text-align: left;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 8px;
            font-size: 0.9rem;
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

        /* Compare mode styling */
        .compare-section {
            display: none;
        }
        .compare-section.active {
            display: block;
        }
        .compare-files {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }
        .compare-file {
            text-align: left;
        }
        .compare-arrow {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: #667eea;
            margin-bottom: 16px;
        }

        button[type="submit"] {
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
        button[type="submit"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -10px rgba(102, 126, 234, 0.5);
        }
        button[type="submit"]:disabled {
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
        .version {
            margin-top: 24px;
            font-size: 0.75rem;
            color: #a0aec0;
        }

        @media (max-width: 500px) {
            .compare-files {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Therefore Configuration Processor</h1>
        <p class="subtitle">Generate documentation or compare Therefore configuration exports</p>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <div class="mode-tabs">
            <button type="button" class="mode-tab active" data-mode="generate">Generate Docs</button>
            <button type="button" class="mode-tab" data-mode="compare">Compare</button>
        </div>

        <!-- Generate Documentation Mode -->
        <form method="post" action="/" enctype="multipart/form-data" id="generateForm" class="compare-section active">
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

        <!-- Compare Mode -->
        <form method="post" action="/compare" enctype="multipart/form-data" id="compareForm" class="compare-section">
            <div class="compare-files">
                <div class="compare-file">
                    <label class="upload-label">Before (older config)</label>
                    <div class="upload-area upload-area-a" id="uploadAreaA">
                        <div class="upload-icon">📄</div>
                        <p class="upload-text">Configuration A</p>
                        <p class="upload-hint">Original/before</p>
                    </div>
                    <input type="file" name="file_a" id="fileInputA" accept=".xml">
                </div>
                <div class="compare-file">
                    <label class="upload-label">After (newer config)</label>
                    <div class="upload-area upload-area-b" id="uploadAreaB">
                        <div class="upload-icon">📄</div>
                        <p class="upload-text">Configuration B</p>
                        <p class="upload-hint">New/after</p>
                    </div>
                    <input type="file" name="file_b" id="fileInputB" accept=".xml">
                </div>
            </div>

            <button type="submit" id="compareBtn" disabled>
                <span class="btn-text">Compare Configurations</span>
                <span class="loading" id="loadingCompare">
                    <span class="spinner"></span>
                    Comparing...
                </span>
            </button>
        </form>

        <p class="version">v{{ version }}</p>
    </div>

    <script>
        // Mode switching
        const modeTabs = document.querySelectorAll('.mode-tab');
        const generateForm = document.getElementById('generateForm');
        const compareForm = document.getElementById('compareForm');

        modeTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                modeTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                const mode = tab.dataset.mode;
                if (mode === 'generate') {
                    generateForm.classList.add('active');
                    compareForm.classList.remove('active');
                } else {
                    generateForm.classList.remove('active');
                    compareForm.classList.add('active');
                }
            });
        });

        // Generate mode file handling
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const submitBtn = document.getElementById('submitBtn');
        const btnText = document.querySelector('#generateForm .btn-text');
        const loading = document.getElementById('loading');

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
                updateFileDisplay(uploadArea, fileInput);
                updateGenerateButton();
            }
        });

        fileInput.addEventListener('change', () => {
            updateFileDisplay(uploadArea, fileInput);
            updateGenerateButton();
        });

        function updateFileDisplay(area, input) {
            if (input.files.length) {
                const fileName = input.files[0].name;
                area.classList.add('file-selected');
                area.innerHTML = `
                    <div class="upload-icon">✅</div>
                    <p class="file-name">${fileName}</p>
                `;
            }
        }

        function updateGenerateButton() {
            submitBtn.disabled = !fileInput.files.length;
        }

        generateForm.addEventListener('submit', () => {
            btnText.style.display = 'none';
            loading.classList.add('active');
            submitBtn.disabled = true;
        });

        // Compare mode file handling
        const uploadAreaA = document.getElementById('uploadAreaA');
        const uploadAreaB = document.getElementById('uploadAreaB');
        const fileInputA = document.getElementById('fileInputA');
        const fileInputB = document.getElementById('fileInputB');
        const compareBtn = document.getElementById('compareBtn');
        const compareBtnText = document.querySelector('#compareForm .btn-text');
        const loadingCompare = document.getElementById('loadingCompare');

        function setupUploadArea(area, input, otherInput) {
            area.addEventListener('click', () => input.click());

            area.addEventListener('dragover', (e) => {
                e.preventDefault();
                area.classList.add('dragover');
            });

            area.addEventListener('dragleave', () => {
                area.classList.remove('dragover');
            });

            area.addEventListener('drop', (e) => {
                e.preventDefault();
                area.classList.remove('dragover');
                if (e.dataTransfer.files.length) {
                    input.files = e.dataTransfer.files;
                    updateFileDisplay(area, input);
                    updateCompareButton();
                }
            });

            input.addEventListener('change', () => {
                updateFileDisplay(area, input);
                updateCompareButton();
            });
        }

        setupUploadArea(uploadAreaA, fileInputA, fileInputB);
        setupUploadArea(uploadAreaB, fileInputB, fileInputA);

        function updateCompareButton() {
            compareBtn.disabled = !(fileInputA.files.length && fileInputB.files.length);
        }

        compareForm.addEventListener('submit', () => {
            compareBtnText.style.display = 'none';
            loadingCompare.classList.add('active');
            compareBtn.disabled = true;
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
        .version {
            font-size: 0.7rem;
            opacity: 0.7;
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
            <span class="version">v{{ version }}</span>
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

COMPARE_RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Comparison - Therefore Configuration Processor</title>
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
        .summary-bar {
            background: white;
            padding: 16px 24px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            gap: 24px;
            flex-wrap: wrap;
            align-items: center;
        }
        .summary-stat {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }
        .summary-stat.added { color: #22c55e; }
        .summary-stat.removed { color: #ef4444; }
        .summary-stat.modified { color: #f59e0b; }
        .version {
            font-size: 0.7rem;
            opacity: 0.7;
        }
        .iframe-container {
            height: calc(100vh - 110px);
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
        <h1>Configuration Comparison</h1>
        <div class="header-actions">
            <a href="/download-diff" class="btn btn-primary">
                <span>⬇️</span> Download HTML
            </a>
            <a href="/" class="btn btn-secondary">
                <span>📄</span> New Comparison
            </a>
            <span class="version">v{{ version }}</span>
        </div>
    </div>
    <div class="summary-bar">
        <span>{{ file_a }} vs {{ file_b }}</span>
        <span class="summary-stat added">+{{ added }} added</span>
        <span class="summary-stat removed">-{{ removed }} removed</span>
        <span class="summary-stat modified">~{{ modified }} modified</span>
    </div>
    <div class="iframe-container">
        <iframe src="/preview-diff" title="Comparison Preview"></iframe>
    </div>
</body>
</html>
"""

# Store the last generated HTML for download
_last_generated_html = None
_last_generated_title = "documentation"
_last_diff_html = None
_last_diff_title = "comparison"


@app.route('/', methods=['GET', 'POST'])
def upload():
    """Handle file upload and display results."""
    global _last_generated_html, _last_generated_title

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(UPLOAD_PAGE, error="No file selected", version=__version__)

        file = request.files['file']
        if file.filename == '':
            return render_template_string(UPLOAD_PAGE, error="No file selected", version=__version__)

        if not file.filename.lower().endswith('.xml'):
            return render_template_string(UPLOAD_PAGE, error="Please upload an XML file", version=__version__)

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

            return render_template_string(RESULT_PAGE, title=title, stats=stats, version=__version__)

        except Exception as e:
            return render_template_string(UPLOAD_PAGE, error=f"Error processing file: {str(e)}", version=__version__)

    return render_template_string(UPLOAD_PAGE, error=None, version=__version__)


@app.route('/compare', methods=['POST'])
def compare():
    """Handle comparison of two configuration files."""
    global _last_diff_html, _last_diff_title

    # Check for both files
    if 'file_a' not in request.files or 'file_b' not in request.files:
        return render_template_string(UPLOAD_PAGE, error="Please upload both configuration files", version=__version__)

    file_a = request.files['file_a']
    file_b = request.files['file_b']

    if file_a.filename == '' or file_b.filename == '':
        return render_template_string(UPLOAD_PAGE, error="Please upload both configuration files", version=__version__)

    if not file_a.filename.lower().endswith('.xml') or not file_b.filename.lower().endswith('.xml'):
        return render_template_string(UPLOAD_PAGE, error="Both files must be XML files", version=__version__)

    try:
        # Parse both XML files
        parser = ConfigurationParser()

        xml_content_a = file_a.read().decode('utf-8')
        config_a = parser.parse_string(xml_content_a)

        xml_content_b = file_b.read().decode('utf-8')
        config_b = parser.parse_string(xml_content_b)

        # Compare configurations
        comparator = DiffComparator()
        diff_result = comparator.compare(
            config_a, config_b,
            file_a_name=file_a.filename,
            file_b_name=file_b.filename
        )

        # Generate diff HTML
        diff_generator = DiffHTMLGenerator(diff_result)
        diff_html = diff_generator.generate()

        # Store for download
        _last_diff_html = diff_html
        _last_diff_title = f"comparison_{file_a.filename.replace('.xml', '')}_vs_{file_b.filename.replace('.xml', '')}"

        # Calculate summary stats
        total_added = sum(s.added for s in diff_result.summary.values())
        total_removed = sum(s.removed for s in diff_result.summary.values())
        total_modified = sum(s.modified for s in diff_result.summary.values())

        return render_template_string(
            COMPARE_RESULT_PAGE,
            file_a=file_a.filename,
            file_b=file_b.filename,
            added=total_added,
            removed=total_removed,
            modified=total_modified,
            version=__version__
        )

    except Exception as e:
        return render_template_string(UPLOAD_PAGE, error=f"Error comparing files: {str(e)}", version=__version__)


@app.route('/preview')
def preview():
    """Return the generated HTML for iframe preview."""
    global _last_generated_html
    if _last_generated_html:
        return Response(_last_generated_html, mimetype='text/html')
    return "No documentation generated yet", 404


@app.route('/preview-diff')
def preview_diff():
    """Return the generated diff HTML for iframe preview."""
    global _last_diff_html
    if _last_diff_html:
        return Response(_last_diff_html, mimetype='text/html')
    return "No comparison generated yet", 404


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


@app.route('/download-diff')
def download_diff():
    """Download the generated diff HTML file."""
    global _last_diff_html, _last_diff_title
    if _last_diff_html:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{_last_diff_title}_{timestamp}.html"
        buffer = BytesIO(_last_diff_html.encode('utf-8'))
        return send_file(
            buffer,
            mimetype='text/html',
            as_attachment=True,
            download_name=filename
        )
    return "No comparison generated yet", 404


def main():
    """Run the web server."""
    print("Starting Therefore Configuration Processor Web Server...")
    print("Open http://localhost:5050 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5050)


if __name__ == '__main__':
    main()
