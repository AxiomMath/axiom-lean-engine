"""CLI entry point for AXLE - dynamically generated from endpoint metadata."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, cast

from axle import AxleClient, __version__
from axle.cli.endpoints import ENDPOINTS, CliOutputConfig, EndpointMetadata, InputField


def snake_to_kebab(name: str) -> str:
    """Convert snake_case to kebab-case."""
    return name.replace("_", "-")


def kebab_to_snake(name: str) -> str:
    """Convert kebab-case to snake_case."""
    return name.replace("-", "_")


def read_file_or_stdin(path: str) -> str:
    """Read content from file path or stdin if path is '-'."""
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text()


def parse_list(value: str | None) -> list[str] | None:
    """Parse comma-separated list."""
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_int_list(value: str | None) -> list[int] | None:
    """Parse comma-separated list of integers."""
    if not value:
        return None
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def parse_dict(value: str | None) -> dict[str, str] | None:
    """Parse key=val,key=val format or JSON."""
    if not value:
        return None
    # Try JSON first
    if value.startswith("{"):
        return cast(dict[str, str], json.loads(value))
    # Parse key=val format
    result: dict[str, str] = {}
    for pair in value.split(","):
        if "=" in pair:
            key, val = pair.split("=", 1)
            result[key.strip()] = val.strip()
    return result


def get_positional_inputs(inputs: list[InputField]) -> list[InputField]:
    """Get inputs that are positional arguments, sorted by position."""
    positional = [inp for inp in inputs if inp.get("cli_positional")]

    def sort_key(x: InputField) -> int:
        pos = x.get("cli_positional")
        return pos if isinstance(pos, int) else 999

    return sorted(positional, key=sort_key)


def get_flag_inputs(inputs: list[InputField]) -> list[InputField]:
    """Get inputs that are flags (not positional and not hidden)."""
    return [inp for inp in inputs if not inp.get("cli_positional") and not inp.get("cli_hidden")]


def add_endpoint_subparser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    endpoint_name: str,
    metadata: EndpointMetadata,
) -> None:
    """Add a subparser for an endpoint based on its metadata."""
    inputs = metadata.get("inputs", [])
    outputs = metadata.get("outputs", [])
    cli_output = metadata.get("cli_output", {})

    # Create subparser
    sub = subparsers.add_parser(
        endpoint_name,
        help=metadata.get("description", ""),
        description=metadata.get("details", ""),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    positional_inputs = get_positional_inputs(inputs)
    flag_inputs = get_flag_inputs(inputs)

    # Add positional arguments
    for inp in positional_inputs:
        arg_name = inp["name"].upper()
        help_text = inp.get("description", "")

        if inp.get("cli_multiple_files"):
            sub.add_argument(arg_name, nargs="+", help=help_text)
        else:
            if inp.get("cli_stdin_support"):
                help_text += " (use - for stdin)"
            sub.add_argument(arg_name, help=help_text)

    # Add flag arguments
    for inp in flag_inputs:
        flag_name = inp.get("cli_flag", f"--{snake_to_kebab(inp['name'])}")
        help_text = inp.get("description", "")

        if inp["type"] == "checkbox":
            default = inp.get("default", False)
            # For checkboxes with default=True, we need --no-X to disable
            if default:
                sub.add_argument(
                    f"--no-{snake_to_kebab(inp['name'])}",
                    action="store_false",
                    dest=inp["name"],
                    default=default,
                    help=f"Disable {inp['name'].replace('_', ' ')} (default: enabled)",
                )
            else:
                sub.add_argument(
                    flag_name,
                    action="store_true",
                    dest=inp["name"],
                    default=default,
                    help=f"{help_text} (default: {default})",
                )

        elif inp["type"] == "dict":
            if inp.get("cli_dict_inline"):
                sub.add_argument(
                    flag_name,
                    help=f"{help_text} (format: key=val,key=val or JSON)",
                )
            if inp.get("cli_dict_file_flag"):
                sub.add_argument(
                    inp["cli_dict_file_flag"],
                    help=f"JSON file with {inp['name']}",
                )

        elif inp["type"] == "number":
            default = inp.get("default")
            if default is not None:
                help_text += f" (default: {default})"
            sub.add_argument(
                flag_name,
                type=float,
                default=default,
                help=help_text,
            )

        elif inp["type"] == "list":
            if inp.get("default") is not None:
                help_text += f" (default: {inp.get('default')})"
            sub.add_argument(
                flag_name,
                help=f"{help_text} (comma-separated)",
            )

        else:  # text, textarea
            required = inp.get("required", False) and not inp.get("cli_positional")
            sub.add_argument(
                flag_name,
                required=required,
                help=help_text,
            )

    # Add output flags based on cli_output config
    if cli_output.get("supports_output_file"):
        sub.add_argument("-o", "--output", help="Output file path")
    if cli_output.get("supports_output_dir"):
        default_dir = cli_output.get("output_dir_default", "output/")
        sub.add_argument(
            "-d",
            "--output-dir",
            default=default_dir,
            help=f"Output directory (default: {default_dir})",
        )
    if cli_output.get("force_flag"):
        sub.add_argument("-f", "--force", action="store_true", help="Overwrite existing files")

    # Add --strict flag for endpoints with okay output
    has_okay_field = any(out.get("name") == "okay" for out in outputs)
    if has_okay_field:
        sub.add_argument(
            "--strict",
            action="store_true",
            help="Exit with non-zero code if validation fails (okay is false)",
        )


def build_request_kwargs(
    args: argparse.Namespace,
    endpoint_name: str,
    metadata: EndpointMetadata,
) -> dict[str, Any]:
    """Build request kwargs from parsed arguments."""
    inputs = metadata.get("inputs", [])
    kwargs: dict[str, Any] = {}

    for inp in inputs:
        name = inp["name"]
        inp_type = inp["type"]

        # Handle positional with multiple files
        if inp.get("cli_multiple_files"):
            arg_name = name.upper()
            if hasattr(args, arg_name):
                file_paths = getattr(args, arg_name)
                kwargs[name] = [read_file_or_stdin(fp) for fp in file_paths]
            continue

        # Handle positional with stdin support
        if inp.get("cli_positional"):
            arg_name = name.upper()
            if hasattr(args, arg_name):
                path = getattr(args, arg_name)
                kwargs[name] = read_file_or_stdin(path)
            continue

        # Handle dict with file flag
        if inp_type == "dict" and inp.get("cli_dict_file_flag"):
            file_flag_attr = inp["cli_dict_file_flag"].lstrip("-").replace("-", "_")
            inline_attr = (
                inp.get("cli_flag", f"--{snake_to_kebab(name)}").lstrip("-").replace("-", "_")
            )

            if hasattr(args, file_flag_attr) and getattr(args, file_flag_attr):
                file_path = getattr(args, file_flag_attr)
                try:
                    with open(file_path) as f:
                        kwargs[name] = json.load(f)
                except FileNotFoundError:
                    raise SystemExit(f"Error: File not found: {file_path}")
                except json.JSONDecodeError as e:
                    raise SystemExit(f"Error: Invalid JSON in {file_path}: {e}")
            elif hasattr(args, inline_attr) and getattr(args, inline_attr):
                kwargs[name] = parse_dict(getattr(args, inline_attr))
            continue

        # Handle regular flags
        flag_attr = inp.get("cli_flag", f"--{snake_to_kebab(name)}").lstrip("-").replace("-", "_")

        # Also check direct name for checkbox types stored with dest=name
        value = None
        if hasattr(args, name):
            value = getattr(args, name)
        elif hasattr(args, flag_attr):
            value = getattr(args, flag_attr)

        if value is None:
            continue

        # Skip if checkbox is at default value
        if inp_type == "checkbox":
            default = inp.get("default", False)
            if value == default:
                continue
            kwargs[name] = value

        elif inp_type == "list":
            if isinstance(value, str):
                if inp.get("cli_list_type") == "int":
                    kwargs[name] = parse_int_list(value)
                else:
                    kwargs[name] = parse_list(value)
            elif value:
                kwargs[name] = value

        elif inp_type == "number":
            default = inp.get("default")
            if value != default:
                kwargs[name] = value

        elif inp_type == "dict":
            if isinstance(value, str):
                kwargs[name] = parse_dict(value)
            elif value:
                kwargs[name] = value

        else:  # text, textarea
            if value:
                kwargs[name] = value

    return kwargs


def format_output(
    result: dict[str, Any],
    cli_output: CliOutputConfig,
    json_output: bool,
) -> str:
    """Format the result for output."""
    mode = cli_output.get("mode", "json_stdout")

    if json_output or mode == "json_stdout":
        return json.dumps(result, indent=2)

    # For lean_stdout mode, return content field if present
    if mode == "lean_stdout":
        return cast(str, result.get("content", ""))

    return json.dumps(result, indent=2)


def handle_multiple_files_output(
    result: dict[str, Any],
    args: argparse.Namespace,
    cli_output: CliOutputConfig,
) -> int:
    """Handle multiple files output mode. Returns exit code."""
    output_dir = getattr(args, "output_dir", cli_output.get("output_dir_default", "output/"))
    pattern = cli_output.get("output_file_pattern", "output_{i}.lean")
    force = getattr(args, "force", False)

    os.makedirs(output_dir, exist_ok=True)

    # Handle both list and dict document outputs
    documents = result.get("documents", [])
    if isinstance(documents, dict):
        # Dict output: use keys as filenames
        items = list(documents.items())
    else:
        # List output: use pattern with index
        items = [(pattern.format(i=i), doc) for i, doc in enumerate(documents)]

    # Check if files exist
    if not force:
        for name, _ in items:
            if isinstance(documents, dict):
                fpath = os.path.join(output_dir, f"{name}.lean")
            else:
                fpath = os.path.join(output_dir, name)
            if os.path.exists(fpath):
                sys.stderr.write(f"Error: {fpath} already exists. Use -f to overwrite.\n")
                return 2

    # Write files
    for name, doc in items:
        if isinstance(documents, dict):
            fpath = os.path.join(output_dir, f"{name}.lean")
            file_content = doc["content"] if isinstance(doc, dict) else doc
        else:
            fpath = os.path.join(output_dir, name)
            file_content = doc
        with open(fpath, "w") as f:
            f.write(file_content)
        sys.stderr.write(f"Wrote {fpath}\n")

    # Output summary to stdout
    print(json.dumps(result, indent=2))
    return 0


async def run_command(args: argparse.Namespace) -> int:
    """Run the specified command."""
    command = args.command
    endpoint_name = kebab_to_snake(command)

    # Special case for environments
    if endpoint_name == "environments":
        async with AxleClient(url=args.url) as client:
            print(json.dumps(await client.environments(), indent=2))
        return 0

    metadata = ENDPOINTS.get(endpoint_name)

    if not metadata:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1

    cli_output = metadata.get("cli_output", {})

    # Build request kwargs
    kwargs = build_request_kwargs(args, endpoint_name, metadata)

    # Execute the API call
    async with AxleClient(url=args.url) as client:
        result = await client.run_one(endpoint_name, kwargs)

    # Handle output based on mode
    mode = cli_output.get("mode", "json_stdout")

    if mode == "multiple_files":
        exit_code = handle_multiple_files_output(result, args, cli_output)
        if exit_code != 0:
            return exit_code
    else:
        output = format_output(result, cli_output, args.json)

        # Write to file or stdout
        if hasattr(args, "output") and args.output:
            Path(args.output).write_text(output)
            print(f"Output written to {args.output}", file=sys.stderr)
        else:
            if mode == "lean_stdout":
                # Don't add extra newline for lean output
                print(output, end="")
            else:
                print(output)

        # Write metadata to stderr for lean_stdout mode
        if mode == "lean_stdout" and cli_output.get("metadata_to_stderr"):
            metadata_out = {k: v for k, v in result.items() if k != "content"}
            if metadata_out:
                sys.stderr.write(json.dumps(metadata_out, indent=2) + "\n")

    # Check strict mode
    if getattr(args, "strict", False) and not result.get("okay", True):
        return 3

    # Return exit code based on result
    return 0


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser dynamically from endpoint metadata."""
    parser = argparse.ArgumentParser(
        prog="axle",
        description="AXLE - Axiom Lean Engine CLI",
    )
    parser.add_argument("--version", action="version", version=f"axle {__version__}")
    parser.add_argument("--url", default=None, help="API server URL")
    parser.add_argument("--json", action="store_true", help="Force JSON output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Dynamically add subparsers for each endpoint
    for endpoint_name, metadata in ENDPOINTS.items():
        add_endpoint_subparser(subparsers, snake_to_kebab(endpoint_name), metadata)

    # Add environments command
    subparsers.add_parser("environments", help="List available Lean environments")

    return parser


def main() -> None:
    """CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        exit_code = asyncio.run(run_command(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
