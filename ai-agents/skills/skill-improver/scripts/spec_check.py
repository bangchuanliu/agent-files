#!/usr/bin/env python3
"""Spec conformance check for a skill directory. Deterministic checks only.

    python3 scripts/spec_check.py <skill-dir> [<skill-dir> ...]
    python3 scripts/spec_check.py --all <skills-root>

Covers the mechanically-detectable half of the agentskills.io v1 spec and the
community pitfall list: frontmatter shape, name/description rules, body size,
link resolution, reference depth, and script hygiene. Everything here has one
correct answer, so a reviewer should never spend attention on it.

Voice, density, over-abstraction and time-sensitivity are NOT checked here - they need
judgement and belong in the review pass.

Exit 0 = clean, 1 = findings, 2 = bad usage.
"""
import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")

NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
VALID_KINDS = ("leaf", "orchestrator")
VALID_AGENTS = {"claude", "copilot", "openai"}
SKIP_DISCOVERY_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "data", "assets", "dist",
    "build", "target", "__pycache__",
}
# A NOT-for clause names its neighbours either as "-> use x" or as "(x)".
# Both forms are in use; neither is more correct.
# The parenthesised form must look like a skill name - kebab-case with at least
# one hyphen - or "(the tokenized table)" reads as a route to a skill called "the".
NEIGHBOUR_RE = re.compile(r"(?:->|→)\s*use\s+([a-z0-9][a-z0-9-]*)"
                          r"|\(([a-z0-9]+(?:-[a-z0-9]+)+)\)")
