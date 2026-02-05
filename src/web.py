"""Flask web interface for Therefore Configuration Processor."""

from flask import Flask, request, render_template_string, Response, send_file, jsonify, session, stream_with_context
from io import BytesIO
import os
import tempfile
import uuid
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from . import __version__
from .parser.config_parser import ConfigurationParser
from .generator.html_generator import HTMLGenerator
from .differ.comparator import DiffComparator
from .differ.diff_generator import DiffHTMLGenerator
from .progress_tracker import progress_tracker

# Load .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)  # Override system env vars with .env file
        print(f"Loaded .env from: {env_path}")
except ImportError:
    print("Warning: python-dotenv not installed, environment variables from .env will not be loaded")
    pass

# Import AI module with graceful degradation
try:
    from .ai import LLMConfig, AISummaryGenerator, AI_AVAILABLE
except ImportError:
    AI_AVAILABLE = False
    LLMConfig = None
    AISummaryGenerator = None

# Load multiple LLM configurations with fallback support
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.4'))
LLM_CONFIGS = []

# Try to load numbered LLM configs (LLM_1_, LLM_2_, etc.)
for i in range(1, 10):  # Support up to 9 LLMs
    base_url = os.getenv(f'LLM_{i}_BASE_URL')
    if base_url:
        model_name = os.getenv(f'LLM_{i}_MODEL_NAME', 'gpt-4')
        api_key = os.getenv(f'LLM_{i}_API_KEY', 'not-needed')

        if AI_AVAILABLE and LLMConfig:
            config = LLMConfig(
                base_url=base_url,
                model_name=model_name,
                api_key=api_key,
                temperature=LLM_TEMPERATURE
            )
            LLM_CONFIGS.append(config)
            print(f"Loaded LLM config #{i}: {base_url}")

AI_CONFIGURED = bool(LLM_CONFIGS and AI_AVAILABLE)


# Job manager for async processing
class JobManager:
    """Manages background processing jobs."""

    def __init__(self):
        self._jobs: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def create_job(self, job_id: str) -> None:
        """Create a new job."""
        with self._lock:
            self._jobs[job_id] = {
                'status': 'processing',
                'progress': 0,
                'total': 0,
                'current': '',
                'result': None,
                'error': None,
                'created_at': datetime.now(),
                'filename': None
            }

    def update_progress(self, job_id: str, completed: int, total: int, current: str) -> None:
        """Update job progress."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update({
                    'progress': completed,
                    'total': total,
                    'current': current
                })

    def complete_job(self, job_id: str, result: bytes, filename: str) -> None:
        """Mark job as completed."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update({
                    'status': 'completed',
                    'result': result,
                    'filename': filename
                })

    def fail_job(self, job_id: str, error: str) -> None:
        """Mark job as failed."""
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update({
                    'status': 'failed',
                    'error': error
                })

    def get_job(self, job_id: str) -> Optional[dict]:
        """Get job status."""
        with self._lock:
            return self._jobs.get(job_id)

    def cleanup_old_jobs(self, max_age_hours: int = 24) -> None:
        """Remove jobs older than specified hours."""
        from datetime import timedelta
        with self._lock:
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            self._jobs = {
                jid: job for jid, job in self._jobs.items()
                if job['created_at'] > cutoff
            }


job_manager = JobManager()

app = Flask(__name__)

