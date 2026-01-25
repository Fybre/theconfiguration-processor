# Therefore Configuration Processor - With Docker Setup

## Overview

This Docker setup provides a containerized version of the Therefore Configuration Processor web application. The application generates HTML documentation from Therefore document management system configuration exports.

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
│   └── ...                     # Other source files
├── samples/                    # Sample configuration files
├── output/                     # Generated HTML documentation (volume mapped)
└── README.md                   # This file
```

## Features

- **Web Interface**: Upload Therefore configuration XML files through a user-friendly web interface
- **HTML Generation**: Automatically generates comprehensive HTML documentation
- **Volume Mapping**: Output files are available on your host system
- **Health Monitoring**: Built-in health checks to ensure the service is running
- **Easy Deployment**: Single command to start the entire service

## Requirements

- Docker installed on your system
- Docker Compose (included with modern Docker installations)

## Execution Methods

The Therefore Configuration Processor can be run in multiple ways:

### 1. Docker Web Server (Recommended)

```bash
# Start the web server container
docker-compose up

# Access the web interface at:
# http://localhost:5050

# Upload XML files through the browser interface
# Download generated HTML files with timestamps
```

### 2. Native Web Server

```bash
# Install dependencies
pip install -e ".[web]"

# Run the web server
python -m src.web

# Access at http://localhost:5050
```

### 3. Command Line Interface

```bash
# Install the package
pip install -e .

# Process a configuration file
python -m src.main samples/demo-TheConfiguration.xml -o output/ --title "My Configuration"

# With verbose output
python -m src.main samples/demo-TheConfiguration.xml -o output/ -v
```

### 4. Graphical User Interface

```bash
# Install GUI dependencies
pip install -e ".[gui]"

# Run the GUI application
python -m src.main --gui
```

## Docker vs Native Execution

**Docker Benefits:**

- Consistent environment across different systems
- Easy deployment and distribution
- Volume mapping for easy file access
- Built-in health monitoring

**Native Benefits:**

- Faster startup time
- Direct file system access
- Easier debugging and development
- No Docker overhead

## Quick Start

1. **Build and start the container**:

   ```bash
   docker-compose up
   ```

2. **Access the web interface**:
   Open your browser to [http://localhost:5050](http://localhost:5050)

3. **Upload a configuration file**:
   - Click or drag-and-drop a Therefore configuration XML file
   - The system will process the file and generate HTML documentation

4. **Download results**:
   - Preview the generated documentation in the browser
   - Download the HTML file for offline use

## Docker Configuration Details

### Dockerfile

- **Base Image**: `python:3.12-slim`
- **Port**: Exposed on port 5050
- **Dependencies**: Flask web framework
- **Health Check**: Verifies web server availability
- **Command**: Runs the Flask web server

### docker-compose.yaml

- **Service Name**: `configuration-processor`
- **Port Mapping**: `5050:5050` (host:container)
- **Volume Mapping**:
  - `./output:/app/output` - Generated HTML files
  - `./samples:/app/samples` - Sample configuration files
- **Restart Policy**: `unless-stopped` for automatic recovery

## Usage Examples

### Basic Usage

```bash
# Start the service
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop the service
docker-compose down
```

### Processing Files

1. **Via Web Interface**:
   - Upload through the browser at http://localhost:5050
   - Download the generated HTML file

2. **Using Sample Files**:
   - Sample files are available in the `samples/` directory
   - You can test with `samples/demo-TheConfiguration.xml`

### Accessing Generated Files

Generated HTML files are automatically available in your local `output/` directory due to the volume mapping. You can access them directly from your host system.

## Health Monitoring

The container includes a health check that verifies the web server is responding:

```bash
# Check container health status
docker inspect --format='{{json .State.Health}}' configuration-processor
```

## Development Notes

- The web server runs in debug mode by default (not suitable for production)
- For production use, consider adding a proper WSGI server like Gunicorn
- The container automatically restarts if it crashes

## Troubleshooting

**Common Issues**:

1. **Port Conflict**: If port 5050 is already in use, change the port mapping in `docker-compose.yaml`

2. **Permission Issues**: Ensure your user has permission to access Docker

3. **Health Check Failures**: Verify the web server is running with `docker logs configuration-processor`

**View Logs**:

```bash
docker logs configuration-processor
```

## Sample Configuration Files

The `samples/` directory contains example Therefore configuration files you can use to test the system:

- `demo-TheConfiguration.xml` - Basic demo configuration
- `full-sample.xml` - Complete sample with all features
- Various other test configurations

## Output Files

Generated HTML documentation includes:

- Comprehensive system overview
- Configuration statistics
- Interactive navigation
- Detailed field and workflow documentation
- Role and permission information
- **Date/Time Stamps**: Downloaded files include timestamps in the filename (format: `filename_documentation_YYYYMMDD_HHMMSS.html`)

## License

This project is licensed under the MIT License. See the project's main license file for details.
