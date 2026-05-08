"""Generate a simple pull-request review summary for changed files."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import re


RULES: tuple[dict[str, object], ...] = (
    {
        "severity": "high",
        "title": "Avoid dynamic code execution",
        "pattern": re.compile(r"\b(?:eval|exec)\s*\("),
        "message": "Use explicit functions or parsers instead of eval/exec.",
        "extensions": {".py"},
    },
    {
        "severity": "high",
        "title": "Avoid subprocess shell=True",
        "pattern": re.compile(r"\bsubprocess\.[A-Za-z_]+\([^#\n]*\bshell\s*=\s*True\b"),
        "message": "Pass arguments as a list instead of invoking a shell.",
        "extensions": {".py"},
    },
    {
        "severity": "medium",
        "title": "Avoid bare except blocks",
        "pattern": re.compile(r"^\s*except\s*:\s*$", re.MULTILINE),
        "message": "Catch specific exceptions so failures stay reviewable.",
        "extensions": {".py"},
    },
    {
        "severity": "low",
        "title": "Review TODO/FIXME/HACK markers",
        "pattern": re.compile(r"(?mi)^\s*(?:#|//|/\*+|<!--|- \[)\s*(?:TODO|FIXME|HACK)\b"),
        "message": "Resolve or justify remaining work before merging.",
        "extensions": {".py", ".md", ".yml", ".yaml"},
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--base-sha")
    parser.add_argument("--head-sha")
    parser.add_argument("--summary-file", required=True)
    parser.add_argument("--files", nargs="*")
    return parser.parse_args()


def git_changed_files(repo_root: Path, base_sha: str, head_sha: str) -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            base_sha,
            head_sha,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for raw_path in result.stdout.splitlines():
        path = repo_root / raw_path.strip()
        if path.is_file():
            files.append(path)
    return files


def line_number_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def collect_findings(files: list[Path], repo_root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in files:
        suffix = path.suffix.lower()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if path.as_posix().endswith((".github/workflows/pr-review.yml", ".github/workflows/pr-review.yaml")):
            if "pull_request_target" in text and "actions/checkout" in text:
                findings.append(
                    {
                        "severity": "high",
                        "path": path.relative_to(repo_root).as_posix(),
                        "line": 1,
                        "title": "Avoid pull_request_target with code checkout",
                        "message": "This combination can expose write tokens to untrusted PR code.",
                    }
                )

        for rule in RULES:
            allowed_extensions = rule["extensions"]
            if suffix not in allowed_extensions:
                continue
            pattern = rule["pattern"]
            for match in pattern.finditer(text):
                findings.append(
                    {
                        "severity": rule["severity"],
                        "path": path.relative_to(repo_root).as_posix(),
                        "line": line_number_for_offset(text, match.start()),
                        "title": rule["title"],
                        "message": rule["message"],
                    }
                )
    findings.sort(
        key=lambda item: (
            {"high": 0, "medium": 1, "low": 2}[str(item["severity"])],
            str(item["path"]),
            int(item["line"]),
        )
    )
    return findings


def build_summary(files: list[Path], findings: list[dict[str, object]], repo_root: Path) -> str:
    changed = [path.relative_to(repo_root).as_posix() for path in files]
    lines = ["### Scope", ""]
    if changed:
        for path in changed:
            lines.append(f"- `{path}`")
    else:
        lines.append("- No changed files were detected for review.")

    lines.extend(["", "### Findings", ""])
    if not findings:
        lines.append("- No findings from the current review rules.")
        return "\n".join(lines) + "\n"

    lines.append("| Severity | File | Line | Rule | Recommendation |")
    lines.append("| --- | --- | ---: | --- | --- |")
    for finding in findings:
        lines.append(
            "| {severity} | `{path}` | {line} | {title} | {message} |".format(
                severity=str(finding["severity"]).upper(),
                path=str(finding["path"]),
                line=int(finding["line"]),
                title=str(finding["title"]),
                message=str(finding["message"]),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    if args.files:
        files = [(repo_root / path).resolve() for path in args.files]
        files = [path for path in files if path.is_file()]
    elif args.base_sha and args.head_sha:
        files = git_changed_files(repo_root, args.base_sha, args.head_sha)
    else:
        raise ValueError("Either --files or both --base-sha and --head-sha must be provided.")

    findings = collect_findings(files, repo_root)
    summary = build_summary(files, findings, repo_root)
    Path(args.summary_file).write_text(summary, encoding="utf-8")
    return 1 if any(finding["severity"] == "high" for finding in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