# Session configuration
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

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

        /* AI Generation Progress Bar */
        .progress-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.8);
            z-index: 10000;
            align-items: center;
            justify-content: center;
        }

        .progress-overlay.active {
            display: flex;
        }

        .progress-box {
            background: white;
            border-radius: 12px;
            padding: 40px;
            min-width: 500px;
            max-width: 600px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        }

        .progress-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 25px;
            text-align: center;
            color: #1a202c;
        }

        .progress-bar-container {
            background: #e2e8f0;
            height: 35px;
            border-radius: 17.5px;
            overflow: hidden;
            margin-bottom: 15px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }

        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 0.95rem;
        }

        .progress-status {
            text-align: center;
            color: #4a5568;
            font-size: 1rem;
            margin-top: 15px;
            font-weight: 500;
        }

        .progress-current-item {
            text-align: center;
            color: #718096;
            font-size: 0.85rem;
            margin-top: 8px;
            font-style: italic;
            min-height: 20px;
        }

        .progress-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid #e2e8f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
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
                <p class="upload-hint">Remember to export Role Assignments for full security information</p>
            </div>
            <input type="file" name="file" id="fileInput" accept=".xml">

            <!-- AI Summary Settings -->
            {% if ai_configured %}
            <div class="ai-settings" style="text-align: left; margin: 20px 0; padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px;">
                <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="checkbox" name="with_ai" id="withAI" style="display: inline-block; width: auto;">
                    <span style="font-weight: 600; color: white;">✨ Generate AI Summaries</span>
                </label>
                <p id="aiStatus" style="font-size: 0.8rem; color: rgba(255,255,255,0.9); margin: 8px 0 0 28px;">
                    <span class="ai-status-spinner" style="display: inline-block; width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite;"></span>
                    Checking AI server status...
                </p>
                <button type="button" id="clearCacheBtn" style="margin-top: 12px; padding: 8px 16px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 4px; cursor: pointer; font-size: 0.85rem;">
                    🗑️ Clear AI Cache
                </button>
                <p id="cacheStatus" style="font-size: 0.75rem; color: rgba(255,255,255,0.8); margin: 4px 0 0 0; display: none;"></p>
            </div>
            {% endif %}

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

    <!-- AI Generation Progress Overlay -->
    <div id="progressOverlay" class="progress-overlay">
        <div class="progress-box">
            <div class="progress-title">
                <span class="progress-spinner"></span>
                Generating AI Summaries
            </div>
            <div class="progress-bar-container">
                <div id="progressBar" class="progress-bar">0%</div>
            </div>
            <div id="progressStatus" class="progress-status">Initializing...</div>
            <div id="progressCurrentItem" class="progress-current-item"></div>
        </div>
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

        generateForm.addEventListener('submit', (e) => {
            // Always prevent default and use async processing
            e.preventDefault();

            const aiEnabled = document.getElementById('withAI')?.checked;

            if (aiEnabled) {
                // Show progress overlay for AI generation
                showProgressOverlay();
            } else {
                // Show progress overlay for non-AI generation too
                showProgressOverlay();
            }
        });

        async function showProgressOverlay() {
            const progressOverlay = document.getElementById('progressOverlay');
            const progressBar = document.getElementById('progressBar');
            const progressStatus = document.getElementById('progressStatus');
            const progressCurrentItem = document.getElementById('progressCurrentItem');

            // Generate tracker ID
            const trackerId = generateUUID();

            // Show progress overlay
            progressOverlay.classList.add('active');
            progressStatus.textContent = 'Starting processing...';
            progressCurrentItem.textContent = '';
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';

            try {
                // Create tracker on server first
                await fetch(`/create-tracker/${trackerId}`, { method: 'POST' });

                // Submit form
                const formData = new FormData(generateForm);
                formData.append('tracker_id', trackerId);

                progressStatus.textContent = 'Uploading file...';

                const uploadResponse = await fetch('/', {
                    method: 'POST',
                    body: formData
                });

                const uploadResult = await uploadResponse.json();

                if (!uploadResult.success) {
                    throw new Error(uploadResult.message || 'Upload failed');
                }

                const jobId = uploadResult.job_id;
                progressStatus.textContent = 'Processing started...';

                // Connect to SSE for progress updates
                const eventSource = new EventSource(`/ai-progress/${trackerId}`);

                eventSource.onmessage = (event) => {
                    const data = JSON.parse(event.data);

                    if (data.connected) {
                        return;
                    }

                    if (data.done) {
                        eventSource.close();
                    } else {
                        const percent = Math.round((data.completed / data.total) * 100);
                        progressBar.style.width = percent + '%';
                        progressBar.textContent = percent + '%';
                        progressStatus.textContent = `Processing ${data.completed} of ${data.total} items`;
                        progressCurrentItem.textContent = data.current;
                    }
                };

                eventSource.onerror = (error) => {
                    console.error('SSE connection error:', error);
                    eventSource.close();
                };

                // Poll for job completion
                const pollInterval = setInterval(async () => {
                    try {
                        const statusResponse = await fetch(`/job-status/${jobId}`);
                        const status = await statusResponse.json();

                        if (status.status === 'completed') {
                            clearInterval(pollInterval);
                            eventSource.close();
                            progressBar.style.width = '100%';
                            progressBar.textContent = '100%';
                            progressStatus.textContent = 'Complete! Downloading...';

                            // Download the result using fetch and blob
                            try {
                                const resultResponse = await fetch(`/job-result/${jobId}`);
                                const blob = await resultResponse.blob();
                                const filename = resultResponse.headers.get('Content-Disposition')
                                    ?.split('filename=')[1]
                                    ?.replace(/"/g, '') || 'documentation.html';

                                // Create download link and trigger it
                                const url = window.URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.style.display = 'none';
                                a.href = url;
                                a.download = filename;
                                document.body.appendChild(a);
                                a.click();
                                window.URL.revokeObjectURL(url);
                                document.body.removeChild(a);

                                progressStatus.textContent = 'Download complete!';

                                // Close overlay and reload page
                                setTimeout(() => {
                                    progressOverlay.classList.remove('active');
                                    window.location.reload();
                                }, 2000);
                            } catch (error) {
                                console.error('Download error:', error);
                                progressStatus.textContent = 'Download failed. Refreshing page...';
                                setTimeout(() => {
                                    progressOverlay.classList.remove('active');
                                    window.location.reload();
                                }, 2000);
                            }

                        } else if (status.status === 'failed') {
                            clearInterval(pollInterval);
                            eventSource.close();
                            progressOverlay.classList.remove('active');
                            alert('Processing failed: ' + (status.error || 'Unknown error'));
                        }
                    } catch (error) {
                        console.error('Status check error:', error);
                    }
                }, 1000); // Poll every second

            } catch (error) {
                console.error('Error:', error);
                progressOverlay.classList.remove('active');
                alert('Error: ' + error.message);
            }
        }

        function generateUUID() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c == 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }

        // Check AI server status on page load
        const aiStatus = document.getElementById('aiStatus');
        if (aiStatus) {
            fetch('/test-llm', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log('='.repeat(60));
                    console.log('AI Configuration:');
                    console.log('  Provider:', data.provider);
                    console.log('  Model:', data.model);
                    console.log('  Base URL:', data.base_url);
                    console.log('  Status:', data.success ? 'Online' : 'Offline');
                    console.log('='.repeat(60));

                    if (data.success) {
                        aiStatus.innerHTML = `✓ AI server online: ${data.provider} (${data.model})`;
                    } else {
                        aiStatus.innerHTML = '✗ AI server offline: ' + data.message;
                        aiStatus.style.color = 'rgba(255,200,200,0.9)';
                    }
                })
                .catch(error => {
                    console.error('AI test failed:', error);
                    aiStatus.innerHTML = '✗ AI server offline';
                    aiStatus.style.color = 'rgba(255,200,200,0.9)';
                });
        }

        // Clear AI cache button
        const clearCacheBtn = document.getElementById('clearCacheBtn');
        const cacheStatus = document.getElementById('cacheStatus');
        if (clearCacheBtn) {
            clearCacheBtn.addEventListener('click', () => {
                if (!confirm('Clear all cached AI summaries? This cannot be undone.')) {
                    return;
                }

                clearCacheBtn.disabled = true;
                clearCacheBtn.textContent = 'Clearing...';

                fetch('/clear-ai-cache', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            cacheStatus.innerHTML = `✓ ${data.message}`;
                            cacheStatus.style.color = 'rgba(144,238,144,1)';
                        } else {
                            cacheStatus.innerHTML = `✗ ${data.message}`;
                            cacheStatus.style.color = 'rgba(255,200,200,0.9)';
                        }
                        cacheStatus.style.display = 'block';

                        setTimeout(() => {
                            cacheStatus.style.display = 'none';
                        }, 5000);
                    })
                    .catch(error => {
                        cacheStatus.innerHTML = '✗ Failed to clear cache';
                        cacheStatus.style.color = 'rgba(255,200,200,0.9)';
                        cacheStatus.style.display = 'block';
                    })
                    .finally(() => {
                        clearCacheBtn.disabled = false;
                        clearCacheBtn.textContent = '🗑️ Clear AI Cache';
                    });
            });
        }

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

