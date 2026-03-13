"""Hunk-level staging via Dulwich.

Spec format:
{
    "path/to/file.py": "all",                    # stage whole file
    "path/to/other.py": [0, 2],                  # stage hunks by index
    "path/to/deleted.py": "delete"               # stage deletion
}
"""

import difflib
import os
import stat

from dulwich.repo import Repo
from dulwich.objects import Blob


def _decode_safe(data: bytes) -> str | None:
    try:
        return data.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return None


def _get_head_tree(repo: Repo):
    try:
        head_sha = repo.head()
        commit = repo[head_sha]
        return repo[commit.tree]
    except Exception:
        return None


def _read_blob_from_tree(repo: Repo, tree, path: str) -> bytes | None:
    if tree is None:
        return None
    parts = path.split("/")
    current = tree
    for i, part in enumerate(parts):
        found = False
        for item in current.items():
            name = item.path.decode("utf-8") if isinstance(item.path, bytes) else item.path
            if name == part:
                obj = repo[item.sha]
                if i == len(parts) - 1:
                    if isinstance(obj, Blob):
                        return obj.data
                    return None
                else:
                    current = obj
                    found = True
                    break
        if not found:
            return None
    return None


def _compute_hunks(old_lines: list[str], new_lines: list[str]) -> list[tuple[int, int, list[str]]]:
    """Compute hunks as (old_start, old_count, diff_lines) using unified_diff."""
    import re
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    hunks = []
    current_lines = []
    current_old_start = 0
    current_old_count = 0

    for line in diff:
        if line.startswith("@@"):
            if current_lines:
                hunks.append((current_old_start, current_old_count, current_lines))
            m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if m:
                current_old_start = int(m.group(1))
                current_old_count = int(m.group(2)) if m.group(2) else 1
            current_lines = []
        elif line.startswith("---") or line.startswith("+++"):
            continue
        elif current_lines is not None or line.startswith((" ", "+", "-")):
            if current_lines is None:
                current_lines = []
            current_lines.append(line)

    if current_lines:
        hunks.append((current_old_start, current_old_count, current_lines))

    return hunks


def _apply_hunks(old_lines: list[str], hunks: list[tuple[int, int, list[str]]], selected_indices: list[int]) -> list[str]:
    """Apply selected hunks to old_lines, producing new content.

    For each selected hunk, apply its changes. For non-selected hunks,
    keep the original lines.
    """
    # Build a map: old line number -> list of new lines to insert
    # Process all hunks, applying only selected ones
    result = []
    old_pos = 0  # 0-indexed position in old_lines

    all_hunks = list(enumerate(hunks))

    for hunk_idx, (old_start, old_count, diff_lines) in all_hunks:
        # old_start is 1-indexed
        hunk_old_start = old_start - 1 if old_start > 0 else 0

        # Copy lines before this hunk
        while old_pos < hunk_old_start and old_pos < len(old_lines):
            result.append(old_lines[old_pos])
            old_pos += 1

        if hunk_idx in selected_indices:
            # Apply this hunk: use + and context lines, skip - lines
            for line in diff_lines:
                if line.startswith("+"):
                    result.append(line[1:])
                elif line.startswith("-"):
                    old_pos += 1  # skip removed line
                elif line.startswith(" "):
                    result.append(line[1:])
                    old_pos += 1
        else:
            # Don't apply: keep original lines
            for line in diff_lines:
                if line.startswith("-") or line.startswith(" "):
                    if old_pos < len(old_lines):
                        result.append(old_lines[old_pos])
                        old_pos += 1

    # Copy remaining lines
    while old_pos < len(old_lines):
        result.append(old_lines[old_pos])
        old_pos += 1

    return result


def _stage_whole_file(repo: Repo, repo_path: str, path: str) -> str:
    """Stage entire file content from working tree."""
    full_path = os.path.join(repo_path, path)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(full_path, "rb") as f:
        content = f.read()

    blob = Blob.from_string(content)
    repo.object_store.add_object(blob)

    index = repo.open_index()
    st = os.stat(full_path)
    index[path.encode("utf-8")] = index.get_changes_as_new_entry(
        path.encode("utf-8"), blob.id, st
    ) if hasattr(index, "get_changes_as_new_entry") else _make_index_entry(st, blob.id)
    index.write()

    return blob.id.decode("ascii") if isinstance(blob.id, bytes) else str(blob.id)


