"""Unstage mode: reset index entries back to HEAD state.

Spec format:
{
    "path/to/file.py": "all",       # unstage entire file (reset to HEAD)
    "path/to/new.py": "all"         # unstage new file (remove from index)
}
"""

import os
import stat

from dulwich.repo import Repo
from dulwich.objects import Blob

from repo_utils import get_head_tree, read_blob_from_tree


def _make_index_entry_from_blob(st, blob_id, path: str):
    """Create an index entry matching HEAD state."""
    from dulwich.index import IndexEntry

    name_len = len(path.encode("utf-8")) if path else 0
    flags = min(name_len, 0xFFF)

    return IndexEntry(
        ctime=(int(st.st_ctime), 0),
        mtime=(int(st.st_mtime), 0),
        dev=st.st_dev,
        ino=st.st_ino,
        mode=stat.S_IFREG | 0o644,
        uid=st.st_uid,
        gid=st.st_gid,
        size=st.st_size,
        sha=blob_id,
        flags=flags,
    )


def unstage_spec(repo_path: str, spec: dict) -> dict:
    """Unstage files by resetting index entries to HEAD state.

    For files that exist in HEAD: restore index entry to HEAD blob.
    For new files (not in HEAD): remove from index entirely.

    Returns:
        {"ok": True, "unstaged": {"path": "reset_to_head" | "removed_from_index", ...}}
    """
    repo_path = os.path.abspath(repo_path)
    repo = Repo(repo_path)
    tree = get_head_tree(repo)
    index = repo.open_index()

    unstaged = {}

    for path, action in spec.items():
        if action != "all":
            raise ValueError(f"Unstage only supports 'all' action, got: {action}")

        key = path.encode("utf-8")
        head_bytes = read_blob_from_tree(repo, tree, path)

        if head_bytes is not None:
            # File exists in HEAD — restore index to HEAD blob
            blob = Blob.from_string(head_bytes)
            repo.object_store.add_object(blob)

            full_path = os.path.join(repo_path, path)
            if os.path.isfile(full_path):
                st = os.stat(full_path)
            else:
                # File was deleted in working tree but exists in HEAD
                # Use a minimal stat-like object
                st = os.stat(repo_path)  # fallback

            index[key] = _make_index_entry_from_blob(st, blob.id, path)
            unstaged[path] = "reset_to_head"
        else:
            # New file (not in HEAD) — remove from index
            if key in index:
                del index[key]
            unstaged[path] = "removed_from_index"

    index.write()

    return {"ok": True, "unstaged": unstaged}