# Helper functions for storing generated HTML in temporary files
def save_html_to_temp(html_content: str, title: str) -> str:
    """Save HTML to temporary file and return file ID."""
    file_id = str(uuid.uuid4())
    temp_dir = Path(tempfile.gettempdir()) / 'therefore-processor'
    temp_dir.mkdir(exist_ok=True)

    temp_file = temp_dir / f"{file_id}.html"
    temp_file.write_text(html_content, encoding='utf-8')

    # Store metadata in session
    session[f'{file_id}_title'] = title

    return file_id

def get_html_from_temp(file_id: str) -> tuple:
    """Retrieve HTML from temporary file."""
    temp_dir = Path(tempfile.gettempdir()) / 'therefore-processor'
    temp_file = temp_dir / f"{file_id}.html"

    if temp_file.exists():
        html_content = temp_file.read_text(encoding='utf-8')
        title = session.get(f'{file_id}_title', 'documentation')
        return html_content, title
    return None, None


@app.route('/create-tracker/<tracker_id>', methods=['POST'])
def create_tracker(tracker_id):
    """Create a progress tracker before starting generation."""
    progress_tracker.create_tracker(tracker_id)
    return jsonify({'success': True, 'tracker_id': tracker_id})


@app.route('/ai-progress/<tracker_id>')
def ai_progress(tracker_id):
    """Stream AI generation progress via Server-Sent Events."""
    def generate():
        # Send initial connection confirmation
        yield f"data: {json.dumps({'connected': True})}\n\n"

        for update in progress_tracker.get_updates(tracker_id):
            if update.get('done'):
                yield f"data: {json.dumps({'done': True})}\n\n"
                break
            else:
                yield f"data: {json.dumps(update)}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/clear-ai-cache', methods=['POST'])
