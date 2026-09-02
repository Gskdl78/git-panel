from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field


@dataclass
class GitResult:
    ok: bool
    stdout: str
    stderr: str
    code: int

    @property
    def text(self) -> str:
        return (self.stdout + "\n" + self.stderr).strip()


@dataclass
class FileChange:
    path: str
    index_status: str
    work_status: str

    @property
    def staged(self) -> bool:
        return self.index_status not in (" ", "?")


@dataclass
class RepoStatus:
    branch: str = ""
    ahead: int = 0
    behind: int = 0
    files: list[FileChange] = field(default_factory=list)


@dataclass
class Commit:
    sha: str
    subject: str


_BRANCH_RE = re.compile(r"^## (?:No commits yet on )?(.+?)(?:\.\.\.|$| \[)")


class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def run(self, *args: str) -> GitResult:
        p = subprocess.run(
            ["git", "-c", "core.quotepath=false", "-C", self.repo_path, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return GitResult(p.returncode == 0, p.stdout, p.stderr, p.returncode)

    def is_repo(self) -> bool:
        return self.run("rev-parse", "--is-inside-work-tree").ok

    def status(self) -> RepoStatus:
        res = self.run("status", "--porcelain", "-b")
        st = RepoStatus()
        for line in res.stdout.splitlines():
            if line.startswith("## "):
                m = _BRANCH_RE.match(line)
                if m:
                    st.branch = m.group(1)
                a = re.search(r"ahead (\d+)", line)
                b = re.search(r"behind (\d+)", line)
                st.ahead = int(a.group(1)) if a else 0
                st.behind = int(b.group(1)) if b else 0
            elif line:
                path = line[3:]
                if " -> " in path:
                    path = path.split(" -> ")[1]
                st.files.append(FileChange(path.strip('"'), line[0], line[1]))
        return st

    def stage(self, path: str) -> GitResult:
        return self.run("add", "--", path)

    def unstage(self, path: str) -> GitResult:
        r = self.run("reset", "HEAD", "--", path)
        if not r.ok:  # 還沒有任何 commit 時 HEAD 不存在
            r = self.run("rm", "--cached", "-r", "--", path)
        return r

    def commit(self, message: str) -> GitResult:
        return self.run("commit", "-m", message)

    def log(self, n: int = 30) -> list[Commit]:
        r = self.run("log", f"-{n}", "--pretty=%h\x1f%s")
        return [
            Commit(*line.split("\x1f", 1))
            for line in r.stdout.splitlines()
            if "\x1f" in line
        ]

    def diff_file(self, path: str, staged: bool = False) -> str:
        args = ["diff", "--cached"] if staged else ["diff"]
        return self.run(*args, "--", path).stdout

    def show_commit(self, sha: str) -> str:
        return self.run("show", "--stat", "--patch", sha).stdout
