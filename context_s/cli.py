"""Command-line utilities for ContextS."""

from __future__ import annotations

import argparse
import os
import sys
from getpass import getpass
from textwrap import dedent
from typing import Iterable, Tuple

from .config import (
    CONFIG_DIR_ENV,
    get_config_path,
    get_context7_api_key,
    mask_secret,
    set_context7_api_key,
)

CONTEXT7_API_BASE_URL = "https://context7.com/api"
AI_ENV_VARS: Tuple[Tuple[str, str], ...] = (
    ("GEMINI_API_KEY", "Google Gemini"),
    ("OPENAI_API_KEY", "OpenAI"),
    ("ANTHROPIC_API_KEY", "Anthropic"),
)


def _format_status(value: bool) -> str:
    return "configured" if value else "missing"


def show_dashboard() -> None:
    """Display a simple dashboard summarising the setup state."""
    api_key, source = get_context7_api_key()
    config_path = get_config_path()
    config_exists = config_path.exists()

    print("ContextS Dashboard")
    print("=" * 18)
    print()
    print(f"Context7 API endpoint : {CONTEXT7_API_BASE_URL}")
    print(
        "Context7 API key      : "
        + (
            f"{_describe_source(source)} ({mask_secret(api_key)})"
            if api_key
            else "not configured"
        )
    )
    print(
        "Configuration file    : "
        + (
            f"{config_path}"
            if config_exists
            else f"{config_path} (create via `context-s setup`)"
        )
    )
    config_dir_override = os.getenv(CONFIG_DIR_ENV)
    if config_dir_override:
        print(f"Config directory env  : {CONFIG_DIR_ENV}={config_dir_override}")
    else:
        print(f"Config directory env  : {CONFIG_DIR_ENV} (not set)")
    print()
    print("AI Providers")
    print("-----------")
    for env_var, label in AI_ENV_VARS:
        present = bool(os.getenv(env_var))
        print(f"- {label:<16} : {_format_status(present)} ({env_var})")
    print()
    print("Next steps")
    print("----------")
    print("* Run `context-s setup` to configure your Context7 API key (optional).")
    print("* Launch the MCP server with `python main.py` once your API keys are ready.")
    print("* Use `context-s help` to see available CLI commands.")


def _describe_source(source: str) -> str:
    if source == "environment":
        return "environment variable"
    if source == "config":
        return "stored in config"
    return "unknown source"


def show_help() -> None:
    """Display CLI usage instructions."""
    message = dedent(
        """
        ContextS CLI
        ============

        Usage:
          context-s               Show the dashboard summary
          context-s help          Display this help message
          context-s setup [opts]  Configure the Context7 API key

        Setup options:
          --api-key <key>         Set the Context7 API key without prompting.
          --remove                Remove the stored Context7 API key from the config file.
          --print-path            Show where the configuration file is stored.
          --no-prompt             Skip interactive prompts (use with --api-key or --remove).
        """
    ).strip()
    print(message)


def run_setup(argv: Iterable[str]) -> int:
    """Handle the `context-s setup` command."""
    parser = argparse.ArgumentParser(
        prog="context-s setup",
        description="Configure access to the Context7 API.",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        help="Set the Context7 API key non-interactively.",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove any stored Context7 API key from the configuration file.",
    )
    parser.add_argument(
        "--print-path",
        action="store_true",
        help="Display the path to the configuration file and exit.",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Skip interactive prompts (useful for automation).",
    )

    args = parser.parse_args(list(argv))

    if args.print_path:
        print(f"Configuration file: {get_config_path()}")
        return 0

    api_key, source = get_context7_api_key()
    if api_key:
        print(
            f"Current Context7 API key: {mask_secret(api_key)} (source: {_describe_source(source)})"
        )
    else:
        print("No Context7 API key is currently configured.")
    print("You can obtain a key from https://context7.com/dashboard (optional).")

    if args.remove:
        set_context7_api_key(None)
        print("Stored Context7 API key removed.")
        # Removing the key still succeeds even if an environment variable overrides it
        if source == "environment":
            print(
                "An environment variable is still set. Unset CONTEXT7_API_KEY if you wish to fully remove the key."
            )
        return 0

    if args.api_key:
        set_context7_api_key(args.api_key)
        print("Context7 API key saved to configuration file.")
        if source == "environment":
            print(
                "Note: The environment variable CONTEXT7_API_KEY still takes precedence at runtime."
            )
        return 0

    if args.no_prompt:
        return 0

    if source == "environment":
        print(
            "A Context7 API key is already supplied via the CONTEXT7_API_KEY environment variable."
        )
        print("Update that variable directly if you need to change the key.")
        return 0

    if not sys.stdin.isatty():
        print(
            "Interactive input is not available. Re-run with `--api-key` or from an interactive terminal.",
            file=sys.stderr,
        )
        return 1

    try:
        entered = getpass("Enter Context7 API key (leave blank to skip): ")
    except (EOFError, KeyboardInterrupt):
        print("\nSetup cancelled.")
        return 1

    if entered.strip():
        set_context7_api_key(entered.strip())
        print("Context7 API key saved to configuration file.")
    else:
        print("No changes made.")

    return 0


def main(argv: Iterable[str] | None = None) -> int:
    """Entry point for the `context-s` CLI."""
    if argv is None:
        argv = sys.argv[1:]

    arguments = list(argv)
    if not arguments:
        show_dashboard()
        return 0

    command, *rest = arguments
    if command in {"help", "-h", "--help"}:
        show_help()
        return 0

    if command in {"setup"}:
        return run_setup(rest)

    if command in {"dashboard"}:
        show_dashboard()
        return 0

    print(f"Unknown command: {command}", file=sys.stderr)
    print("Run `context-s help` to see available commands.", file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI direct execution
    raise SystemExit(main())