def clear_ai_cache():
    """Clear all cached AI summaries."""
    if not AI_AVAILABLE:
        return jsonify({'success': False, 'message': 'AI module not available'})

    try:
        from .ai.summary_generator import AISummaryGenerator
        count = AISummaryGenerator.clear_cache()
        return jsonify({
            'success': True,
            'message': f'Cleared {count} cached summary file(s)',
            'count': count
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@app.route('/test-llm', methods=['POST'])
def test_llm():
    """Test connection to all configured LLMs."""
    if not AI_CONFIGURED:
        return jsonify({
            'success': False,
            'message': 'AI not configured. Set LLM_1_BASE_URL and LLM_1_MODEL_NAME environment variables.'
        })

    try:
        print("=" * 60)
        print("Testing AI LLM Configurations:")
        print("=" * 60)

        llm_status = []
        at_least_one_working = False

        for i, config in enumerate(LLM_CONFIGS, 1):
            # Detect provider from base URL
            provider = "Unknown"
            if "azure.com" in config.base_url.lower():
                provider = "Azure OpenAI"
            elif "11434" in config.base_url or "ollama" in config.base_url.lower():
                provider = "Ollama"
            elif "localhost" in config.base_url or "127.0.0.1" in config.base_url:
                provider = "Local LLM"
            else:
                provider = f"Custom ({config.base_url.split('/')[2]})"

            print(f"\nLLM #{i} ({provider}):")
            print(f"  Base URL: {config.base_url}")
            print(f"  Model: {config.model_name}")
            print(f"  API Key: {'*' * 10 if config.api_key != 'not-needed' else 'not-needed'}")

            # Test connection
            from .ai.summary_generator import AISummaryGenerator
            generator = AISummaryGenerator(config)
            success, message = generator.test_connection()

            print(f"  Status: {'✓ Online' if success else '✗ Offline - ' + message}")

            llm_status.append({
                'priority': i,
                'provider': provider,
                'model': config.model_name,
                'base_url': config.base_url,
                'success': success,
                'message': message if not success else 'Online'
            })

            if success:
                at_least_one_working = True

        print("=" * 60)

        # Build response message
        if at_least_one_working:
            working_llms = [s for s in llm_status if s['success']]
            primary = working_llms[0]
            message = f"{primary['provider']} ({primary['model']})"
            if len(working_llms) > 1:
                message += f" + {len(working_llms) - 1} fallback(s)"
        else:
            message = "All LLMs offline"

        return jsonify({
            'success': at_least_one_working,
            'message': message,
            'llms': llm_status,
            'provider': llm_status[0]['provider'] if llm_status else 'None',
            'model': llm_status[0]['model'] if llm_status else 'None',
            'base_url': llm_status[0]['base_url'] if llm_status else 'None'
        })

    except Exception as e:
        print(f"AI test error: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


def process_file_async(job_id: str, xml_content: str, filename: str, with_ai: bool, tracker_id: str):
    """Process file in background thread."""
    try:
        # Parse the XML
        parser = ConfigurationParser()
        config = parser.parse_string(xml_content)

        # Check if AI summaries are requested
        ai_summaries = None
        if with_ai and AI_CONFIGURED:
            try:
                ai_generator = AISummaryGenerator(LLM_CONFIGS)

                # Try to load from cache first
                ai_summaries = ai_generator.load_from_cache(xml_content)

                if ai_summaries:
                    print("  Skipping generation - using cached summaries")
                else:
                    # Cache miss - generate new summaries in parallel
                    print("=" * 60)
                    print(f"Generating AI summaries (parallel) with {len(LLM_CONFIGS)} configured LLM(s)")
                    for i, llm_config in enumerate(LLM_CONFIGS, 1):
                        provider = "Azure OpenAI" if "azure.com" in llm_config.base_url.lower() else \
                                   "Ollama" if "11434" in llm_config.base_url else "Local LLM"
                        print(f"  {i}. {provider} ({llm_config.model_name})")
                    print("=" * 60)

                    def progress_callback(completed, total, current):
                        progress_tracker.update(tracker_id, completed, total, current)
                        job_manager.update_progress(job_id, completed, total, current)
                        print(f"  Progress: {completed}/{total} - {current}")

                    # Use parallel generation
                    ai_summaries = ai_generator.generate_all_summaries_parallel(
                        config,
                        progress_callback=progress_callback,
                        max_workers=3
                    )

                    progress_tracker.mark_done(tracker_id)

                    # Save to cache
                    if ai_summaries:
                        ai_generator.save_to_cache(xml_content, ai_summaries)

                    print(f"✓ AI summary generation completed")
            except Exception as e:
                # Log error but continue without summaries
                print(f"✗ AI summary generation failed: {e}")
                if tracker_id:
                    progress_tracker.mark_done(tracker_id)
                ai_summaries = None

        # Generate HTML
        title = filename.replace('.xml', '').replace('_', ' ').title()
        generator = HTMLGenerator(config, title=title, ai_summaries=ai_summaries)
        html_content = generator.generate_string()

        # Complete the job
        result_bytes = html_content.encode('utf-8')
        result_filename = filename.replace('.xml', '_documentation.html')
        job_manager.complete_job(job_id, result_bytes, result_filename)

    except Exception as e:
        print(f"✗ Job {job_id} failed: {e}")
        job_manager.fail_job(job_id, str(e))
        if tracker_id:
            progress_tracker.mark_done(tracker_id)


@app.route('/', methods=['GET', 'POST'])
def upload():
    """Handle file upload and display results."""
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(UPLOAD_PAGE, error="No file selected", version=__version__,
                                        ai_configured=AI_CONFIGURED)

        file = request.files['file']
        if file.filename == '':
            return render_template_string(UPLOAD_PAGE, error="No file selected", version=__version__,
                                        ai_configured=AI_CONFIGURED)

        if not file.filename.lower().endswith('.xml'):
            return render_template_string(UPLOAD_PAGE, error="Please upload an XML file", version=__version__,
                                        ai_configured=AI_CONFIGURED)

        try:
            # Read XML content
            xml_content = file.read().decode('utf-8')

            # Create job ID
            job_id = str(uuid.uuid4())
            tracker_id = request.form.get('tracker_id') or job_id
            with_ai = request.form.get('with_ai') == 'on'

            # Create tracker if needed
            if not request.form.get('tracker_id'):
                progress_tracker.create_tracker(tracker_id)

            # Create job
            job_manager.create_job(job_id)

            # Start processing in background
            thread = threading.Thread(
                target=process_file_async,
                args=(job_id, xml_content, file.filename, with_ai, tracker_id)
            )
            thread.daemon = True
            thread.start()

            # Return immediately with job ID
            return jsonify({
                'success': True,
                'job_id': job_id,
                'tracker_id': tracker_id,
                'message': 'Processing started'
            })

        except Exception as e:
            return render_template_string(UPLOAD_PAGE, error=f"Error processing file: {str(e)}", version=__version__,
                                        ai_configured=AI_CONFIGURED)

    return render_template_string(UPLOAD_PAGE, error=None, version=__version__,
                                ai_configured=AI_CONFIGURED)


@app.route('/job-status/<job_id>', methods=['GET'])
def job_status(job_id):
    """Get job status."""
    job = job_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'status': job['status'],
        'progress': job['progress'],
        'total': job['total'],
        'current': job['current'],
        'error': job['error']
    })


@app.route('/job-result/<job_id>', methods=['GET'])
def job_result(job_id):
    """Download job result."""
    job = job_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed'}), 400

    if not job['result']:
        return jsonify({'error': 'No result available'}), 404

    # Return the HTML file
    return Response(
        job['result'],
        mimetype='text/html',
        headers={
            'Content-Disposition': f'attachment; filename="{job["filename"]}"'
        }
    )


@app.route('/compare', methods=['POST'])
def compare():
    """Handle comparison of two configuration files."""
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

        # Store in temp file and save ID in session
        diff_title = f"comparison_{file_a.filename.replace('.xml', '')}_vs_{file_b.filename.replace('.xml', '')}"
        diff_file_id = save_html_to_temp(diff_html, diff_title)
        session['diff_file_id'] = diff_file_id

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
    file_id = session.get('generated_file_id')
    if file_id:
        html_content, _ = get_html_from_temp(file_id)
        if html_content:
            return Response(html_content, mimetype='text/html')
    return "No documentation generated yet", 404


@app.route('/preview-diff')
def preview_diff():
    """Return the generated diff HTML for iframe preview."""
    file_id = session.get('diff_file_id')
    if file_id:
        html_content, _ = get_html_from_temp(file_id)
        if html_content:
            return Response(html_content, mimetype='text/html')
    return "No comparison generated yet", 404


@app.route('/download')
def download():
    """Download the generated HTML file."""
    file_id = session.get('generated_file_id')
    if file_id:
        html_content, title = get_html_from_temp(file_id)
        if html_content:
            from datetime import datetime
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{title}_documentation_{timestamp}.html"
            buffer = BytesIO(html_content.encode('utf-8'))
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
    file_id = session.get('diff_file_id')
    if file_id:
        html_content, title = get_html_from_temp(file_id)
        if html_content:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{title}_{timestamp}.html"
            buffer = BytesIO(html_content.encode('utf-8'))
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
