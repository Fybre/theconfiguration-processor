"""Command-line interface for Therefore Configuration Processor."""

import argparse
import sys
from pathlib import Path

from . import __version__
from .parser import ConfigurationParser
from .generator import HTMLGenerator


def main(args=None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="theconfiguration-processor",
        description="Generate HTML documentation from Therefore configuration exports."
    )

    parser.add_argument(
        "input",
        help="Path to the Therefore configuration XML file"
    )

    parser.add_argument(
        "-o", "--output",
        default="./output",
        help="Output directory (default: ./output)"
    )

    parser.add_argument(
        "-t", "--title",
        default="Therefore Configuration",
        help="Documentation title (default: 'Therefore Configuration')"
    )

    parser.add_argument(
        "-f", "--filename",
        default="documentation.html",
        help="Output filename (default: documentation.html)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parsed_args = parser.parse_args(args)

    # Validate input file
    input_path = Path(parsed_args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {parsed_args.input}", file=sys.stderr)
        return 1

    if not input_path.suffix.lower() == ".xml":
        print(f"Warning: Input file does not have .xml extension", file=sys.stderr)

    # Create output path
    output_dir = Path(parsed_args.output)
    output_file = output_dir / parsed_args.filename

    try:
        # Parse configuration
        if parsed_args.verbose:
            print(f"Parsing configuration from: {input_path}")

        parser_instance = ConfigurationParser()
        config = parser_instance.parse(str(input_path))

        if parsed_args.verbose:
            stats = config.get_statistics()
            print(f"  Found {stats['categories']} categories")
            print(f"  Found {stats['fields']} fields")
            print(f"  Found {stats['workflows']} workflows")
            print(f"  Found {stats['folders']} folders")
            print(f"  Found {stats['roles']} roles")
            print(f"  Found {stats['eforms']} EForms")
            print(f"  Found {stats['queries']} queries")

        # Generate documentation
        if parsed_args.verbose:
            print(f"Generating documentation...")

        generator = HTMLGenerator(config, title=parsed_args.title)
        output_path = generator.generate(str(output_file))

        print(f"Documentation generated: {output_path}")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if parsed_args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
