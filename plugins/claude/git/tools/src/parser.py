"""Parse mode: read-only repository analysis.

Returns JSON with branch, recent commits, file statuses, and unified diffs
split into hunks.
"""

import difflib
import os

from dulwich.repo import Repo
from dulwich.objects import Blob


def _decode_safe(data: bytes) -> str | None:
    """Decode bytes to str, return None for binary content."""
    try:
        return data.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return None


def _get_head_tree(repo: Repo):
    """Return the tree object for HEAD, or None if no commits yet."""
    try:
        head_sha = repo.head()
        commit = repo[head_sha]
        return repo[commit.tree]
    except Exception:
        return None


def _read_blob_from_tree(repo: Repo, tree, path: str) -> bytes | None:
    """Read file content from a tree by path."""
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


def _parse_hunk_header(header: str) -> dict:
    """Parse @@ -old_start,old_count +new_start,new_count @@ into dict."""
    import re
    m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)", header)
    if not m:
        return {"header": header, "old_start": 0, "old_count": 0, "new_start": 0, "new_count": 0}
    return {
        "header": header.strip(),
        "old_start": int(m.group(1)),
        "old_count": int(m.group(2)) if m.group(2) else 1,
        "new_start": int(m.group(3)),
        "new_count": int(m.group(4)) if m.group(4) else 1,
    }


def _compute_hunks(old_content: str | None, new_content: str | None) -> list[dict]:
    """Compute unified diff hunks between old and new content."""
    old_lines = (old_content or "").splitlines(keepends=True)
    new_lines = (new_content or "").splitlines(keepends=True)

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    if not diff:
        return []

    hunks = []
    current_hunk = None

    for line in diff:
        if line.startswith("@@"):
            if current_hunk is not None:
                hunks.append(current_hunk)
            header_info = _parse_hunk_header(line)
            current_hunk = {
                "index": len(hunks),
                **header_info,
                "lines": [],
            }
        elif line.startswith("---") or line.startswith("+++"):
            continue
        elif current_hunk is not None:
            # Strip trailing newline for clean JSON output
            current_hunk["lines"].append(line.rstrip("\n"))

    if current_hunk is not None:
        hunks.append(current_hunk)

    return hunks


def _file_status(in_index: bool, in_workdir: bool, old_content: bytes | None, new_content: bytes | None) -> str:
    """Determine file status string."""
    if not in_index and in_workdir:
        return "untracked"
    if in_index and not in_workdir:
        return "deleted"
    if old_content != new_content:
        return "modified"
    return "clean"


def _get_index_entries(repo: Repo) -> dict[str, bytes]:
    """Return dict of path -> sha from the index."""
    index = repo.open_index()
    entries = {}
    for path in index:
        decoded = path.decode("utf-8") if isinstance(path, bytes) else path
        entries[decoded] = index[path].sha
    return entries


def _get_staged_status(repo: Repo, tree, path: str, index_entries: dict) -> bool:
    """Check if a file has staged content (index differs from HEAD)."""
    if path not in index_entries:
        return False
    index_sha = index_entries[path]
    head_content = _read_blob_from_tree(repo, tree, path)
    if head_content is None:
        return True  # new file staged
    # Compare HEAD blob sha with index sha
    head_blob = Blob.from_string(head_content)
    return head_blob.id != index_sha


def parse_repo(repo_path: str) -> dict:
    """Parse repository state and return JSON-serializable dict."""
    repo_path = os.path.abspath(repo_path)
    repo = Repo(repo_path)

    # Branch
    try:
        ref = repo.refs.get_symrefs().get(b"HEAD", b"")
        branch = ref.decode("utf-8").replace("refs/heads/", "") if ref else "HEAD"
    except Exception:
        branch = "unknown"

    # HEAD tree
    tree = _get_head_tree(repo)

    # Recent commits
    recent_commits = []
    try:
        head_sha = repo.head()
        walker = repo.get_walker(include=[head_sha], max_entries=10)
        for entry in walker:
            c = entry.commit
            msg = c.message.decode("utf-8", errors="replace").split("\n")[0]
            recent_commits.append({
                "hash": c.id.decode("utf-8")[:7] if isinstance(c.id, bytes) else str(c.id)[:7],
                "message": msg,
            })
    except Exception:
        pass

    # Index entries
    index_entries = _get_index_entries(repo)

    # Check for staged content
    has_staged_content = False
    for path in index_entries:
        if _get_staged_status(repo, tree, path, index_entries):
            has_staged_content = True
            break

    # Collect all known paths
    all_paths = set()

    # From HEAD tree
    if tree is not None:
        def _walk_tree(t, prefix=""):
            for item in t.items():
                name = item.path.decode("utf-8") if isinstance(item.path, bytes) else item.path
                full = f"{prefix}{name}" if not prefix else f"{prefix}/{name}"
                obj = repo[item.sha]
                if isinstance(obj, Blob):
                    all_paths.add(full)
                else:
                    _walk_tree(obj, full)
        _walk_tree(tree)

    # From index
    all_paths.update(index_entries.keys())

    # From working directory (untracked)
    for root, dirs, filenames in os.walk(repo_path):
        # Skip .git directory
        dirs[:] = [d for d in dirs if d != ".git"]
        for fname in filenames:
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, repo_path)
            all_paths.add(rel)

    # Build file info, skipping .git paths
    files = {}
    for path in sorted(all_paths):
        if path.startswith(".git/") or path == ".git":
            continue

        # HEAD content
        head_bytes = _read_blob_from_tree(repo, tree, path)
        head_text = _decode_safe(head_bytes) if head_bytes is not None else None

        # Working tree content
        workdir_path = os.path.join(repo_path, path)
        if os.path.isfile(workdir_path):
            try:
                with open(workdir_path, "rb") as f:
                    work_bytes = f.read()
                work_text = _decode_safe(work_bytes)
            except (IOError, OSError):
                work_bytes = None
                work_text = None
        else:
            work_bytes = None
            work_text = None

        in_index = path in index_entries
        in_workdir = work_bytes is not None

        status = _file_status(in_index or head_bytes is not None, in_workdir, head_bytes, work_bytes)
        if status == "clean":
            continue

        is_staged = _get_staged_status(repo, tree, path, index_entries) if in_index else False

        # Compute hunks (HEAD vs working tree for unstaged, HEAD vs index for staged)
        if work_text is None and head_text is None:
            # Binary or inaccessible
            hunks = []
            is_binary = True
        else:
            hunks = _compute_hunks(head_text, work_text)
            is_binary = False

        file_info = {
            "status": status,
            "in_index": is_staged,
            "hunks": hunks,
        }
        if is_binary:
            file_info["binary"] = True

        files[path] = file_info

    return {
        "ok": True,
        "branch": branch,
        "has_staged_content": has_staged_content,
        "recent_commits": recent_commits,
        "files": files,
    }