def _make_index_entry(st, blob_id, *, blob_size: int | None = None, smudge: bool = False):
    """Create an index entry tuple compatible with Dulwich.

    When smudge=True, set mtime/ctime to 0 to force git to compare blob
    content rather than relying on stat cache (avoids racy-git when index
    content differs from working tree).
    """
    from dulwich.index import IndexEntry

    if smudge:
        ctime = (0, 0)
        mtime = (0, 0)
    else:
        ctime = (int(st.st_ctime), 0)
        mtime = (int(st.st_mtime), 0)

    return IndexEntry(
        ctime=ctime,
        mtime=mtime,
        dev=st.st_dev,
        ino=st.st_ino,
        mode=stat.S_IFREG | 0o644,
        uid=st.st_uid,
        gid=st.st_gid,
        size=blob_size if blob_size is not None else st.st_size,
        sha=blob_id,
        flags=min(len(blob_id), 0xFFF) if isinstance(blob_id, str) else 0,
    )


def _stage_deletion(repo: Repo, repo_path: str, path: str) -> None:
    """Stage file deletion."""
    index = repo.open_index()
    key = path.encode("utf-8")
    if key in index:
        del index[key]
        index.write()


def _stage_hunks(repo: Repo, repo_path: str, tree, path: str, hunk_indices: list[int]) -> str:
    """Stage specific hunks of a file."""
    # Read HEAD content
    head_bytes = _read_blob_from_tree(repo, tree, path)
    head_text = _decode_safe(head_bytes) if head_bytes is not None else ""
    old_lines = (head_text or "").splitlines()

    # Read working tree content
    full_path = os.path.join(repo_path, path)
    with open(full_path, "r") as f:
        new_text = f.read()
    new_lines = new_text.splitlines()

    # Compute hunks
    hunks = _compute_hunks(old_lines, new_lines)
    if not hunks:
        raise ValueError(f"No hunks found for {path}")

    # Validate indices
    for idx in hunk_indices:
        if idx < 0 or idx >= len(hunks):
            raise ValueError(f"Hunk index {idx} out of range (0-{len(hunks)-1}) for {path}")

    # Apply selected hunks to HEAD content
    staged_lines = _apply_hunks(old_lines, hunks, hunk_indices)
    staged_content = "\n".join(staged_lines)
    if new_text.endswith("\n"):
        staged_content += "\n"

    # Create blob and update index
    staged_bytes = staged_content.encode("utf-8")
    blob = Blob.from_string(staged_bytes)
    repo.object_store.add_object(blob)

    index = repo.open_index()
    st = os.stat(full_path)
    # Use smudge=True to force git to read blob content instead of
    # trusting stat cache (staged content differs from working tree).
    index[path.encode("utf-8")] = _make_index_entry(
        st, blob.id, blob_size=len(staged_bytes), smudge=True,
    )
    index.write()

    return blob.id.decode("ascii") if isinstance(blob.id, bytes) else str(blob.id)


def stage_spec(repo_path: str, spec: dict) -> dict:
    """Stage files according to spec.

    Returns:
        {"ok": True, "staged": {"path": "sha_or_deleted", ...}}
    """
    repo_path = os.path.abspath(repo_path)
    repo = Repo(repo_path)
    tree = _get_head_tree(repo)

    staged = {}

    for path, action in spec.items():
        if action == "all":
            sha = _stage_whole_file(repo, repo_path, path)
            staged[path] = sha
        elif action == "delete":
            _stage_deletion(repo, repo_path, path)
            staged[path] = "deleted"
        elif isinstance(action, list):
            sha = _stage_hunks(repo, repo_path, tree, path, action)
            staged[path] = sha
        else:
            raise ValueError(f"Unknown action for {path}: {action}")

    return {"ok": True, "staged": staged}