RESERVED_NAMES = {"anthropic", "claude"}
DESCRIPTION_LIMIT = 1024          # agentskills.io v1
# agentskills.io v1 caps name at 64 chars. Copilot CLI does not appear to enforce
# it - over-length skills load - so this is a portability finding, not a blocker.
NAME_LIMIT = 64
BODY_LINE_LIMIT = 500             # ~5k tokens, the activation budget
TOC_LINE_THRESHOLD = 100          # reference files longer than this need a TOC
def strip_code(text):
    """Drop fenced blocks and inline code so literal examples are not parsed as links.

    Line-based on purpose. A regex over the whole document mispairs when a file
    has an odd number of fences, and the inline-code pass then spans line breaks
    and swallows real content.
    """
    out, fence = [], None
    for line in text.split("\n"):
        marker = line.lstrip()[:3]
        if marker in ("```", "~~~"):
            fence = None if fence == marker else (fence or marker)
            out.append("")
            continue
        out.append("" if fence else re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'(][^)]*)?\s*\)")


def findings_for(skill_dir, siblings=None, house=False):
    """Return a list of (severity, message) for one skill directory.

    siblings: set of installed skill names, for checking that a description's
    NOT-for clause routes somewhere real. None disables that check.
    house:    also check the aspirational 'Use when:' / 'NOT for:' format.
    """
    out = []
    skill_dir = os.path.realpath(skill_dir)
    folder = os.path.basename(skill_dir)
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        return [("P1", f"no SKILL.md in {skill_dir}")]

    raw = open(path, encoding="utf-8").read()

    # --- frontmatter ------------------------------------------------------
    if raw.startswith("\ufeff"):
        out.append(("P1", "file begins with a BOM; the skill will not load"))
    if not raw.startswith("---"):
        out.append(("P1", "frontmatter must start at line 1 with ---"))
    match = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
    if not match:
        out.append(("P1", "no parsable YAML frontmatter block"))
        return out
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return out + [("P1", f"frontmatter is not valid YAML: {exc}")]
    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        return out + [("P1", f"frontmatter must be a YAML mapping, got "
                             f"{type(meta).__name__}")]
    for field in ("name", "description"):
        if field in meta and not isinstance(meta[field], str):
            out.append(("P1", f"{field} must be a string, got "
                              f"{type(meta[field]).__name__}"))
    if "disable-model-invocation" in meta and not isinstance(meta["disable-model-invocation"], bool):
        out.append(("P1", "disable-model-invocation must be a boolean"))
    if "agents" in meta and not isinstance(meta["agents"], (str, list)):
        out.append(("P1", f"agents must be a comma-separated string or list, got "
                          f"{type(meta['agents']).__name__}"))
    if isinstance(meta.get("description"), str) and not meta["description"].strip():
        out.append(("P1", "description is blank"))

    name = str(meta.get("name", "") or "")
    description = str(meta.get("description", "") or "")
    user_invoked = meta.get("disable-model-invocation") is True

    # --- name -------------------------------------------------------------
    if not name:
        out.append(("P1", "frontmatter has no name"))
    else:
        if name != folder:
            out.append(("P1", f"name '{name}' does not match folder '{folder}'"))
        if not NAME_RE.fullmatch(name):
            out.append(("P1", f"name '{name}' must be lowercase letters, digits "
                              f"and single hyphens"))
        if len(name) > NAME_LIMIT:
            out.append(("P3", f"name is {len(name)} chars; agentskills.io v1 caps it at "
                              f"{NAME_LIMIT}. Copilot CLI loads it anyway - this matters only "
                              f"for strict validators and other agents"))
        if name.lower() in RESERVED_NAMES:
            out.append(("P1", f"name '{name}' is reserved"))

    # --- description ------------------------------------------------------
    if not description:
        out.append(("P1", "frontmatter has no description - model-invoked skills cannot trigger, and user-invoked skills need a human summary"))
    else:
        if len(description) > DESCRIPTION_LIMIT:
            out.append(("P1", f"description is {len(description)} chars, "
                              f"limit {DESCRIPTION_LIMIT}"))
        # The house convention ends every description with 'NOT for: X -> use Y',
        # so the ASCII routing arrow is allowed. Everything else angle-bracketed
        # breaks strict validators.
        scrubbed = (description + " " + name).replace("->", " ").replace("→", " ")
        for char in "<>":
            if char in scrubbed:
                context = re.search(rf".{{0,40}}{re.escape(char)}.{{0,40}}", description)
                out.append(("P1", f"'{char}' in name/description breaks strict validators"
                                  + (f" - ...{context.group(0)}..." if context else "")))
                break
        if re.match(r"\s*(I |I'll|We |We'll)", description):
            out.append(("P2", "description is first-person; use third-person"))
        if user_invoked and ("Use when:" in description or "NOT for:" in description):
            out.append(("P3", "user-invoked description should be a one-line human summary, not trigger routing"))

    # --- house conventions ------------------------------------------------
    kind = meta.get("kind")
    if kind is None:
        out.append(("P2", f"no kind: in frontmatter - expected one of {VALID_KINDS}"))
    elif kind not in VALID_KINDS:
        out.append(("P2", f"kind: '{kind}' is not one of {VALID_KINDS}"))

    # A description that routes to a neighbour should route somewhere real. This
    # is the one house check worth enforcing by default: a renamed sibling leaves
    # a pointer that reads perfectly and resolves to nothing.
    agents = meta.get("agents")
    if isinstance(agents, str):
        agent_names = [a for a in re.split(r"[,\s]+", agents.strip()) if a]
    elif isinstance(agents, list):
        agent_names = [str(a) for a in agents]
    else:
        agent_names = []
    for agent in agent_names:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", agent):
            out.append(("P2", f"agents entry '{agent}' contains characters "
                              "lib/links.sh supports() will not match cleanly"))
        elif agent.lower() not in VALID_AGENTS:
            out.append(("P3", f"agents entry '{agent}' is not one of the known "
                              f"adapters {sorted(VALID_AGENTS)}"))

    if "NOT for:" in description and siblings is not None:
        tail = description.split("NOT for:")[-1]
        for arrow_form, paren_form in NEIGHBOUR_RE.findall(tail):
            neighbour = arrow_form or paren_form
            # A hyphen-free token that is not an installed skill is ordinary prose
            # ("-> use the tokenized table"), not a dangling route.
            if neighbour and "-" not in neighbour and neighbour not in siblings:
                continue
            if neighbour and neighbour != folder and neighbour not in siblings:
                out.append(("P2", f"description routes to '{neighbour}', which is not an "
                                  f"installed skill - renamed, or a typo"))

    if house:
        if not user_invoked:
            if not description.strip().startswith("Use when"):
                out.append(("P3", "description does not start with 'Use when' (house convention)"))
            if "NOT for:" not in description:
                out.append(("P3", "description has no 'NOT for:' clause (house convention)"))

    # --- body -------------------------------------------------------------
    body = raw[match.end():]
    lines = len(body.splitlines())
    if lines > BODY_LINE_LIMIT:
        out.append(("P2", f"body is {lines} lines, over the {BODY_LINE_LIMIT}-line "
                          f"activation budget - move detail into references/"))
    for m in re.finditer(r"[\w.]+\\[\w.]+\.(?:py|sh|md|json|ya?ml|txt|csv|tsv)\b", body):
        out.append(("P2", f"backslash path '{m.group(0)}' - use forward slashes"))
        break

    # --- links and reference depth ---------------------------------------
    # Strip inline code first: a skill that documents markdown syntax contains
    # literal `[text](url)` examples that are not links.
    prose = strip_code(body)
    for target in LINK_RE.findall(prose):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if not os.path.exists(os.path.join(skill_dir, target.split("#")[0])):
            out.append(("P1", f"broken link: {target}"))

    ref_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(ref_dir):
        for entry in sorted(os.listdir(ref_dir)):
            ref_path = os.path.join(ref_dir, entry)
            if not entry.endswith(".md") or not os.path.isfile(ref_path):
                continue
            ref = open(ref_path, encoding="utf-8").read()
            ref_lines = len(ref.splitlines())
            if ref_lines > TOC_LINE_THRESHOLD and not re.search(
                    r"^#+ (Contents|Table of contents)", ref, re.I | re.M):
                out.append(("P3", f"references/{entry} is {ref_lines} lines with no "
                                  f"Contents section"))
            for target in LINK_RE.findall(strip_code(ref)):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                resolved = os.path.join(ref_dir, target.split("#")[0])
                if not os.path.exists(resolved):
                    out.append(("P1", f"references/{entry} has a broken link: {target}"))
                elif target.endswith(".md") and os.path.basename(target) not in body:
                    out.append(("P3", f"references/{entry} links on to {target}, which "
                                      f"SKILL.md does not link directly - keep references "
                                      f"one level deep"))

    # --- scripts ----------------------------------------------------------
    script_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(script_dir):
        # A script may be documented in SKILL.md or in a reference file; both count.
        documented = body
        if os.path.isdir(ref_dir):
            for entry in os.listdir(ref_dir):
                ref_file = os.path.join(ref_dir, entry)
                if os.path.isfile(ref_file):
                    documented += open(ref_file, encoding="utf-8", errors="ignore").read()
        for entry in sorted(os.listdir(script_dir)):
            full = os.path.join(script_dir, entry)
            if not os.path.isfile(full) or entry == "__init__.py":
                continue
            # Only files meant to be run need the executable bit; an imported
            # helper module is not a CLI and never will be.
            has_shebang = open(full, encoding="utf-8", errors="ignore").read(2) == "#!"
            # Three ways a script is used: run directly (./x.py - needs +x), run via
            # an interpreter (python3 x.py - does not), or imported. Only the first
            # needs the executable bit, so infer intent from how the docs invoke it.
            via_interpreter = re.search(
                rf"(?:python3?|bash|sh)\s+\S*{re.escape(entry)}\b", documented) is not None
            run_directly = (not via_interpreter) and re.search(
                rf"(?:^|[\s`(])(?:\./|~?/)\S*{re.escape(entry)}\b",
                documented, re.M) is not None
            invoked = via_interpreter or run_directly
            if run_directly and not os.access(full, os.X_OK):
                out.append(("P2", f"scripts/{entry} is invoked directly but is not "
                                  f"executable (chmod +x)"))
            elif has_shebang and not os.access(full, os.X_OK):
                out.append(("P3", f"scripts/{entry} has a shebang but is not executable "
                                  f"(chmod +x)"))
            if entry not in documented and (has_shebang or invoked):
                out.append(("P2", f"scripts/{entry} is runnable but documented nowhere - "
                                  f"dead weight, or an undocumented capability"))
    return out


def main():
    parser = argparse.ArgumentParser(description="Spec conformance check for skills.")
    parser.add_argument("paths", nargs="+", help="skill directories, or a parent with --all")
    parser.add_argument("--all", action="store_true",
                        help="treat each path as a parent directory of skills")
    parser.add_argument("--quiet", action="store_true", help="only print skills with findings")
    parser.add_argument("--house", action="store_true",
                        help="also check house description format (Use when / NOT for)")
    args = parser.parse_args()

    targets = []
    for path in args.paths:
        if args.all:
            try:
                entries = sorted(os.scandir(path), key=lambda e: e.name)
            except OSError as exc:
                print(f"Cannot scan {path}: {exc}", file=sys.stderr)
                return 2
            for entry in entries:
                if not entry.is_dir(follow_symlinks=False):
                    continue
                if entry.name.startswith(".") or entry.name in SKIP_DISCOVERY_DIRS:
                    continue
                if os.path.isfile(os.path.join(entry.path, "SKILL.md")):
                    targets.append(entry.path)
        else:
            targets.append(path)

    if not targets:
        print("No skills found. Check the path - an empty scan is a misconfiguration, "
              "not a clean result.", file=sys.stderr)
        return 2

    # Installed skill names, so a NOT-for clause can be checked for dangling routes.
    parents = {os.path.dirname(os.path.realpath(t)) for t in targets}
    siblings = set()
    for parent in parents:
        if os.path.isdir(parent):
            siblings |= {d for d in os.listdir(parent)
                         if os.path.isfile(os.path.join(parent, d, "SKILL.md"))}

    total = 0
    for target in targets:
        found = findings_for(target, siblings=siblings, house=args.house)
        total += len(found)
        if found:
            print(f"\n{os.path.basename(os.path.normpath(target))}")
            for severity, message in found:
                print(f"  {severity}  {message}")
        elif not args.quiet:
            print(f"\n{os.path.basename(os.path.normpath(target))}\n  clean")

    print(f"\n{len(targets)} skill(s), {total} finding(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
