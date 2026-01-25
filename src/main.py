#!/usr/bin/env python3
"""
Therefore Configuration Processor - Main Entry Point

Generate HTML documentation from Therefore document management system
configuration export files.

Usage:
    # CLI mode
    python -m src.main config.xml -o output/

    # GUI mode
    python -m src.main --gui

    # With options
    python -m src.main config.xml -o output/ --title "My System"
"""

import sys
import argparse


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="theconfiguration-processor",
        description="Generate HTML documentation from Therefore configuration exports.",
        add_help=False
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface"
    )

    parser.add_argument(
        "-h", "--help",
        action="store_true",
        help="Show this help message and exit"
    )

    # Parse only known args to check for --gui
    args, remaining = parser.parse_known_args()

    if args.gui:
        # Launch GUI
        from .gui import main as gui_main
        gui_main()
        return 0
    else:
        # Run CLI with all arguments
        from .cli import main as cli_main
        # Reconstruct full argument list
        if args.help:
            remaining = ["-h"] + remaining
        return cli_main(remaining)


if __name__ == "__main__":
    sys.exit(main())
