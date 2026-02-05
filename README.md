# Therefore Configuration Processor

## Overview

The Therefore Configuration Processor generates comprehensive, interactive HTML documentation from Therefore document management system configuration exports. It includes AI-powered summaries, security audit reports, and interactive workflow visualizations.

## Key Features

### 📄 Core Documentation
- **Web Interface**: Upload Therefore configuration XML files through a user-friendly web interface
- **HTML Generation**: Automatically generates comprehensive, navigable HTML documentation
- **Interactive Navigation**: Collapsible sections, search functionality, and quick navigation sidebar
- **Configuration Comparison**: Compare two configuration files side-by-side with detailed diff views
- **Volume Mapping**: Output files are available on your host system (Docker mode)

### 🤖 AI-Powered Summaries
- **Local LLM Integration**: Generate human-readable summaries using local LLMs (Ollama, LM Studio, LocalAI)
- **Parallel Generation**: Process multiple summaries concurrently for faster results
- **Real-Time Progress**: Live progress bar with Server-Sent Events showing generation status
- **Comprehensive Coverage**: AI summaries for system overview, categories, workflows, and roles
- **Privacy-First**: All AI processing happens locally - no external API calls

### 🔒 Security Audit Report
- **Permission Conflict Detection**: Identify objects with both allow and deny permissions
- **Unsecured Object Analysis**: Find objects without any role assignments (publicly accessible)
- **Deny Role Analysis**: Review roles that explicitly block access and their impact
- **Overprivileged User Detection**: Identify users/groups with excessive role assignments
- **Role Access Matrix**: Comprehensive view of role assignments by object type
- **User Access Summary**: Detailed breakdown of what each user/group can access

### 📊 Interactive Workflow Diagrams
- **Click-to-Expand**: Click any workflow diagram to view full-size in an overlay
- **Pan & Zoom Controls**: Interactive controls with mouse wheel zoom, click-drag pan
- **Mermaid Visualization**: Flowchart-based workflow process diagrams
- **Usage Instructions**: Built-in header with keyboard shortcuts and interaction guide

## Project Structure

```
.
├── Dockerfile                  # Docker container configuration
├── docker-compose.yaml         # Docker Compose configuration
├── .dockerignore               # Files to ignore during Docker build
├── src/                        # Source code
│   ├── web.py                  # Flask web application
│   ├── cli.py                  # Command line interface
│   ├── main.py                 # Main entry point
│   ├── ai/                     # AI summary generation module
│   │   ├── llm_client.py       # OpenAI-compatible LLM client
│   │   ├── prompts.py          # Prompt templates
│   │   └── summary_generator.py # Summary orchestration
│   ├── analyzer/               # Analysis modules
│   │   └── security_analyzer.py # Security audit analyzer
│   ├── generator/              # HTML generation
│   │   ├── html_generator.py   # Main HTML generator
│   │   ├── html_generator_security.py # Security section generator
│   │   └── templates.py        # HTML/CSS/JS templates
│   ├── parser/                 # XML parsing
│   │   ├── config_parser.py    # Configuration parser
│   │   ├── models.py           # Data models
│   │   └── constants.py        # Type lookup tables
│   ├── progress_tracker.py     # Real-time progress tracking
│   └── utils/                  # Utility functions
├── samples/                    # Sample configuration files
├── output/                     # Generated HTML documentation
├── tests/                      # Test suite
└── README.md                   # This file
```

## Requirements

### Basic Requirements
- Python 3.12+
- Docker (for containerized deployment)

### Optional Requirements for AI Features
- Local LLM server (Ollama, LM Studio, or LocalAI)
- OpenAI-compatible API endpoint

## Installation & Setup

### 1. Docker Web Server (Recommended)

```bash
# Start the web server container
docker-compose up

# Access the web interface at:
# http://localhost:5050

# Upload XML files through the browser interface
# Download generated HTML files with timestamps
```

### 2. Native Installation

```bash
# Basic installation
pip install -e .

# With web server support
pip install -e ".[web]"

# With AI summary generation
pip install -e ".[webai]"

# With GUI support
pip install -e ".[gui]"

# Full installation (all features)
pip install -e ".[web,webai,gui]"
```

### 3. AI Setup (Optional)

For AI-powered summaries, set up a local LLM:

**Ollama** (Recommended):
```bash
# Install Ollama
# Visit https://ollama.ai for installation instructions

# Start Ollama server
ollama serve

# Pull a model
ollama pull llama3.2
```

