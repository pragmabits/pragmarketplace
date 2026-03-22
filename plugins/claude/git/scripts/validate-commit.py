import re
import sys

DEFAULT_TYPES = ["feat", "fix", "docs", "style", "refactor", "test", "chore", "perf"]

ALLOWED_PUNCTUATION = set(" ,./+-")


def _build_pattern(valid_types: list[str]) -> re.Pattern:
    types_group = "|".join(re.escape(t) for t in valid_types)
    return re.compile(rf"^({types_group})(!?): (.+)$")


def _is_valid_description_char(character: str) -> bool:
    return character.isalpha() or character.isdigit() or character in ALLOWED_PUNCTUATION


def _is_valid_start_char(character: str) -> bool:
    return (character.isalpha() and character.islower()) or character.isdigit()


def validate_commit_message(
    message: str,
    *,
    extra_types: list[str] | None = None,
    allow_body: bool = False,
    max_length: int | None = None,
) -> str | None:
    valid_types = DEFAULT_TYPES + (extra_types or [])
    pattern = _build_pattern(valid_types)
    types_display = " | ".join(valid_types)

    if not message:
        return "commit message is empty"

    # Split subject from body
    if "\n" in message:
        if not allow_body:
            return "commit message must be a single line (no body or footer)"
        # Validate only the subject line
        subject = message.split("\n", 1)[0]
    else:
        subject = message

    match = pattern.match(subject)
    if not match:
        return (
            f"commit message does not match the required format\n"
            f"  received: {subject}\n"
            f"  expected: type: description\n"
            f"  valid types: {types_display}\n"
            f"  description must start with a lowercase letter or digit"
        )

    description = match.group(3)

    if max_length is not None and len(description) > max_length:
        return (
            f"description exceeds maximum length ({len(description)} > {max_length})\n"
            f"  received: {subject}"
        )

    if not _is_valid_start_char(description[0]):
        return (
            f"description must start with a lowercase letter or digit\n"
            f"  received: {subject}"
        )
    for character in description:
        if not _is_valid_description_char(character):
            return (
                f"description contains disallowed character: {character!r}\n"
                f"  received: {subject}\n"
                f"  allowed: Unicode letters, digits, spaces, and , . / + -"
            )

    # Validate body format if present
    if allow_body and "\n" in message:
        parts = message.split("\n", 1)
        body = parts[1]
        # Body must start with a blank line
        if body and not body.startswith("\n"):
            return (
                "body must be separated from subject by a blank line\n"
                f"  received first body line: {body.split(chr(10), 1)[0]}"
            )

    return None


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(
        prog="validate-commit.py",
        description="Validate commit message format",
    )
    ap.add_argument("message", help="Commit message to validate")
    ap.add_argument(
        "--extra-types",
        default="",
        help="Comma-separated list of additional valid types (e.g., build,ci,revert)",
    )
    ap.add_argument(
        "--allow-body",
        action="store_true",
        help="Allow multi-line commit messages with body",
    )
    ap.add_argument(
        "--max-length",
        type=int,
        default=None,
        help="Maximum description length in characters",
    )

    args = ap.parse_args()

    extra = [t.strip() for t in args.extra_types.split(",") if t.strip()] if args.extra_types else None

    validation_error = validate_commit_message(
        args.message,
        extra_types=extra,
        allow_body=args.allow_body,
        max_length=args.max_length,
    )
    if validation_error is not None:
        print(f"error: {validation_error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
