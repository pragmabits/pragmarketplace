import re
import sys

STRUCTURE_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|test|chore|perf): (.+)$"
)

ALLOWED_PUNCTUATION = set(" ,./+-")


def _is_valid_description_char(character: str) -> bool:
    return character.isalpha() or character.isdigit() or character in ALLOWED_PUNCTUATION


def _is_valid_start_char(character: str) -> bool:
    return (character.isalpha() and character.islower()) or character.isdigit()


def validate_commit_message(message: str) -> str | None:
    if not message:
        return "commit message is empty"
    if "\n" in message:
        return "commit message must be a single line (no body or footer)"
    match = STRUCTURE_PATTERN.match(message)
    if not match:
        return (
            f"commit message does not match the required format\n"
            f"  received: {message}\n"
            f"  expected: type: description\n"
            f"  valid types: feat | fix | docs | style | refactor | test | chore | perf\n"
            f"  description must start with a lowercase letter or digit"
        )
    description = match.group(2)
    if not _is_valid_start_char(description[0]):
        return (
            f"description must start with a lowercase letter or digit\n"
            f"  received: {message}"
        )
    for character in description:
        if not _is_valid_description_char(character):
            return (
                f"description contains disallowed character: {character!r}\n"
                f"  received: {message}\n"
                f"  allowed: Unicode letters, digits, spaces, and , . / + -"
            )
    return None


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: validate-commit.py <commit-message>", file=sys.stderr)
        sys.exit(1)
    commit_message = sys.argv[1]
    validation_error = validate_commit_message(commit_message)
    if validation_error is not None:
        print(f"error: {validation_error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
