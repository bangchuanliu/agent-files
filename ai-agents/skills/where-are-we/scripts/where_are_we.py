"""Long-horizon project status: what am I in the middle of, across days and weeks?

Reads hand-written status files under $WAW_ROOT (default ~/.where-are-we), derives
everything derivable from git / gh / the worktree tree, and reports one verdict per
project. Also surfaces in-flight markdown (plan.md and friends) found under
$WTREE_ROOT/*/* that no status file has adopted yet.

Read-only except for the explicit `update` subcommand.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WAW_ROOT = Path(os.environ.get("WAW_ROOT", "~/.where-are-we")).expanduser()
WTREE_ROOT = Path(os.environ.get("WTREE_ROOT", "~/.worktree")).expanduser()
STALE_DAYS = int(os.environ.get("WAW_STALE_DAYS", "21"))
OWNER = os.environ.get("WTREE_BRANCH_PREFIX", os.environ.get("USER", ""))

# Markdown filenames that are in-flight thinking even when committed.
NOTE_NAMES = {"plan.md", "notes.md", "todo.md", "status.md", "design.md", "spec.md"}
SKIP_NOTES = {"readme.md", "changelog.md", "license.md", "contributing.md", "agents.md"}

VERDICT_ORDER = ["orphan", "pick-up", "review", "wrap-up", "waiting", "paused", "done"]
KNOWN_STATUS = ["active", "paused", "blocked", "done"]


# ---------------------------------------------------------------- shell helpers

def run(cmd: list[str], cwd: str | None = None, timeout: int = 25) -> tuple[int, str]:
    """Run a command, fully buffered. Never pipes a producer into a consumer."""
    try:
        res = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)
    return res.returncode, (res.stdout or "").strip()


def git(path: Path, *args: str) -> str:
    code, out = run(["git", "-C", str(path), *args])
    return out if code == 0 else ""


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_date(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw[: len(fmt) + 4], fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw).astimezone(timezone.utc)
    except ValueError:
        return None


def age_days(when: datetime | None) -> float | None:
    if when is None:
        return None
    return (now() - when).total_seconds() / 86400.0


def fmt_age(when: datetime | None) -> str:
    d = age_days(when)
    if d is None:
        return "-"
    if d < 1:
        return "today"
    if d < 2:
        return "1d"
    if d < 45:
        return f"{int(d)}d"
    return f"{int(d / 7)}w"


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s


def strip_owner(name: str) -> str:
    for prefix in (f"{OWNER}-", f"{OWNER}/"):
        if prefix and name.startswith(prefix):
            return name[len(prefix):]
    return name


# ------------------------------------------------------------- frontmatter I/O

LIST_KEYS = {"worktrees", "branches", "prs", "links", "repos"}


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Minimal YAML-subset frontmatter: `key: value` and `- item` lists."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    meta: dict[str, Any] = {}
    key: str | None = None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and key:
            meta.setdefault(key, [])
            if isinstance(meta[key], list):
                meta[key].append(line.lstrip()[2:].strip().strip('"').strip("'"))
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1).strip(), m.group(2).strip()
        value = value.strip('"').strip("'")
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            meta[key] = [v for v in items if v]
        elif value == "":
            meta[key] = [] if key in LIST_KEYS else ""
        else:
            meta[key] = value
    return meta, "\n".join(lines[end + 1:]).lstrip("\n")


def render_front_matter(meta: dict[str, Any]) -> str:
    order = ["project", "status", "next", "started", "updated",
             "repos", "worktrees", "branches", "prs", "links"]
    keys = [k for k in order if k in meta] + [k for k in meta if k not in order]
    out = ["---"]
    for k in keys:
        v = meta[k]
        if isinstance(v, list):
            out.append(f"{k}:")
            out.extend(f"  - {item}" for item in v)
        else:
            out.append(f"{k}: {v}")
    out.append("---")
    return "\n".join(out)


# ----------------------------------------------------------------- data model

@dataclass
class Worktree:
    path: Path
    repo: str
    dirname: str
    exists: bool = True
    branch: str = ""
    dirty: int = 0
    unpushed: int = 0
    last_commit: datetime | None = None
    notes: list[Path] = field(default_factory=list)
    prs: list[dict[str, Any]] = field(default_factory=list)
    claimed_by: str | None = None


@dataclass
class Project:
    slug: str
    file: Path
    meta: dict[str, Any]
    body: str
    worktrees: list[Worktree] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    verdict: str = "pick-up"
    reason: str = ""
    last_activity: datetime | None = None

    @property
    def status(self) -> str:
        return str(self.meta.get("status") or "active").lower()

    @property
    def next_action(self) -> str:
        return str(self.meta.get("next") or "").strip()


# ------------------------------------------------------------------ discovery

def scan_worktrees() -> list[Worktree]:
    found: list[Worktree] = []
    if not WTREE_ROOT.is_dir():
        return found
    for repo_dir in sorted(p for p in WTREE_ROOT.iterdir() if p.is_dir()):
        for wt in sorted(p for p in repo_dir.iterdir() if p.is_dir()):
            found.append(inspect_worktree(wt))
    return found


def inspect_worktree(path: Path) -> Worktree:
    wt = Worktree(path=path, repo=path.parent.name, dirname=path.name)
    if not path.is_dir():
        wt.exists = False
        return wt
    # Never parse the branch out of the directory name; the path slug is lossy.
    wt.branch = git(path, "rev-parse", "--abbrev-ref", "HEAD")
    porcelain = git(path, "status", "--porcelain")
    wt.dirty = len([l for l in porcelain.splitlines() if l.strip()])
    unpushed = git(path, "rev-list", "--count", "HEAD", "--not", "--remotes")
    wt.unpushed = int(unpushed) if unpushed.isdigit() else 0
    ts = git(path, "log", "-1", "--format=%cI")
    wt.last_commit = parse_date(ts)
    wt.notes = find_notes(path, porcelain)
    return wt


def find_notes(path: Path, porcelain: str) -> list[Path]:
    """In-flight markdown: well-known note names at top level, plus any dirty or
    untracked .md anywhere in the worktree. Committed, unchanged repo docs are
    repo content, not work in progress."""
    notes: dict[str, Path] = {}
    for child in sorted(path.glob("*.md")):
        name = child.name.lower()
        if name in NOTE_NAMES:
            notes[str(child)] = child
    for line in porcelain.splitlines():
        rel = line[3:].strip().strip('"')
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        if not rel.lower().endswith(".md"):
            continue
        if Path(rel).name.lower() in SKIP_NOTES:
            continue
        candidate = path / rel
        if candidate.is_file():
            notes[str(candidate)] = candidate
    return sorted(notes.values())


def load_projects() -> list[Project]:
    projects: list[Project] = []
    if not WAW_ROOT.is_dir():
        return projects
    for f in sorted(WAW_ROOT.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        meta, body = parse_front_matter(text)
        slug = str(meta.get("project") or f.stem)
        meta.setdefault("project", slug)
        projects.append(Project(slug=slug, file=f, meta=meta, body=body))
    return projects


def link(projects: list[Project], worktrees: list[Worktree]) -> None:
    """Attach worktrees to projects: explicit frontmatter first, then slug match."""
    by_path = {str(w.path): w for w in worktrees}
    for proj in projects:
        claimed: list[Worktree] = []
        for raw in as_list(proj.meta.get("worktrees")):
            p = Path(os.path.expanduser(raw))
            if str(p) in by_path:
                claimed.append(by_path[str(p)])
            elif p.is_dir():
                claimed.append(inspect_worktree(p))
            else:
                proj.missing.append(str(p))
        wanted_branches = {b.strip() for b in as_list(proj.meta.get("branches")) if b.strip()}
        for w in worktrees:
            if w in claimed:
                continue
            if w.branch and (w.branch in wanted_branches
                             or strip_owner(w.branch) == proj.slug
                             or strip_owner(w.dirname) == proj.slug):
                claimed.append(w)
        for b in wanted_branches:
            if not any(w.branch == b for w in claimed):
                proj.missing.append(f"branch {b}")
        for w in claimed:
            w.claimed_by = proj.slug
        proj.worktrees = claimed


def as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    return [s.strip() for s in str(value).split(",") if s.strip()]


# ------------------------------------------------------------------ PR lookup

def attach_prs(worktrees: list[Worktree]) -> None:
    for w in worktrees:
        if not w.exists or not w.branch or w.branch == "HEAD":
            continue
        code, out = run(
            ["gh", "pr", "list", "--head", w.branch, "--state", "all",
             "--limit", "10", "--json", "number,state,url,title,isDraft"],
            cwd=str(w.path), timeout=45,
        )
        if code != 0 or not out:
            w.prs = []
            continue
        try:
            w.prs = json.loads(out)
        except ValueError:
            w.prs = []


# -------------------------------------------------------------------- verdict

def decide(proj: Project) -> None:
    declared = parse_date(str(proj.meta.get("updated") or ""))
    acts: list[datetime | None] = [declared]
    for w in proj.worktrees:
        acts.append(w.last_commit)
        for n in w.notes:
            try:
                acts.append(datetime.fromtimestamp(n.stat().st_mtime, tz=timezone.utc))
            except OSError:
                pass
    if declared is None:
        # Only fall back to the file's own mtime when no `updated:` was written;
        # otherwise a stray touch would make a dead project look alive.
        try:
            acts.append(datetime.fromtimestamp(proj.file.stat().st_mtime, tz=timezone.utc))
        except OSError:
            pass
    real = [a for a in acts if a]
    proj.last_activity = max(real) if real else None

    dirty = sum(w.dirty for w in proj.worktrees)
    unpushed = sum(w.unpushed for w in proj.worktrees)
    prs = [pr for w in proj.worktrees for pr in w.prs]
    open_prs = [pr for pr in prs if str(pr.get("state", "")).upper() == "OPEN"]
    days = age_days(proj.last_activity)

    local = ""
    if dirty or unpushed:
        local = f" [{dirty} uncommitted, {unpushed} unpushed]"

    # Declared intent wins over inferred state: a human who wrote `paused` or
    # `blocked` knows something git does not.
    if proj.status == "done":
        proj.verdict, proj.reason = "done", "marked done"
    elif proj.missing:
        proj.verdict = "orphan"
        proj.reason = f"referenced but gone: {', '.join(proj.missing[:3])}{local}"
    elif proj.status == "blocked":
        proj.verdict = "waiting"
        proj.reason = (proj.next_action or "marked blocked") + local
    elif proj.status == "paused":
        proj.verdict = "paused"
        proj.reason = (proj.next_action or "paused on purpose") + local
    elif dirty or unpushed:
        proj.verdict = "pick-up"
        proj.reason = (proj.next_action + " -" if proj.next_action else "") + \
            f" {dirty} uncommitted file(s), {unpushed} unpushed commit(s)"
    elif open_prs:
        proj.verdict = "waiting"
        proj.reason = "PR open: " + ", ".join(str(pr.get("url", "")) for pr in open_prs[:2])
    elif prs:
        proj.verdict = "wrap-up"
        proj.reason = "every PR closed or merged, tree clean - mark done"
    elif days is not None and days >= STALE_DAYS:
        proj.verdict = "review"
        proj.reason = f"no activity for {int(days)}d - still alive, or pause it?"
    else:
        proj.verdict = "pick-up"
        proj.reason = proj.next_action or "active, no recorded next step"


# --------------------------------------------------------------------- render

def truncate(text: str, width: int) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= width else text[: width - 1] + "\u2026"


def table(headers: list[str], rows: list[list[str]], widths: list[int]) -> str:
    cells = [[truncate(c, w) for c, w in zip(row, widths)] for row in rows]
    widths = [max(len(h), *(len(r[i]) for r in cells)) if cells else len(h)
              for i, h in enumerate(headers)]

    def line(l: str, m: str, r: str) -> str:
        return l + m.join("\u2500" * (w + 2) for w in widths) + r

    def row(vals: list[str]) -> str:
        return "\u2502 " + " \u2502 ".join(v.ljust(w) for v, w in zip(vals, widths)) + " \u2502"

    out = [line("\u250c", "\u252c", "\u2510"), row(headers), line("\u251c", "\u253c", "\u2524")]
    out.extend(row(c) for c in cells)
    out.append(line("\u2514", "\u2534", "\u2518"))
    return "\n".join(out)


def where_label(proj: Project) -> str:
    if not proj.worktrees:
        return "(no worktree)"
    parts = [f"{w.repo}:{w.branch or '?'}" for w in proj.worktrees]
    return ", ".join(parts)


def git_label(proj: Project) -> str:
    if not proj.worktrees:
        return "-"
    dirty = sum(w.dirty for w in proj.worktrees)
    unpushed = sum(w.unpushed for w in proj.worktrees)
    bits = []
    if dirty:
        bits.append(f"dirty({dirty})")
    if unpushed:
        bits.append(f"unpushed({unpushed})")
    return " ".join(bits) if bits else "clean"


def pr_label(proj: Project, pr_on: bool) -> str:
    if not pr_on:
        return "-"
    prs = [pr for w in proj.worktrees for pr in w.prs]
    if not prs:
        return "none"
    states: dict[str, int] = {}
    for pr in prs:
        s = str(pr.get("state", "?")).lower()
        states[s] = states.get(s, 0) + 1
    return " ".join(f"{v}{k[:4]}" for k, v in sorted(states.items()))


def report(projects: list[Project], orphan_notes: list[Worktree], pr_on: bool,
           show_all: bool) -> str:
    out: list[str] = []
    visible = [p for p in projects if show_all or p.verdict != "done"]
    visible.sort(key=lambda p: (VERDICT_ORDER.index(p.verdict),
                                -(age_days(p.last_activity) or 0)))
    if visible:
        rows = [[p.slug, p.status, fmt_age(p.last_activity), where_label(p),
                 git_label(p), pr_label(p, pr_on), p.verdict] for p in visible]
        out.append(table(
            ["Project", "Status", "Last touch", "Where", "Git", "PR", "Next step"],
            rows, [24, 8, 10, 40, 18, 12, 9]))
    else:
        out.append(f"No project status files in {WAW_ROOT}.")
        out.append("Create one:  where-are-we update <slug> --next \"...\"")

    attention = [p for p in visible if p.verdict in ("orphan", "pick-up", "review", "wrap-up")]
    if attention:
        out.append("")
        for p in attention:
            out.append(f"  {p.verdict:<8} {p.slug}: {p.reason}")
            if p.next_action and p.verdict != "pick-up":
                out.append(f"           next: {p.next_action}")

    if orphan_notes:
        out.append("")
        out.append("Unadopted work in progress (markdown under a worktree, no status file):")
        rows = []
        for w in orphan_notes:
            for n in w.notes:
                try:
                    mt = datetime.fromtimestamp(n.stat().st_mtime, tz=timezone.utc)
                except OSError:
                    mt = None
                rel = str(n.relative_to(w.path))
                rows.append([f"{w.repo}:{w.branch or '?'}", rel, fmt_age(mt),
                             f"where-are-we update {strip_owner(w.branch or w.dirname)}"])
        out.append(table(["Where", "File", "Touched", "Adopt with"], rows,
                         [40, 28, 10, 46]))
    return "\n".join(out)


def to_json(projects: list[Project], orphan_notes: list[Worktree]) -> str:
    payload = {
        "root": str(WAW_ROOT),
        "generated_at": now().isoformat(),
        "projects": [
            {
                "project": p.slug,
                "file": str(p.file),
                "status": p.status,
                "next": p.next_action,
                "verdict": p.verdict,
                "reason": p.reason,
                "last_activity": p.last_activity.isoformat() if p.last_activity else None,
                "stale_days": round(age_days(p.last_activity), 1) if p.last_activity else None,
                "missing": p.missing,
                "worktrees": [
                    {
                        "path": str(w.path), "repo": w.repo, "branch": w.branch,
                        "dirty": w.dirty, "unpushed": w.unpushed,
                        "last_commit": w.last_commit.isoformat() if w.last_commit else None,
                        "notes": [str(n) for n in w.notes],
                        "prs": w.prs,
                    } for w in p.worktrees
                ],
            } for p in projects
        ],
        "unadopted": [
            {"path": str(w.path), "repo": w.repo, "branch": w.branch,
             "notes": [str(n) for n in w.notes]}
            for w in orphan_notes
        ],
    }
    return json.dumps(payload, indent=2)


# -------------------------------------------------------------------- update

TEMPLATE_BODY = """## Why