**LM Studio**:
- Download and install LM Studio
- Load a model
- Start the local server (default: http://localhost:1234/v1)

**LocalAI**:
- Follow LocalAI installation instructions
- Configure OpenAI-compatible endpoint

## Usage

### Web Interface

```bash
# Start the web server
python -m src.web

# Access at http://localhost:5050
```

**Features:**
1. Upload Therefore configuration XML files (drag-and-drop or click to browse)
2. Enable AI summaries (optional):
   - Check "Generate AI Summaries"
   - Configure LLM endpoint (default: http://localhost:11434/v1)
   - Set model name (default: llama3.2)
   - Click "Test Connection" to verify
3. View real-time progress during AI generation
4. Preview and download generated HTML documentation
5. Compare two configurations side-by-side

### Command Line Interface

```bash
# Basic usage
python -m src.main samples/demo-TheConfiguration.xml -o output/ --title "My Configuration"

# With verbose output
python -m src.main samples/demo-TheConfiguration.xml -o output/ -v

# Specify custom output filename
python -m src.main config.xml -o output/ --output-filename custom-name.html
```

### Graphical User Interface

```bash
# Install GUI dependencies
pip install -e ".[gui]"

# Run the GUI application
python -m src.main --gui
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# LLM Configuration
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=llama3.2
LLM_TIMEOUT=60

# Flask Configuration
FLASK_DEBUG=True
FLASK_PORT=5050
```

### LLM Configuration

The AI summary feature supports any OpenAI-compatible API:

| Provider | Default URL | Notes |
|----------|-------------|-------|
| Ollama | http://localhost:11434/v1 | Recommended for local use |
| LM Studio | http://localhost:1234/v1 | GUI-based model management |
| LocalAI | http://localhost:8080/v1 | Self-hosted alternative |

## Generated Documentation Features

The generated HTML includes:

### Core Documentation
- **System Overview**: Configuration statistics, version info, metadata
- **Categories**: Document types with fields, permissions, and workflows
- **Workflows**: Task flows with transitions, conditions, and routing
- **Roles**: Permission assignments and access control
- **Folders**: Document organization structure
- **Dictionaries**: Keyword lists and lookup tables

### AI Summaries (Optional)
- **Natural Language Descriptions**: Human-readable explanations of complex configurations
- **Key Highlights**: Bullet points highlighting important aspects
- **Contextual Analysis**: Purpose, security considerations, and usage patterns

### Security Audit Report
- **Permission Conflicts**: Objects with contradictory allow/deny rules
- **Unsecured Objects**: Items without role assignments
- **Deny Role Analysis**: Roles blocking access and affected users
- **Overprivileged Users**: Users with excessive permissions
- **Role Access Matrix**: Summary of role assignments by type
- **User Access Summary**: Per-user/group access breakdown

### Interactive Elements
- **Collapsible Sections**: Expand/collapse for easier navigation
- **Search Functionality**: Quick search across all content
- **Field Filtering**: Toggle required vs. optional fields
- **Label Field Highlighting**: Visual indicators for label fields
- **Workflow Diagrams**: Click-to-expand with pan/zoom controls
- **Dark Mode Support**: Automatic theme detection
- **Mobile Responsive**: Works on tablets and smartphones

## Performance

### AI Summary Generation Times
With local LLM (Ollama + llama3.2):
- System overview: 10-15 seconds
- Per category: 8-12 seconds
- Per workflow: 8-12 seconds
- Per role: 6-10 seconds

**Typical configuration** (20 categories, 5 workflows, 3 roles):
- Sequential generation: ~12-15 minutes
- Parallel generation (3 workers): ~4-6 minutes

### Optimization
- In-memory caching for repeated requests
- Parallel processing with configurable workers
- Real-time progress tracking
- Graceful degradation when LLM unavailable

## Docker Configuration

### Dockerfile
- **Base Image**: `python:3.12-slim`
- **Port**: Exposed on port 5050
- **Dependencies**: Flask, optional AI libraries
- **Health Check**: Verifies web server availability
- **Command**: Runs the Flask web server

### docker-compose.yaml
- **Service Name**: `configuration-processor`
- **Port Mapping**: `5050:5050` (host:container)
- **Volume Mapping**:
  - `./output:/app/output` - Generated HTML files
  - `./samples:/app/samples` - Sample configuration files
- **Restart Policy**: `unless-stopped` for automatic recovery

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_parser.py

# Verbose output
pytest -v
```

### Project Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run linting
flake8 src/

# Format code
black src/

# Type checking
mypy src/
```

## Troubleshooting

### Common Issues

**Port 5050 already in use:**
```bash
# Change port in docker-compose.yaml or use environment variable
FLASK_PORT=5051 python -m src.web
```

**AI generation fails:**
- Verify LLM server is running: `curl http://localhost:11434/v1/models`
- Check model is loaded: `ollama list`
- Test connection in web interface before generating

**Workflow diagrams not displaying:**
- Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- Check browser console for JavaScript errors
- Verify Mermaid.js library is loading

**Memory issues with large configurations:**
- Disable AI summaries for initial processing
- Increase Python memory limit if needed
- Process in CLI mode instead of web interface

### View Logs

```bash
# Docker logs
docker logs configuration-processor

# Native Python logs
python -m src.web 2>&1 | tee app.log
```

## Sample Files

The `samples/` directory contains example configurations:
- Various test configurations with different complexity levels
- Use for testing and demonstration purposes

## Security & Privacy

### AI Features
- ✅ **Local-Only**: No external API calls, data never leaves your network
- ✅ **No API Keys**: Local LLMs don't require authentication
- ✅ **Optional**: AI features are completely optional
- ✅ **Graceful Degradation**: Full functionality without AI enabled

### General
- Input validation and sanitization
- HTML escaping for all dynamic content
- No sensitive data storage
- Open source for security review

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/Fybre/theconfiguration-processor/issues
- Documentation: See CLAUDE.md for development guidelines

## Acknowledgments

Built with:
- Flask - Web framework
- Mermaid.js - Workflow diagrams
- svg-pan-zoom - Interactive diagram controls
- OpenAI-compatible APIs - AI summary generation
