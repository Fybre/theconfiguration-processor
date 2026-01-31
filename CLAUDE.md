# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Therefore Configuration Processor generates HTML documentation from Therefore document management system configuration XML exports. It parses complex XML configuration files and produces interactive HTML documentation.

## Commands

### Install and Run
```bash
# Install for development
pip install -e ".[dev]"

# Install with web server support
pip install -e ".[web]"

# Run CLI
python -m src.main samples/demo-TheConfiguration.xml -o output/ --title "My Configuration"

# Run web server (port 5050)
python -m src.web

# Run GUI (requires tkinter)
python -m src.main --gui
```

### Testing
```bash
# Run all tests
pytest

# Run a single test
pytest tests/test_parser.py::TestConfigurationParser::test_parse_category

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

### Docker
```bash
docker-compose up      # Start web server
docker-compose down    # Stop
```

## Architecture

The codebase follows a parser-generator pattern:

```
src/
├── main.py              # Entry point (dispatches to CLI or GUI)
├── cli.py               # CLI argument parsing and orchestration
├── web.py               # Flask web application
├── gui.py               # Tkinter GUI
├── parser/
│   ├── config_parser.py # XML parsing (ConfigurationParser class)
│   ├── models.py        # Dataclasses for all config entities
│   └── constants.py     # Lookup tables for type codes
├── generator/
│   ├── html_generator.py # HTML generation (HTMLGenerator class)
│   └── templates.py      # HTML/CSS/JS template strings
└── utils/
    └── helpers.py        # XML text extraction, HTML escaping, slugify
```

### Data Flow
1. `ConfigurationParser.parse(xml_path)` reads XML and returns a `Configuration` object
2. `Configuration` contains lists of dataclasses (Category, WorkflowProcess, Role, etc.)
3. `Configuration.build_lookup_maps()` creates cross-reference dicts (called automatically)
4. `HTMLGenerator(config).generate(output_path)` produces HTML documentation

### Key Model Relationships
- Categories contain Fields and may belong to CaseDefinitions
- WorkflowProcesses contain WorkflowTasks which have WorkflowTransitions
- Fields reference KeywordDictionaries via TypeNo (not DictionaryNo directly)
- RoleAssignments link Roles to objects (categories, folders) with Users/Groups
- Configuration provides lookup methods: `get_category()`, `get_dictionary_by_type_no()`, `get_folder_path()`, etc.

### XML Parsing Notes
- Localized text uses `<TStr><T><L>1033</L><S>text</S></T></TStr>` format
- Use `get_text_from_tstr()` helper to extract text from TStr elements
- Negative IDs (e.g., CtgryNo=-1) are common for new objects
- Type codes are mapped via constants.py lookup tables (FIELD_TYPES, WORKFLOW_TASK_TYPE, etc.)

## No External Dependencies

Core functionality uses only Python standard library. Flask is optional for web server.
