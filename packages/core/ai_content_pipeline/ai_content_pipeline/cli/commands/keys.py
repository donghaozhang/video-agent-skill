"""
CLI commands for managing API keys.

Commands:
- ``set-key``   — store a key via hidden prompt or --stdin
- ``get-key``   — display a stored key (masked by default)
- ``check-keys`` — show status of all known API keys
"""

import os
import sys

import click

from ..credentials import (
    KNOWN_KEYS,
    credentials_path,
    delete_key,
    load_all_keys,
    load_key,
    save_key,
)


def _mask(value: str) -> str:
    """Mask all but the first 6 and last 3 characters of a value.

    Args:
        value: The secret string to mask.

    Returns:
        Masked string, e.g. ``fal_ab...23``.
    """
    if len(value) <= 9:
        return value[:3] + "..." + value[-2:] if len(value) > 5 else "***"
    return value[:6] + "..." + value[-3:]


def _key_source(key_name: str) -> str:
    """Determine where a key's value originates.

    If the env value matches the credentials value, the key was injected
    from credentials — report ``"credentials"`` as the source.

    Returns:
        ``"environment"``, ``"credentials"``, or ``"not set"``.
    """
    cred_value = load_key(key_name)
    env_value = os.environ.get(key_name)
    # Reason: inject_keys() copies credential values into os.environ,
    # so matching values means the source is the credentials file.
    if cred_value and env_value and cred_value == env_value:
        return "credentials"
    if env_value:
        return "environment"
    if cred_value:
        return "credentials"
    return "not set"


# ---------------------------------------------------------------------------
# set-key
# ---------------------------------------------------------------------------

@click.command("set-key")
@click.argument("key_name")
@click.option("--stdin", "use_stdin", is_flag=True, default=False,
              help="Read value from stdin (for piping / automation).")
@click.pass_context
def set_key(ctx, key_name, use_stdin):
    """Store an API key securely.

    KEY_NAME is the environment variable name (e.g. FAL_KEY).
    The value is NEVER passed as a command argument — it is read from an
    interactive hidden prompt (default) or from stdin (--stdin).

    \b
    Examples:
      aicp set-key FAL_KEY                       # interactive prompt
      echo "$FAL_KEY" | aicp set-key FAL_KEY --stdin  # piped input
    """
    out = ctx.obj["output"]

    # Warn on unknown key names
    if key_name not in KNOWN_KEYS:
        out.warning(
            f"'{key_name}' is not a recognised key name. "
            f"Known keys: {', '.join(KNOWN_KEYS)}"
        )

    # Read the value — never from argv
    if use_stdin:
        if sys.stdin.isatty():
            out.error("--stdin requires piped input (stdin is a terminal)")
            ctx.exit(1)
            return
        value = sys.stdin.read().strip()
    else:
        value = click.prompt(f"Enter value for {key_name}", hide_input=True)

    if not value:
        out.error("Empty value — key not saved.")
        ctx.exit(1)
        return

    path = save_key(key_name, value)
    out.info(f"{key_name} saved to {path}")

    if ctx.obj.get("json_mode"):
        out.result(
            {"key": key_name, "saved": True, "path": str(path)},
            command="set-key",
        )


# ---------------------------------------------------------------------------
# get-key
# ---------------------------------------------------------------------------

@click.command("get-key")
@click.argument("key_name")
@click.option("--reveal", is_flag=True, default=False,
              help="Show the full value instead of a masked version.")
@click.pass_context
def get_key(ctx, key_name, reveal):
    """Display a stored API key (masked by default).

    \b
    Examples:
      aicp get-key FAL_KEY            # masked output
      aicp get-key FAL_KEY --reveal   # full value
    """
    out = ctx.obj["output"]
    value = load_key(key_name)
    env_value = os.environ.get(key_name)
    source = _key_source(key_name)

    if ctx.obj.get("json_mode"):
        out.result(
            {
                "key": key_name,
                "set": bool(value or env_value),
                "source": source,
            },
            command="get-key",
        )
        return

    if value:
        display = value if reveal else _mask(value)
        out.info(f"{key_name}={display}  (source: credentials)")
    elif env_value:
        display = env_value if reveal else _mask(env_value)
        out.info(f"{key_name}={display}  (source: environment)")
    else:
        out.info(f"{key_name} is not set")


# ---------------------------------------------------------------------------
# check-keys
# ---------------------------------------------------------------------------

@click.command("check-keys")
@click.pass_context
def check_keys(ctx):
    """Show the status of all known API keys.

    \b
    Examples:
      aicp check-keys
      aicp check-keys --json
    """
    out = ctx.obj["output"]
    rows = []
    for key_name in KNOWN_KEYS:
        source = _key_source(key_name)
        is_set = source != "not set"
        rows.append({"name": key_name, "set": is_set, "source": source})

    if ctx.obj.get("json_mode"):
        out.result({"keys": rows}, command="check-keys")
        return

    for row in rows:
        mark = "set" if row["set"] else "not set"
        icon = "+" if row["set"] else "-"
        source_info = f" ({row['source']})" if row["set"] else ""
        out.info(f"  [{icon}] {row['name']:<25} {mark}{source_info}")

    cred_path = credentials_path()
    out.info(f"\nCredentials file: {cred_path}")


# ---------------------------------------------------------------------------
# delete-key
# ---------------------------------------------------------------------------

@click.command("delete-key")
@click.argument("key_name")
@click.pass_context
def delete_key_cmd(ctx, key_name):
    """Remove a stored API key from the credentials file.

    \b
    Examples:
      aicp delete-key FAL_KEY
    """
    out = ctx.obj["output"]
    removed = delete_key(key_name)

    if ctx.obj.get("json_mode"):
        out.result(
            {"key": key_name, "deleted": removed},
            command="delete-key",
        )
        return

    if removed:
        out.info(f"{key_name} removed from credentials.")
    else:
        out.info(f"{key_name} was not found in credentials.")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_key_commands(cli_group):
    """Register key management commands with the root CLI group."""
    cli_group.add_command(set_key)
    cli_group.add_command(get_key)
    cli_group.add_command(check_keys)
    cli_group.add_command(delete_key_cmd)