(one paragraph: what problem this project solves, for a reader who forgot)

## Log

"""


def cmd_update(args: argparse.Namespace) -> int:
    WAW_ROOT.mkdir(parents=True, exist_ok=True)
    slug = slugify(args.project)
    if not slug:
        print("where-are-we update: empty project slug", file=sys.stderr)
        return 2
    path = WAW_ROOT / f"{slug}.md"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if path.exists():
        meta, body = parse_front_matter(path.read_text(encoding="utf-8", errors="replace"))
        created = False
    else:
        meta, body = {"project": slug, "status": "active", "started": stamp}, TEMPLATE_BODY
        created = True
    meta["project"] = slug
    meta.setdefault("status", "active")
    meta.setdefault("started", stamp)

    if args.status:
        if args.status not in KNOWN_STATUS:
            print(f"status must be one of {', '.join(KNOWN_STATUS)}", file=sys.stderr)
            return 2
        meta["status"] = args.status
    if args.next is not None:
        meta["next"] = args.next
    for key, values in (("worktrees", args.worktree), ("branches", args.branch),
                        ("prs", args.pr), ("links", args.link), ("repos", args.repo)):
        if not values:
            continue
        current = as_list(meta.get(key))
        for v in values:
            v = os.path.abspath(os.path.expanduser(v)) if key == "worktrees" else v
            if v not in current:
                current.append(v)
        meta[key] = current
    meta["updated"] = stamp

    if args.note:
        if "## Log" not in body:
            body = body.rstrip() + "\n\n## Log\n\n"
        body = body.rstrip() + f"\n- {stamp} - {args.note}\n"

    path.write_text(render_front_matter(meta) + "\n\n" + body.lstrip("\n").rstrip() + "\n",
                    encoding="utf-8")
    print(f"{'created' if created else 'updated'} {path}")
    return 0


# ---------------------------------------------------------------------- main

def cmd_show(args: argparse.Namespace) -> int:
    projects = load_projects()
    worktrees = scan_worktrees()
    link(projects, worktrees)
    pr_on = not args.no_pr
    if pr_on:
        targets = [w for p in projects for w in p.worktrees]
        if not args.json:
            targets += [w for w in worktrees if w.claimed_by is None and w.notes]
        attach_prs(targets)
    for p in projects:
        decide(p)
    if args.filter:
        needle = args.filter.lower()
        projects = [p for p in projects
                    if needle in p.slug.lower() or needle in p.body.lower()
                    or any(needle in (w.branch or "").lower() for w in p.worktrees)]
    orphan_notes = [w for w in worktrees if w.claimed_by is None and w.notes]
    if args.json:
        print(to_json(projects, orphan_notes))
    else:
        print(report(projects, orphan_notes, pr_on, args.all))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="where-are-we", description=__doc__)
    sub = ap.add_subparsers(dest="cmd")

    show = sub.add_parser("show", help="report every project in flight (default)")
    show.add_argument("filter", nargs="?", help="only projects matching this text")
    show.add_argument("--json", action="store_true")
    show.add_argument("--all", action="store_true", help="include projects marked done")
    show.add_argument("--no-pr", action="store_true", help="skip gh, much faster")
    show.set_defaults(func=cmd_show)

    up = sub.add_parser("update", help="write a status file (the only mutation)")
    up.add_argument("project")
    up.add_argument("--status", choices=KNOWN_STATUS)
    up.add_argument("--next", help="the single next action")
    up.add_argument("--note", help="append a timestamped line to the Log section")
    up.add_argument("--worktree", action="append", default=[])
    up.add_argument("--branch", action="append", default=[])
    up.add_argument("--pr", action="append", default=[])
    up.add_argument("--link", action="append", default=[])
    up.add_argument("--repo", action="append", default=[])
    up.set_defaults(func=cmd_update)

    # Bare `where-are-we` and `where-are-we <filter>` both mean show.
    if not argv or (argv[0] not in ("show", "update") and not argv[0].startswith("-")):
        argv = ["show", *argv]
    elif argv and argv[0].startswith("-"):
        argv = ["show", *argv]
    args = ap.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(130)
