"""Shared utilities for git repository operations via Dulwich."""

from dulwich.repo import Repo
from dulwich.objects import Blob


def decode_safe(data: bytes) -> str | None:
    """Decode bytes to str, return None for binary content."""
    try:
        return data.decode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return None


def get_head_tree(repo: Repo):
    """Return the tree object for HEAD, or None if no commits yet."""
    try:
        head_sha = repo.head()
        commit = repo[head_sha]
        return repo[commit.tree]
    except Exception:
        return None


def read_blob_from_tree(repo: Repo, tree, path: str) -> bytes | None:
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
